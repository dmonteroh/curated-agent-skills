"""How a skill is used in real sessions, read from saved transcripts.

`usage scan` reads Claude Code project transcripts (`~/.claude/projects/
<project>/*.jsonl`) and Codex session files (`~/.codex/sessions/**/*.jsonl`,
or `codex exec --json` traces), finds the sessions where a skill loaded, and
records what followed: the request that led to it, files written or edited,
commands run, the skill's own scripts, and one generic signal, a matching file
edited after a matching command failed (for a testing skill: a test file
edited after a failing test run). The signal is a count to read, not a
verdict: fixing a real bug in a test also produces it.

Nothing here calls a model. Transcripts are the operator's data: the scan
writes only to the output directory it is given.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import common, trace

_EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
# Patch headers appear with real newlines in an apply_patch tool, and with
# literal "\n" escapes when the patch is a string inside an exec script.
_PATCH_FILE_RE = re.compile(r"\*\*\* (?:Add|Update|Delete) File: ([^\n\\\"]+)")
_CMD_FIELD_RE = re.compile(r'"cmd"\s*:\s*"((?:\\.|[^"\\])*)"')
# Codex exec output carries one JSON chunk per exec_command, as
# "exit_code":N, sometimes with escaped quotes. Older formats print a phrase.
_EXIT_RE = re.compile(r"(?:Exit code|exited with code|exit_code\\?\"?)\s*[:=]?\s*(-?\d+)", re.I)
# Chosen default: enough of the request to recognise the task, short enough
# that the notes file stays a set of excerpts.
EXCERPT_CHARS = 600


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") in ("text", "input_text"))
    return ""


def _loaded_name(raw: str, skill: str) -> bool:
    return raw == skill or raw.endswith(":" + skill)


def _reads_skill(command: str, skill: str) -> bool:
    for seg in trace._read_verb_segments(command):
        for _, name in trace._SKILL_MD_RE.findall(seg):
            if name == skill:
                return True
    return False


def _new_session(path: Path, vendor: str) -> dict:
    return {"path": str(path), "vendor": vendor, "cwd": None, "started": None, "loaded": False,
            "load_signal": None, "request": None, "requests_before_load": 0, "events": []}


def parse_claude(path: Path, skill: str) -> dict:
    """One Claude Code transcript as an ordered list of events after
    normalisation: user requests, skill loads, edits, and commands with their
    outcome."""
    s = _new_session(path, "claude")
    pending = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(e, dict):
            continue
        s["cwd"] = s["cwd"] or e.get("cwd")
        s["started"] = s["started"] or e.get("timestamp")
        message = e.get("message") if isinstance(e.get("message"), dict) else {}
        content = message.get("content")
        if e.get("type") == "user":
            if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in pending:
                        pending.pop(b["tool_use_id"])["failed"] = bool(b.get("is_error"))
                continue
            text = _text_of(content)
            command = re.search(r"<command-name>/?([^<]+)</command-name>", text)
            if command and _loaded_name(command.group(1).strip(), skill):
                s["events"].append({"kind": "load", "signal": "slash_command"})
            if text.strip() and not e.get("isMeta"):
                s["events"].append({"kind": "request", "text": text.strip()[:EXCERPT_CHARS]})
        elif e.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                name, inp = b.get("name"), b.get("input") or {}
                if name == "Skill" and _loaded_name(str(inp.get("skill") or ""), skill):
                    s["events"].append({"kind": "load", "signal": "skill_tool"})
                elif name == "Read" and re.search(rf"skills/{re.escape(skill)}/SKILL\.md$", str(inp.get("file_path") or "")):
                    s["events"].append({"kind": "load", "signal": "file_read"})
                elif name in _EDIT_TOOLS:
                    event = {"kind": "edit", "path": str(inp.get("file_path") or inp.get("notebook_path") or "")}
                    s["events"].append(event)
                    pending[b.get("id")] = event
                elif name == "Bash":
                    command = str(inp.get("command") or "")
                    if _reads_skill(command, skill):
                        s["events"].append({"kind": "load", "signal": "file_read"})
                    event = {"kind": "command", "command": command, "failed": None,
                             "script_runs": trace.script_runs_in(command)}
                    s["events"].append(event)
                    pending[b.get("id")] = event
    return s


def _codex_commands(payload: dict) -> list[str]:
    """Shell commands in one Codex response item, across the formats seen:
    function calls with a command list or a cmd string, local shell calls,
    and the exec custom tool whose input embeds exec_command({"cmd": ...})."""
    ptype = payload.get("type")
    if ptype == "local_shell_call":
        cmd = (payload.get("action") or {}).get("command")
        return [" ".join(cmd) if isinstance(cmd, list) else str(cmd or "")]
    if ptype == "function_call":
        try:
            args = json.loads(payload.get("arguments") or "{}")
        except json.JSONDecodeError:
            return []
        cmd = args.get("cmd", args.get("command"))
        if isinstance(cmd, list):
            return [" ".join(cmd)]
        return [str(cmd)] if cmd else []
    if ptype == "custom_tool_call" and payload.get("name") != "apply_patch":
        return [json.loads(f'"{m}"') for m in _CMD_FIELD_RE.findall(str(payload.get("input") or ""))]
    return []


def parse_codex(path: Path, skill: str) -> dict:
    """One Codex session file (rollout format) or `codex exec --json` trace."""
    s = _new_session(path, "codex")
    pending = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(e, dict):
            continue
        payload = e.get("payload") if isinstance(e.get("payload"), dict) else {}
        etype = e.get("type")
        if etype in ("session_meta", "turn_context"):
            s["cwd"] = s["cwd"] or payload.get("cwd")
            s["started"] = s["started"] or payload.get("timestamp") or e.get("timestamp")
        elif etype == "response_item":
            ptype = payload.get("type")
            if ptype == "message" and payload.get("role") == "user":
                text = _text_of(payload.get("content"))
                if text.strip() and not text.lstrip().startswith(("<environment_context>", "<user_instructions>")):
                    s["events"].append({"kind": "request", "text": text.strip()[:EXCERPT_CHARS]})
            elif ptype in ("custom_tool_call", "function_call", "local_shell_call"):
                raw = str(payload.get("input") or payload.get("arguments") or "")
                for command in _codex_commands(payload):
                    if _reads_skill(command, skill):
                        s["events"].append({"kind": "load", "signal": "command_read"})
                    event = {"kind": "command", "command": command, "failed": None,
                             "script_runs": trace.script_runs_in(command)}
                    s["events"].append(event)
                    pending.setdefault(payload.get("call_id"), []).append(event)
                for rel in _PATCH_FILE_RE.findall(raw):
                    s["events"].append({"kind": "edit", "path": rel.strip()})
            if ptype in ("function_call_output", "custom_tool_call_output") and payload.get("call_id") in pending:
                output = payload.get("output")
                text = output if isinstance(output, str) else json.dumps(output)
                # One exit code per command, in call order. A missing one stays unknown.
                codes = [int(c) for c in _EXIT_RE.findall(text)]
                commands = pending.pop(payload["call_id"])
                for event, code in zip(commands, codes):
                    event["failed"] = code != 0
        elif etype == "item.completed":  # codex exec --json
            item = e.get("item") or {}
            if item.get("type") == "command_execution":
                command = str(item.get("command") or "")
                if _reads_skill(command, skill):
                    s["events"].append({"kind": "load", "signal": "command_read"})
                code = item.get("exit_code")
                s["events"].append({"kind": "command", "command": command,
                                    "failed": None if code is None else code != 0,
                                    "script_runs": trace.script_runs_in(command)})
            elif item.get("type") == "file_change":
                for change in item.get("changes") or []:
                    s["events"].append({"kind": "edit", "path": str(change.get("path") or "")})
    return s


def summarize_session(s: dict, skill: str, path_re: re.Pattern | None, command_re: re.Pattern | None) -> dict:
    """Reduce a parsed session to what happened from the first load on."""
    events = s.pop("events")
    first = next((i for i, ev in enumerate(events) if ev["kind"] == "load"), None)
    s["loaded"] = first is not None
    if first is None:
        return s
    s["load_signal"] = events[first]["signal"]
    requests = [ev for ev in events[:first] if ev["kind"] == "request"]
    s["requests_before_load"] = len(requests)
    s["request"] = requests[-1]["text"] if requests else None
    after = events[first:]
    edits = [ev["path"] for ev in after if ev["kind"] == "edit"]
    commands = [ev for ev in after if ev["kind"] == "command"]
    prefix = f"skills/{skill}/scripts/"
    s.update(
        files_edited=sorted(set(edits)),
        edits=len(edits),
        commands=len(commands),
        failed_commands=sum(ev["failed"] is True for ev in commands),
        # Codex exec scripts often print output without an exit code, so an
        # outcome can be unknown. Failures count only among known outcomes.
        commands_with_outcome=sum(ev["failed"] is not None for ev in commands),
        skill_script_runs=sum(any(r.startswith(prefix) for r in ev["script_runs"]) for ev in commands),
    )
    if path_re is not None:
        s["matched_files_edited"] = sorted({p for p in edits if path_re.search(p)})
    if command_re is not None:
        s["matched_commands"] = sum(bool(command_re.search(ev["command"])) for ev in commands)
        s["matched_commands_failed"] = sum(bool(command_re.search(ev["command"])) and ev["failed"] is True
                                           for ev in commands)
    if path_re is not None and command_re is not None:
        count, failed_seen = 0, False
        for ev in after:
            if ev["kind"] == "command" and command_re.search(ev["command"]):
                failed_seen = ev["failed"] is True
            elif ev["kind"] == "edit" and failed_seen and path_re.search(ev["path"]):
                count += 1
                failed_seen = False
        s["matched_edit_after_failed_command"] = count
    return s


def scan(skill: str, claude_dirs: list[Path], codex_dirs: list[Path], *,
         path_pattern: str | None = None, command_pattern: str | None = None) -> list[dict]:
    path_re = re.compile(path_pattern) if path_pattern else None
    command_re = re.compile(command_pattern) if command_pattern else None
    sessions = []
    for vendor, dirs, parse in (("claude", claude_dirs, parse_claude), ("codex", codex_dirs, parse_codex)):
        for root in dirs:
            files = [root] if root.is_file() else sorted(root.rglob("*.jsonl"))
            for path in files:
                try:
                    parsed = parse(path, skill)
                except OSError as exc:
                    sessions.append({"path": str(path), "vendor": vendor, "error": str(exc), "loaded": False})
                    continue
                sessions.append(summarize_session(parsed, skill, path_re, command_re))
    return sessions


def write_report(skill: str, sessions: list[dict], out: Path, patterns: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    loaded = [s for s in sessions if s.get("loaded")]
    common.write_jsonl(out / "sessions.jsonl", loaded)
    notes = [f"- {s['request'].replace(chr(10), ' ')}" for s in loaded if s.get("request")]
    (out / "usage-notes.txt").write_text("\n".join(notes) + ("\n" if notes else ""), encoding="utf-8")
    by_vendor = {}
    for s in sessions:
        v = by_vendor.setdefault(s["vendor"], {"scanned": 0, "loaded": 0})
        v["scanned"] += 1
        v["loaded"] += bool(s.get("loaded"))
    total = lambda key: sum(s.get(key, 0) or 0 for s in loaded)
    lines = [f"# Usage: {skill}", "",
             "| Vendor | Sessions scanned | Sessions where the skill loaded |", "| --- | --- | --- |"]
    lines += [f"| {v} | {c['scanned']} | {c['loaded']} |" for v, c in sorted(by_vendor.items())]
    lines += ["", f"Path pattern: `{patterns.get('path') or '-'}`. Command pattern: `{patterns.get('command') or '-'}`.", "",
              "| Session | Vendor | Project | Signal | Edits | Commands | Failed / outcome known | Skill script runs | Matched edits after a failed matched command |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in loaded:
        lines.append(f"| {Path(s['path']).stem[:24]} | {s['vendor']} | {s.get('cwd') or '-'} | {s['load_signal']} | "
                     f"{s['edits']} | {s['commands']} | {s['failed_commands']} / {s['commands_with_outcome']} | {s['skill_script_runs']} | "
                     f"{s.get('matched_edit_after_failed_command', '-')} |")
    lines += ["", f"Totals over loaded sessions: {total('edits')} edits, {total('commands')} commands, "
              f"{total('failed_commands')} failed of {total('commands_with_outcome')} with a known outcome, "
              f"{total('skill_script_runs')} skill script runs, "
              f"{total('matched_edit_after_failed_command')} matched edits after a failed matched command.", "",
              "A matched edit after a failed matched command is a lead to read in the transcript, not a verdict.",
              "`usage-notes.txt` holds the request before each load, for `card tasks --usage-notes`. Review it before "
              "sharing: it is transcript text."]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _cmd_scan(args) -> int:
    try:
        if not args.claude and not args.codex:
            raise ValueError("Give at least one --claude or --codex transcript directory.")
        for raw in (args.path_pattern, args.command_pattern):
            if raw:
                re.compile(raw)
        sessions = scan(args.skill, [Path(p) for p in args.claude], [Path(p) for p in args.codex],
                        path_pattern=args.path_pattern, command_pattern=args.command_pattern)
        out = args.out or (common.RUNS_DIR / common.run_id(f"usage-{args.skill}"))
        write_report(args.skill, sessions, out, {"path": args.path_pattern, "command": args.command_pattern})
    except (ValueError, OSError, re.error) as exc:
        print(f"usage scan: {exc}", file=sys.stderr)
        return 2
    print((out / "summary.md").read_text())
    print(out)
    return 0


def add_subparser(subparsers) -> None:
    parser = subparsers.add_parser("usage", help="How a skill is used in saved session transcripts. Free.")
    sub = parser.add_subparsers(dest="subcommand", required=True)
    cmd = sub.add_parser("scan", help="Find sessions where a skill loaded and what followed.")
    cmd.add_argument("--skill", required=True)
    cmd.add_argument("--claude", action="append", default=[], help="a Claude projects directory or transcript (repeatable)")
    cmd.add_argument("--codex", action="append", default=[], help="a Codex sessions directory or file (repeatable)")
    cmd.add_argument("--path-pattern", help="regex for files of interest, for example 'test'")
    cmd.add_argument("--command-pattern", help="regex for commands of interest, for example 'pytest|unittest|jest'")
    cmd.add_argument("--out", type=Path, help="report directory (default under SKILL_EVAL_RUNS_DIR)")
    cmd.set_defaults(func=_cmd_scan)
