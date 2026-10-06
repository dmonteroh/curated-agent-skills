"""Parse vendor CLI traces into one normalised `common.TraceRecord` shape.

Claude Code exposes a `Skill` tool, so a traced claude run shows activation as
a `tool_use` block (`name == "Skill"`, `input == {"skill": "<name>"}`, verified
against a live `claude --print --output-format stream-json` capture: see
`fixtures/trace/claude-activate.jsonl`). Codex has no such tool: it discovers
a skill and reads its `SKILL.md` with a shell command, so activation there
shows up as an `item.completed` `command_execution` naming that path (see
`fixtures/trace/codex-activate.jsonl`). The signal differs in kind between
vendors; the record does not.

Three defects in the prior harness (tmp/writing-style-skill/measure/lib/trace.py)
this module must not repeat:
  1. It hardcoded one skill name. Here, every skill name under a `skills/`
     path is attributed, and a name outside `known_skills` is reported as
     `builtin:<name>` rather than dropped or misattributed.
  2. It never stripped a plugin namespace prefix (`plugin:name`); a
     namespaced Skill call would show as an unmatched raw string. This
     module does NOT repeat that by stripping the prefix either: a stripped
     `anthropic-skills:foo` would silently credit an org built-in to a
     library skill named `foo` (R1 finding C3, confirmed live). A namespaced
     name is matched against `known_skills` only in full; when it is not
     literally there, it is reported as `builtin:<full name>`, prefix and
     all.
  3. It treated any trace with output as clean, so a short auth-error message
     scored as a normal (non-activating) run. Here, a trace with no
     completion event, or whose final text matches an auth/quota/session
     signature, is marked `ok=False` with the matched text as `error`. The
     regex only runs when there is independent reason to look -- an explicit
     error flag/event, or a short, tool-free reply -- so a legitimate answer
     that merely *mentions* "401 Unauthorized" is not misclassified (R1
     finding I5).

Costs are NOT comparable across vendors. Claude reports dollars
(`TraceRecord.cost_usd`), codex reports tokens (`TraceRecord.tokens`). Neither
is converted into the other.
"""
from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import Iterable

from .common import TraceRecord

# A skill file read, in either a Claude tool_use input blob or a codex shell
# command line: "...skills/<name>/SKILL.md..." or the codex built-in path
# "...skills/.system/<name>/SKILL.md...". Works on absolute or relative
# paths, and inside a quoted shell command, because it only anchors on the
# `skills/[.system/]<name>/SKILL.md` tail. The name class excludes shell glob
# characters (`*?[]{}`) on purpose: `grep -l x skills/*/SKILL.md` must not be
# read as a skill literally named `*` (R1 finding I7, confirmed live).
_SKILL_MD_RE = re.compile(r"skills/(\.system/)?([A-Za-z0-9_][A-Za-z0-9_.-]*)/SKILL\.md")

# Codex has no `Skill` tool: it reads SKILL.md with a shell command, so only a
# command that actually reads file *content* counts as activation. `ls` (or
# any other non-reading command) merely naming the path in an argument does
# not (R1 finding I7: "`ls skills/foo/SKILL.md skills/bar/SKILL.md` activates
# both" was the bug). Chosen list, not measured: the read-like commands named
# in the finding, plus `awk` for its `print` idiom.
_READ_VERBS = ("cat", "sed", "head", "tail", "less", "nl", "awk")

# R2 finding: matching a read verb anywhere in the command string (the old
# `_READ_VERB_RE.search(cmd)`) let a pipeline like `grep -l x skills/foo/
# SKILL.md | head` count as a read, because `head` matched even though it
# never sees the path -- `grep` (not a read verb) is what actually took the
# path as its argument. The fix requires the read verb to be the command a
# pipeline SEGMENT starts with, and only that segment's own arguments are
# scanned for a SKILL.md path -- `_read_verb_segments` below.
#
# codex wraps its shell commands as `/bin/bash -lc "<script>"` (confirmed in
# fixtures/trace/codex-activate.jsonl); `_unwrap_shell_c` peels that one
# layer off so the segmentation below runs against the actual script rather
# than treating `/bin/bash` itself as the command. This is a heuristic, not a
# shell parser: nested `bash -c` inside the script, or a script built through
# string concatenation/eval, is not unwrapped further.
_SHELL_OP_RE = re.compile(r"\|\||&&|;|\|")


def _unwrap_shell_c(cmd: str) -> str:
    """Peel one `bash -c`/`sh -lc`/... wrapper off, returning the inner script.

    Returns `cmd` unchanged when it is not shaped like `<shell> -<flags ending
    in c> "<script>"`, or when it cannot be tokenised at all (unbalanced
    quoting): best-effort, never raises.
    """
    try:
        argv = shlex.split(cmd)
    except ValueError:
        return cmd
    if len(argv) < 3:
        return cmd
    exe = argv[0].rsplit("/", 1)[-1]
    if exe not in ("bash", "sh", "zsh", "dash"):
        return cmd
    for tok in argv[1:-1]:
        if tok.startswith("-") and tok.endswith("c"):
            return argv[-1]
    return cmd


def _frontmatter_name_in(output: str, name: str) -> bool:
    """True when `output` holds a SKILL.md frontmatter line naming `name`."""
    return re.search(rf"(?m)^name:\s*[\"']?{re.escape(name)}[\"']?\s*$", output) is not None


def _read_verb_segments(cmd: str) -> list[str]:
    """Pipeline/`&&`/`;`-separated segments of `cmd` whose OWN first token is
    a read verb (after unwrapping one `bash -c` layer). Only these segments'
    text is scanned for a SKILL.md path, so a read verb elsewhere in the same
    command line that did not take the path as its argument cannot credit an
    activation."""
    script = _unwrap_shell_c(cmd)
    segments: list[str] = []
    for raw in _SHELL_OP_RE.split(script):
        raw = raw.strip()
        if not raw:
            continue
        try:
            tokens = shlex.split(raw)
        except ValueError:
            tokens = raw.split()
        if not tokens:
            continue
        verb = tokens[0].rsplit("/", 1)[-1]
        if verb in _READ_VERBS:
            segments.append(raw)
    return segments

# Chosen, not measured: enough vendor-observed phrasings (see
# fixtures/trace/*-auth-error.synthetic.jsonl, modelled on real CLI wording)
# to catch the failure modes DESIGN.md calls out — auth, quota, and an
# expired/failed session — without matching ordinary task text.
_AUTH_ERROR_RE = re.compile(
    r"(?i)\b(not logged in|please run /?login|please run [`']?codex login[`']?|"
    r"invalid api key|authentication[_ ]error|unauthorized|401 unauthorized|"
    r"rate limit|rate_limit_error|quota exceeded|insufficient_quota|"
    r"exceeded your (?:current )?quota|session (?:has )?expired)\b"
)

# Chosen default (R1 finding I5): the auth/quota regex is scoped to short,
# tool-free replies, since that is the shape a real auth failure takes (see
# the auth-error fixtures). Without this scope, a legitimate long answer that
# merely *mentions* "401 Unauthorized" was misclassified as a failed run.
_AUTH_REGEX_MAX_TEXT_BYTES = 300


def _resolve_skill_name(raw: str, known: set[str]) -> str:
    """Match a name against known_skills in full; never strip a namespace.

    A `plugin:name` (or `anthropic-skills:name`) prefix is part of the
    identity of what activated. Stripping it, as an earlier version of this
    function did, credited an organisation-provisioned skill
    (`anthropic-skills:writing-style`) to a library skill of the bare name
    `writing-style` -- confirmed live (R1 finding C3). Anything not literally
    in `known_skills`, prefix and all, is reported as `builtin:<full name>`.
    """
    name = (raw or "").strip()
    if name in known:
        return name
    return f"builtin:{name}" if name else "builtin:unknown"


def _activate(rec: TraceRecord, name: str, signal: str) -> None:
    if name not in rec.activated:
        rec.activated.append(name)
    # First signal wins: a skill can be both read and Skill-tool-invoked in
    # one run, and the first is the more informative one to keep.
    rec.activation_signals.setdefault(name, signal)


def _mark_auth_failure(rec: TraceRecord, *, is_error_flag: bool = False,
                        had_error_event: bool = False) -> None:
    """Never score a failed arm as clean: check the final text for an
    auth/quota/session signature (the old harness scored a 73-byte auth
    error as clean output) -- but only when there is independent reason to
    look, so a legitimate answer that happens to mention "401 Unauthorized"
    is not misclassified (R1 finding I5). The regex runs when the vendor
    already flagged an error (`is_error_flag`, `had_error_event`), or when
    the reply is short and used no tools -- the shape a real auth failure
    takes, and the shape the old harness's 73-byte example had.
    """
    if not rec.ok:
        return
    text = rec.text or ""
    short_and_tool_free = (
        len(text.encode("utf-8")) < _AUTH_REGEX_MAX_TEXT_BYTES and rec.tool_calls == 0
    )
    if not (is_error_flag or had_error_event or short_and_tool_free):
        return
    m = _AUTH_ERROR_RE.search(text)
    if m:
        rec.ok = False
        rec.error = text.strip()[:300] if text else m.group(0)


def _iter_events(path: Path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except ValueError:
            continue


def _skill_label(is_system: str | None, fname: str, known: set[str]) -> str:
    """A `.system/`-segmented path is always a vendor built-in (R1 I7/minor:
    codex seeds `skills/.system/<name>/SKILL.md`, which is never a library
    skill), reported as `builtin:<name>` without consulting `known_skills`.
    Otherwise resolve normally (see `_resolve_skill_name`)."""
    if is_system:
        return f"builtin:{fname}"
    return _resolve_skill_name(fname, known)


def _parse_claude(events, known: set[str]) -> TraceRecord:
    rec = TraceRecord(vendor="claude")
    result_seen = False
    is_error_flag = False
    text_blocks: list[str] = []
    rejected = set()
    for ev in events:
        if ev.get("type") != "user":
            continue
        content = (ev.get("message") or {}).get("content") or []
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            call_id = block.get("tool_use_id")
            if block.get("type") == "tool_result" and block.get("is_error") is True and call_id:
                rejected.add(call_id)
    for ev in events:
        etype = ev.get("type")
        if etype == "system" and ev.get("subtype") == "init":
            skills = ev.get("skills")
            if isinstance(skills, list):
                rec.visible_skills = list(skills)
            # R3 finding I1 (blocker): `visible_tools` was declared on
            # TraceRecord (DESIGN.md sec 3: "Tools the agent could see at
            # start-up") but never actually parsed, so `activation.py`'s
            # tools-mismatch contamination check always compared against
            # `None`. The init event's `tools` list (see
            # fixtures/trace/claude-activate.jsonl) is exactly that signal.
            tools = ev.get("tools")
            if isinstance(tools, list):
                rec.visible_tools = list(tools)
        elif etype == "assistant":
            for block in (ev.get("message") or {}).get("content") or []:
                btype = block.get("type") or ""
                if btype == "tool_use" or btype.endswith("tool_use"):
                    # R2 finding (Critical): with `--json-schema`, claude
                    # answers through a `StructuredOutput` tool_use block
                    # (see fixtures/trace/claude-structured-output.jsonl,
                    # captured live from `complete(..., json_schema=...)`).
                    # It is how the CLI returns structured output, not a
                    # tool the agent chose to use, so it must not inflate
                    # `tool_calls` -- counting it made every judge/generator
                    # call that used a json_schema look like it had used a
                    # tool (`record.tool_calls == 0` is the T-B gate both
                    # check), voiding every verdict in live runs.
                    if btype == "tool_use" and block.get("name") == "StructuredOutput":
                        continue
                    # Count every other tool-use-shaped block (R1 finding I6:
                    # a `server_tool_use` block was undercounted before), but
                    # only the plain `tool_use` blocks carry a `name`/`input`
                    # shape this module knows how to inspect for activation.
                    rec.tool_calls += 1
                    if btype != "tool_use" or block.get("id") in rejected:
                        continue
                    name = block.get("name")
                    inp = block.get("input") or {}
                    if name == "Skill":
                        raw = inp.get("skill") or inp.get("name") or ""
                        _activate(rec, _resolve_skill_name(str(raw), known), "skill_tool")
                    elif name == "Read":
                        blob = json.dumps(inp)
                        for is_system, fname in _SKILL_MD_RE.findall(blob):
                            path = f"skills/{'.system/' if is_system else ''}{fname}/SKILL.md"
                            rec.files_read.append(path)
                            _activate(rec, _skill_label(is_system, fname, known), "file_read")
                    elif name == "Bash":
                        # R2 finding (Minor): a claude `Bash ls .../SKILL.md`
                        # used to count as a read regardless of verb, while
                        # codex already required a read verb for the same
                        # shape of signal. Apply the identical
                        # `_read_verb_segments` rule here.
                        cmd = str(inp.get("command") or "")
                        for seg in _read_verb_segments(cmd):
                            for is_system, fname in _SKILL_MD_RE.findall(seg):
                                path = f"skills/{'.system/' if is_system else ''}{fname}/SKILL.md"
                                rec.files_read.append(path)
                                _activate(rec, _skill_label(is_system, fname, known), "file_read")
                elif btype == "text":
                    text_blocks.append(block.get("text", ""))
        elif etype == "result":
            result_seen = True
            structured = ev.get("structured_output")
            if structured is not None:
                # R2 finding (Critical): with `--json-schema`, the final
                # answer lives in `structured_output`, not `result` (though
                # in practice `result` already carries the same JSON text
                # here -- see the fixture). Serialise it explicitly so the
                # contract does not depend on that redundancy holding.
                rec.text = json.dumps(structured, sort_keys=True, ensure_ascii=False)
            else:
                rec.text = ev.get("result") or "".join(text_blocks)
            if ev.get("total_cost_usd") is not None:
                rec.cost_usd = ev["total_cost_usd"]
            if ev.get("is_error"):
                rec.ok = False
                is_error_flag = True
                rec.error = rec.text or "result event reported is_error"
    if not result_seen:
        rec.ok = False
        rec.error = rec.error or "no result event in trace"
        rec.text = rec.text or "".join(text_blocks)
    _mark_auth_failure(rec, is_error_flag=is_error_flag)
    return rec


def _parse_codex(events, known: set[str]) -> TraceRecord:
    rec = TraceRecord(vendor="codex")
    messages: list[str] = []
    seen_ids: set = set()
    turn_completed = False
    had_error_event = False
    for ev in events:
        etype = ev.get("type")
        item = ev.get("item") if isinstance(ev.get("item"), dict) else {}
        itype = item.get("type")
        if etype == "item.completed":
            # Count every completed item that is not the agent's own message
            # or its reasoning trace (R1 finding I6): a `command_execution`
            # is a tool call regardless of what it read, and so is anything
            # else this vendor emits here.
            if itype not in ("agent_message", "reasoning"):
                cid = item.get("id")
                if cid is None or cid not in seen_ids:
                    if cid is not None:
                        seen_ids.add(cid)
                    rec.tool_calls += 1
            if itype == "command_execution":
                cmd = item.get("command") or ""
                # Only a completed, successful, read-like command counts as
                # activation (R1 finding I7): a failed command never read
                # anything, and a non-reading command such as `ls` merely
                # naming the path is not a read either. R2 finding (Minor):
                # the path must be an argument of the SAME pipeline segment
                # as the read verb (`_read_verb_segments`), not merely
                # present anywhere in the command line.
                #
                # A chained command (`sed … SKILL.md && sed missing.md`) takes
                # the exit code of the last segment that ran, so a later
                # segment's failure hides a read that succeeded (measured: both
                # codex positive-control calls of a 2026-10-05 pr-description
                # selftest). A non-zero command still counts when its output
                # carries the file's own `name:` frontmatter line: the content
                # reached the agent.
                succeeded = item.get("status") == "completed" and item.get("exit_code") == 0
                output = item.get("aggregated_output") or ""
                for seg in _read_verb_segments(cmd):
                    for is_system, fname in _SKILL_MD_RE.findall(seg):
                        if not (succeeded or _frontmatter_name_in(output, fname)):
                            continue
                        path = f"skills/{'.system/' if is_system else ''}{fname}/SKILL.md"
                        rec.files_read.append(path)
                        _activate(rec, _skill_label(is_system, fname, known), "command_read")
            elif itype == "agent_message":
                messages.append(item.get("text") or "")
        elif etype == "turn.completed":
            turn_completed = True
            u = ev.get("usage") or {}
            rec.tokens = {
                "input": u.get("input_tokens"),
                "cached_input": u.get("cached_input_tokens"),
                "output": u.get("output_tokens"),
                "reasoning": u.get("reasoning_output_tokens"),
            }
        elif etype in ("turn.failed", "error"):
            rec.ok = False
            had_error_event = True
            err = ev.get("error") or ev.get("message") or ev
            rec.error = err if isinstance(err, str) else json.dumps(err)
    rec.text = messages[-1] if messages else ""
    # A completion requires turn.completed, not merely an agent_message (R1
    # finding I4): [turn.started, agent_message] with no turn.completed was
    # verified to score `ok=True` before this fix.
    if not turn_completed:
        rec.ok = False
        rec.error = rec.error or "no turn.completed event in trace"
    _mark_auth_failure(rec, had_error_event=had_error_event)
    return rec


# ---------------------------------------------------------------------------
# outside_reads (R2 finding, Important): a shell-capable arm can still read
# an absolute path outside its own home and cwd, since this container gives
# no OS sandbox (DESIGN.md T-A). `parse_trace(..., roots=...)` records every
# such path it can find in the trace, so a run that referenced the
# repository or the real home can be flagged as contaminated.
# ---------------------------------------------------------------------------

# Read-only system prefixes a shell-capable arm can always see regardless of
# isolation (base OS image, not operator or repository state), so a
# reference to one of these is not evidence of contamination. Small and
# labelled on purpose: this is an allowlist of exactly what was chosen to be
# uninteresting, not a general "looks like a system path" heuristic.
_OUTSIDE_READ_ALLOWLIST_EXACT = frozenset({
    "/dev/null",       # every process's discard sink
    "/etc/os-release", # OS identification, read by countless CLI tools
    "/tmp",            # the bare directory itself, not its contents
})
_OUTSIDE_READ_ALLOWLIST_PREFIXES = ("/bin/", "/usr/")  # base OS binaries/data


def _is_allowlisted_system_path(path: str) -> bool:
    if path in _OUTSIDE_READ_ALLOWLIST_EXACT:
        return True
    return any(path.startswith(p) for p in _OUTSIDE_READ_ALLOWLIST_PREFIXES)


def _expand_home(token: str, home: str | None) -> str:
    """Expand a leading `~` against the recorded HOME, when known.

    `roots` is documented (DESIGN.md sec 3) as "the arm's home and cwd", so
    by convention the first root a caller passes is treated as HOME for this
    expansion. Only the bare `~` and `~/...` forms are handled; `~otheruser`
    is left as-is either way, since this module has no way to resolve it.
    """
    if home and token == "~":
        return home
    if home and token.startswith("~/"):
        return home.rstrip("/") + token[1:]
    return token


def _path_tokens(value) -> list[str]:
    """Absolute or `~`-prefixed tokens found in a tool-input value.

    Works for a bare path string (`file_path`, `path`, `pattern`) and for a
    full shell command line (`command`) alike: both tokenise the same way,
    and a bare path simply tokenises to itself. Kept for callers that only
    want the literal absolute/`~` tokens (no relative resolution, no `bash
    -c` unwrapping); `_command_path_candidates` and `_field_path_candidates`
    below are what the outside-reads collectors actually use.
    """
    if not isinstance(value, str) or not value:
        return []
    try:
        tokens = shlex.split(value)
    except ValueError:
        tokens = value.split()
    return [t for t in tokens if t.startswith("/") or t.startswith("~")]


# R3 finding I6: a token this module treats as possibly a relative path
# argument -- not already absolute/`~`-prefixed, and either containing a `/`
# or starting with `.`. Deliberately narrow: a bare word like `notes` or
# `status` is not flagged (too much noise, and no plausible traversal
# reading), but `../CLAUDE.md`, `./x`, and `src/CLAUDE.md` are.
def _looks_like_relative_path(token: str) -> bool:
    return not token.startswith("/") and not token.startswith("~") and (
        "/" in token or token.startswith(".")
    )


def _safe_resolve(path: Path) -> Path:
    try:
        return path.resolve()
    except (OSError, RuntimeError):
        return path


def _resolve_against(token: str, base: Path) -> str:
    return str(_safe_resolve(base / token))


# A heredoc whose body only becomes a file (`cat > f <<EOF`, `cat >> f <<EOF`,
# `tee f <<EOF`): the body is file content, not commands or reads.
_FILE_HEREDOC_RE = re.compile(
    r"^[^\n]*\b(?:cat\s*>>?\s*\S+|tee(?:\s+-a)?\s+\S+)[^\n]*<<-?\s*(['\"]?)(\w+)\1[^\n]*$", re.M)


def _strip_file_heredocs(script: str) -> str:
    """Drop the bodies of heredocs that only write a file.

    Measured 2026-10-05: an arm writing Terraform with `cat > envs/dev/main.tf
    <<'E'` put `source = "../../modules/vcn"` in the body, which resolved to
    a path two levels above its cwd and voided the call as contamination.
    A heredoc fed to an interpreter (`python3 - <<EOF`, `bash <<EOF`) keeps
    its body, because that body can read files."""
    out, pos = [], 0
    for m in _FILE_HEREDOC_RE.finditer(script):
        if m.start() < pos:
            continue
        end_tag = re.compile(rf"^\s*{re.escape(m.group(2))}\s*$", re.M)
        close = end_tag.search(script, m.end())
        out.append(script[pos:m.end()])
        pos = close.end() if close else len(script)
    out.append(script[pos:])
    return "".join(out)


def _command_path_candidates(cmd: str, cwd_root: Path | None) -> list[str]:
    """Absolute, `~`-prefixed, and resolved-relative path tokens in a shell
    command line (R3 findings C1, I6).

    C1: peels one `bash -lc`/`sh -c`/... wrapper (`_unwrap_shell_c`) and
    splits the inner script on the shell-operator regex (`_SHELL_OP_RE`) so
    BOTH sides of a `;`/`&&`/`||`/`|` are scanned -- the old
    `shlex.split(cmd)` over the whole wrapped string treated `/bin/bash`,
    `-lc`, and the entire quoted script as one opaque argv, so a wrapped
    codex command such as `/bin/bash -lc "cat /workspace/CLAUDE.md; cat
    ~/.claude/.credentials.json"` never surfaced either inner `cat` target
    (confirmed: it produced `outside_reads == []`).

    I6: a relative path-like token (`_looks_like_relative_path`) is resolved
    against `cwd_root` -- or, once an earlier segment of this SAME command
    line matched `cd <dir>`, against that directory instead, so `cd
    ../../../../workspace && cat CLAUDE.md` is read as escaping through the
    `cd` target relative to the arm's cwd. This is a best-effort heuristic,
    not a shell interpreter, and it has real limits worth naming: it does
    not track `cd` across separate tool calls (each command line starts back
    at `cwd_root`); `cd ~...` gives up tracking rather than guessing HOME;
    `pushd`/`popd`, subshells, and `cd -` are not understood at all; and a
    bare relative token with neither `/` nor a leading `.` (a plain filename
    argument, like the `CLAUDE.md` in the example above) is never resolved
    on its own -- only the path-like tokens are, which is enough to catch
    the `cd` target itself doing the escaping.
    """
    script = _strip_file_heredocs(_unwrap_shell_c(cmd))
    tokens: list[str] = []
    current_dir = cwd_root
    for raw in _SHELL_OP_RE.split(script):
        raw = raw.strip()
        if not raw:
            continue
        try:
            seg_tokens = shlex.split(raw)
        except ValueError:
            seg_tokens = raw.split()
        if not seg_tokens:
            continue
        for t in seg_tokens:
            if t.startswith("/") or t.startswith("~"):
                tokens.append(t)
            elif current_dir is not None and _looks_like_relative_path(t):
                tokens.append(_resolve_against(t, current_dir))
        if seg_tokens[0] == "cd" and len(seg_tokens) > 1:
            dest = seg_tokens[1]
            if dest.startswith("/"):
                current_dir = _safe_resolve(Path(dest))
            elif dest.startswith("~"):
                current_dir = None  # give up tracking rather than guess HOME
            elif current_dir is not None:
                current_dir = _safe_resolve(current_dir / dest)
    return tokens


def _field_path_candidates(value, cwd_root: Path | None) -> list[str]:
    """Absolute, `~`-prefixed, and resolved-relative path tokens in a bare
    path-shaped tool-input field (`file_path`, `path`, `pattern`). Unlike
    `_command_path_candidates`, this never unwraps a shell wrapper and never
    tracks `cd` -- a bare field is not a command line."""
    if not isinstance(value, str) or not value:
        return []
    try:
        tokens = shlex.split(value)
    except ValueError:
        tokens = value.split()
    out: list[str] = []
    for t in tokens:
        if t.startswith("/") or t.startswith("~"):
            out.append(t)
        elif cwd_root is not None and _looks_like_relative_path(t):
            out.append(_resolve_against(t, cwd_root))
    return out


def _is_under_any_root(path_str: str, roots: list[Path]) -> bool:
    try:
        resolved = Path(path_str).resolve()
    except (OSError, RuntimeError):
        resolved = Path(path_str)
    for root in roots:
        try:
            resolved.relative_to(root.resolve())
            return True
        except (ValueError, OSError):
            continue
    return False


def _record_outside_reads(rec: TraceRecord, candidates: Iterable[str], roots: list[Path]) -> None:
    home = str(roots[0]) if roots else None
    for raw in candidates:
        token = _expand_home(raw, home)
        if _is_allowlisted_system_path(token):
            continue
        if _is_under_any_root(token, roots):
            continue
        if token not in rec.outside_reads:
            rec.outside_reads.append(token)


_CLAUDE_PATH_INPUT_KEYS = ("file_path", "path", "pattern", "command")


def _collect_claude_outside_reads(events, roots: list[Path]) -> list[str]:
    rec = TraceRecord(vendor="claude")  # scratch record, only .outside_reads used
    # roots is documented (DESIGN.md sec 3 / `_expand_home`) as home-then-cwd:
    # roots[1], when present, is the arm's cwd -- the base a relative token
    # resolves against (R3 finding I6).
    cwd_root = roots[1] if len(roots) > 1 else None
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for block in (ev.get("message") or {}).get("content") or []:
            if block.get("type") != "tool_use":
                continue
            inp = block.get("input") or {}
            candidates: list[str] = []
            for key in _CLAUDE_PATH_INPUT_KEYS:
                value = inp.get(key)
                if key == "command":
                    candidates.extend(_command_path_candidates(str(value or ""), cwd_root))
                else:
                    candidates.extend(_field_path_candidates(value, cwd_root))
            _record_outside_reads(rec, candidates, roots)
    return rec.outside_reads


def _collect_codex_outside_reads(events, roots: list[Path]) -> list[str]:
    rec = TraceRecord(vendor="codex")
    cwd_root = roots[1] if len(roots) > 1 else None
    for ev in events:
        item = ev.get("item") if isinstance(ev.get("item"), dict) else {}
        if ev.get("type") == "item.completed" and item.get("type") == "command_execution":
            candidates = _command_path_candidates(str(item.get("command") or ""), cwd_root)
            _record_outside_reads(rec, candidates, roots)
    return rec.outside_reads


def parse_trace(path: Path, vendor: str, known_skills: Iterable[str], *,
                 exit_code: int | None = None,
                 roots: Iterable[str | Path] | None = None) -> TraceRecord:
    """Normalise one raw CLI trace file. See DESIGN.md sec 3 for the contract.

    Activation is attributed only to names in `known_skills`; anything else
    found under a `skills/<name>/` path (a vendor built-in, or an unexpected
    library skill) is reported as `builtin:<name>` so it is measured, never
    hidden (DESIGN.md T-A).

    `exit_code`, when given, is the CLI process's own exit code (from
    `exec_agent`'s return value): a nonzero or negative value marks the
    record `ok=False` regardless of what the event stream itself claimed (R1
    finding I4). This is deliberately independent of the per-vendor
    completion-event checks above, which catch the case where the process
    exits 0 but never actually finished the turn.

    `roots`, when given, is the arm's allowed absolute path prefixes (its
    home and cwd, by convention home first -- see `_expand_home`). Every
    absolute or `~`-prefixed path token this module can find in a claude
    tool_use input (`file_path`, `path`, `pattern`, `command`) or a codex
    `command_execution` command, that resolves outside every root and is not
    in the small read-only-system-path allowlist, lands in
    `TraceRecord.outside_reads` (deduplicated, in first-seen order). With
    `roots=None`, `outside_reads` stays empty -- this module never guesses
    what a caller considers "inside".
    """
    known = {str(k) for k in known_skills}
    events = list(_iter_events(path))
    if vendor == "claude":
        rec = _parse_claude(events, known)
    elif vendor == "codex":
        rec = _parse_codex(events, known)
    else:
        raise ValueError(f"trace.parse_trace: unknown vendor {vendor!r}")
    rec.trace_path = str(path)
    if exit_code is not None and (exit_code != 0):
        rec.ok = False
        rec.error = rec.error or f"exit {exit_code}"
    if roots is not None:
        root_paths = [Path(r) for r in roots]
        if vendor == "claude":
            rec.outside_reads = _collect_claude_outside_reads(events, root_paths)
        else:
            rec.outside_reads = _collect_codex_outside_reads(events, root_paths)
    return rec
