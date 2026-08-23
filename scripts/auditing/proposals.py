#!/usr/bin/env python3
from __future__ import annotations

"""
Removal-proposal ledger: the operator's accept/decline loop for the parallel
review pipeline.

The pipeline's authority split (SKILL_REVIEW_CHECKLIST.md section 4) makes whole
sections, files under references/ or scripts/, and whole skills
propose-never-execute. This tool closes the loop on those proposals:

  record  - run by run_parallel_skill_reviews.sh after a pass: reads each
            <skill>.synthesis.removals sidecar (written by review-result.sh
            from the --removals flag) and appends one PROPOSALS.md entry per
            numbered proposal, deduplicated by content hash against the
            ledger and against ids already ruled in the rulings record
            (logs/removal-rulings.md).
  lint    - validates the ledger: every ruling is pending|approved|declined,
            every entry's text matches its recorded checksum. All problems
            are reported at once.
  apply   - lints first and refuses to act on ANY problem. Then, per entry:
            declined -> a Declined row appended to the rulings record at
            logs/removal-rulings.md, entry removed from the ledger;
            approved -> a writer
            agent is dispatched scoped to that one proposal, the resulting
            diff is verified (something changed, nothing outside the skill's
            own surface), then an executed row is appended and the entry
            removed. Pending entries are never touched. The ledger is
            rewritten after every resolved entry, so a rerun resumes exactly
            where a failure stopped and a second run with nothing approved
            is a no-op.

The operator's whole interface is editing the `ruling:` line of an entry and
running `apply`. Nothing else in the ledger is operator-editable; the
checksum lint blocks apply if anything else changed.
"""

import argparse
import datetime as _dt
import hashlib
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

RULING_WORDS = ("pending", "approved", "declined")

# Same exemption the runner appends to its claude calls: a dispatch from the
# repo root auto-loads CLAUDE.md, whose bootstrap gate can otherwise consume
# the run (see OPEN_ITEMS.md, settled call "Dispatched calls skip the
# repository session-bootstrap").
DISPATCH_BOOTSTRAP_EXEMPTION = (
    "This dispatched call's session-bootstrap is already handled by the orchestrator: "
    "skip every CLAUDE.md/AGENTS.md bootstrap step (no .agent/scripts/status.sh, no .agent/ reads) "
    "and execute the user-message task immediately."
)

LEDGER_HEADER = """# Removal proposals — pending rulings

<!-- Machine-managed by scripts/auditing/proposals.py. `record` (run by
run_parallel_skill_reviews.sh after a review pass) appends one entry per
proposal from the synthesis .removals artifacts; `apply` executes rulings and
moves resolved entries to the rulings record at logs/removal-rulings.md, so
this file holds only proposals still awaiting a ruling and ends after this
comment when nothing awaits one.

Operator: edit ONLY an entry's `ruling:` line — pending | approved |
declined, optionally followed by " — <note>". Then run:
  .venv/bin/python scripts/auditing/proposals.py apply
Any other edit fails the checksum lint and blocks apply until restored.

Dedupe is by content hash (the id in each entry heading), so a re-worded
duplicate of an already-ruled proposal can reappear here; under Quality
Gate 7 that is a review defect — decline it and the ruling is permanent. -->
"""

RULINGS_HEADER = """# Removal rulings — permanent record

<!-- Machine-managed by scripts/auditing/proposals.py `apply`, which appends
one row per resolved ruling. Not operator-editable; nothing else reads it as
a contract.

This file lives in the gitignored logs/ directory by operator ruling
(2026-08-22): rulings are an append-only execution record, not open items,
and they were burying the ~10 lines of OPEN_ITEMS.md that are actually open.
Known consequence, accepted: the record is untracked, so on a fresh clone or
a wiped logs/ directory `proposals.py record` no longer sees these ids and
can re-file an already-ruled proposal, and reviewer arms lose the
don't-re-propose memory. Decline the repeat; the ruling below still stands. -->

| Date | Skill | Proposal | Ruling |
| --- | --- | --- | --- |
"""

ENTRY_HEADING_RE = re.compile(r"^## proposal ([0-9a-f]{12}) — (\S+)$")
RECORDED_RE = re.compile(r"^- recorded: (\d{4}-\d{2}-\d{2})$")
RULING_RE = re.compile(r"^- ruling: (.+)$")
CHECKSUM_RE = re.compile(r"^- checksum: ([0-9a-f]{16})$")
FENCE_RE = re.compile(r"^(`{3,})text$")
RULED_ID_RE = re.compile(r"`id:([0-9a-f]{12})`")
# Numbered proposals are split only on a flush-left, consecutively numbered
# list: an indented or out-of-sequence number is body text, not a new item.
ITEM_START_RE = re.compile(r"^(\d+)[.)]\s+", re.M)
POLICY_SYNTHESIS_RE = re.compile(r"^site=synthesis tier=\S+ vendor=(\S+) resolved=(\S+)")
APPLIED_MARKER_RE = re.compile(r"^APPLIED:", re.M)
BLOCKED_MARKER_RE = re.compile(r"^APPLY-BLOCKED:(.*)$", re.M)


@dataclass
class Entry:
    entry_id: str
    skill: str
    recorded: str
    ruling: str  # the raw value of the ruling: line, note included
    checksum: str
    text: str

    @property
    def ruling_word(self) -> str:
        return _split_ruling(self.ruling)[0]

    @property
    def ruling_note(self) -> str:
        return _split_ruling(self.ruling)[1]


class LedgerError(Exception):
    pass


def _split_ruling(raw: str) -> tuple[str, str]:
    for sep in (" — ", " - "):
        if sep in raw:
            word, note = raw.split(sep, 1)
            return word.strip().lower(), note.strip()
    return raw.strip().lower(), ""


def normalized_hash(skill: str, text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    return hashlib.sha256(f"{skill}\n{normalized}".encode("utf-8")).hexdigest()[:12]


def text_checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def split_items(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    accepted = []
    for match in ITEM_START_RE.finditer(text):
        if int(match.group(1)) == len(accepted) + 1:
            accepted.append(match)
    if not accepted:
        return [text]
    items = []
    for i, match in enumerate(accepted):
        end = accepted[i + 1].start() if i + 1 < len(accepted) else len(text)
        item = text[match.end():end].strip()
        if item:
            items.append(item)
    return items


def _fence_for(text: str) -> str:
    longest = 0
    for run in re.findall(r"`+", text):
        longest = max(longest, len(run))
    return "`" * max(3, longest + 1)


def serialize_entry(entry: Entry) -> str:
    fence = _fence_for(entry.text)
    return (
        f"## proposal {entry.entry_id} — {entry.skill}\n"
        f"\n"
        f"- recorded: {entry.recorded}\n"
        f"- ruling: {entry.ruling}\n"
        f"- checksum: {entry.checksum}\n"
        f"\n"
        f"{fence}text\n"
        f"{entry.text}\n"
        f"{fence}\n"
    )


def serialize_ledger(entries: list[Entry]) -> str:
    parts = [LEDGER_HEADER]
    for entry in entries:
        parts.append("\n" + serialize_entry(entry))
    return "".join(parts)


def parse_ledger(path: Path) -> list[Entry]:
    """Strict parse; raises LedgerError on any structural damage."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    entries: list[Entry] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            heading = ENTRY_HEADING_RE.match(line)
            if not heading:
                raise LedgerError(f"{path.name}:{i + 1}: malformed entry heading: {line!r}")
            entry_id, skill = heading.group(1), heading.group(2)
            fields: dict[str, str] = {}
            i += 1
            fence = None
            while i < len(lines):
                fld = lines[i]
                if not fld.strip():
                    i += 1
                    continue
                fence_match = FENCE_RE.match(fld)
                if fence_match:
                    fence = fence_match.group(1)
                    i += 1
                    break
                matched = False
                for key, rx in (("recorded", RECORDED_RE), ("ruling", RULING_RE), ("checksum", CHECKSUM_RE)):
                    m = rx.match(fld)
                    if m:
                        if key in fields:
                            raise LedgerError(f"{path.name}:{i + 1}: duplicate {key}: line in entry {entry_id}")
                        fields[key] = m.group(1)
                        matched = True
                        break
                if not matched:
                    raise LedgerError(f"{path.name}:{i + 1}: unexpected line in entry {entry_id}: {fld!r}")
                i += 1
            missing = [k for k in ("recorded", "ruling", "checksum") if k not in fields]
            if missing:
                raise LedgerError(f"{path.name}: entry {entry_id} is missing field(s): {', '.join(missing)}")
            if fence is None:
                raise LedgerError(f"{path.name}: entry {entry_id} has no ```text block")
            body: list[str] = []
            closed = False
            while i < len(lines):
                if lines[i] == fence:
                    closed = True
                    i += 1
                    break
                body.append(lines[i])
                i += 1
            if not closed:
                raise LedgerError(f"{path.name}: entry {entry_id}'s ```text block is never closed")
            entries.append(
                Entry(entry_id, skill, fields["recorded"], fields["ruling"], fields["checksum"], "\n".join(body))
            )
        else:
            i += 1
    return entries


def lint_entries(entries: list[Entry]) -> list[str]:
    errors = []
    seen: set[str] = set()
    for entry in entries:
        if entry.ruling_word not in RULING_WORDS:
            errors.append(
                f"entry {entry.entry_id} ({entry.skill}): ruling '{entry.ruling_word}' is not one of: "
                + " | ".join(RULING_WORDS)
            )
        if text_checksum(entry.text) != entry.checksum:
            errors.append(
                f"entry {entry.entry_id} ({entry.skill}): proposal text does not match its checksum - "
                "the text was edited; restore it (the ruling: line is the only editable line)"
            )
        if entry.entry_id in seen:
            errors.append(f"entry {entry.entry_id} ({entry.skill}): duplicate id in the ledger")
        seen.add(entry.entry_id)
    return errors


def write_ledger(path: Path, entries: list[Entry]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(serialize_ledger(entries), encoding="utf-8")
    tmp.replace(path)


def rulings_record_path(auditing: Path) -> Path:
    return auditing / "logs" / "removal-rulings.md"


def ruled_ids(rulings_path: Path) -> set[str]:
    """Ids already ruled. The record is gitignored (operator ruling
    2026-08-22), so a fresh clone legitimately has none: a missing file is an
    empty set, not an error. The accepted cost is that an already-ruled
    proposal can be re-recorded there; decline it."""
    if not rulings_path.exists():
        return set()
    return set(RULED_ID_RE.findall(rulings_path.read_text(encoding="utf-8")))


def append_ruling_row(rulings_path: Path, entry: Entry, ruling_text: str, today: str) -> None:
    """Appends one row to the rulings record, creating it if this is the first
    ruling in a fresh checkout."""
    if not rulings_path.exists():
        rulings_path.parent.mkdir(parents=True, exist_ok=True)
        rulings_path.write_text(RULINGS_HEADER, encoding="utf-8")
    lines = rulings_path.read_text(encoding="utf-8").splitlines(keepends=True)
    last_row = None
    for i, line in enumerate(lines):
        if line.startswith("|"):
            last_row = i
    if last_row is None:
        raise LedgerError(f"{rulings_path.name}: no rulings table found")
    summary = entry.text.strip().splitlines()[0]
    if len(summary) > 120:
        summary = summary[:117] + "..."
    summary = summary.replace("|", "\\|")
    row = f"| {today} | `{entry.skill}` | {summary} `id:{entry.entry_id}` | {ruling_text} |\n"
    lines.insert(last_row + 1, row)
    tmp = rulings_path.with_name(rulings_path.name + ".tmp")
    tmp.write_text("".join(lines), encoding="utf-8")
    tmp.replace(rulings_path)


# --- record -----------------------------------------------------------------


def cmd_record(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    ledger_path = root / "scripts" / "auditing" / "PROPOSALS.md"
    rulings_path = rulings_record_path(root / "scripts" / "auditing")
    logs_dir = Path(args.logs_dir).resolve()
    try:
        entries = parse_ledger(ledger_path)
    except LedgerError as exc:
        print(f"proposals.py record: refusing to append to a damaged ledger: {exc}", file=sys.stderr)
        return 1
    known = {e.entry_id for e in entries} | ruled_ids(rulings_path)
    today = _dt.date.today().isoformat()
    recorded = skipped = 0
    warnings = []
    for verdict_path in sorted(logs_dir.glob("*.synthesis.verdict")):
        keys = dict(
            line.split("=", 1)
            for line in verdict_path.read_text(encoding="utf-8").splitlines()
            if "=" in line
        )
        if keys.get("REMOVAL_PROPOSALS") != "1":
            continue
        skill = verdict_path.name[: -len(".synthesis.verdict")]
        sidecar = logs_dir / f"{skill}.synthesis.removals"
        if not sidecar.exists():
            warnings.append(
                f"warning: {skill}: REMOVAL_PROPOSALS=1 but no {sidecar.name} sidecar "
                "(pre-upgrade run?); proposal text is only in the last-message artifact"
            )
            continue
        for item in split_items(sidecar.read_text(encoding="utf-8")):
            entry_id = normalized_hash(skill, item)
            if entry_id in known:
                skipped += 1
                continue
            known.add(entry_id)
            entries.append(Entry(entry_id, skill, today, "pending", text_checksum(item), item))
            recorded += 1
    if recorded:
        write_ledger(ledger_path, entries)
    for warning in warnings:
        print(warning, file=sys.stderr)
    pending = sum(1 for e in entries if e.ruling_word == "pending")
    print(
        f"proposals.py record: {recorded} recorded, {skipped} already known; "
        f"{pending} entr{'y' if pending == 1 else 'ies'} pending in {ledger_path.relative_to(root)}"
    )
    return 0


# --- lint -------------------------------------------------------------------


def _load_and_lint(ledger_path: Path) -> tuple[list[Entry], list[str]]:
    try:
        entries = parse_ledger(ledger_path)
    except LedgerError as exc:
        return [], [str(exc)]
    return entries, lint_entries(entries)


def cmd_lint(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    entries, errors = _load_and_lint(root / "scripts" / "auditing" / "PROPOSALS.md")
    if errors:
        for error in errors:
            print(f"proposals.py lint: {error}", file=sys.stderr)
        return 1
    counts = {word: sum(1 for e in entries if e.ruling_word == word) for word in RULING_WORDS}
    print(
        "proposals.py lint: ok - "
        + ", ".join(f"{counts[word]} {word}" for word in RULING_WORDS)
    )
    return 0


# --- apply ------------------------------------------------------------------


def default_dispatch_argv(runner_path: Path) -> list[str]:
    proc = subprocess.run(
        [str(runner_path), "--print-model-policy"], capture_output=True, text=True, check=False
    )
    for line in proc.stdout.splitlines():
        m = POLICY_SYNTHESIS_RE.match(line)
        if m:
            vendor, model = m.group(1), m.group(2)
            if vendor != "claude":
                raise LedgerError(
                    f"synthesis vendor is '{vendor}'; pass --dispatch-cmd explicitly for a non-claude writer"
                )
            return [
                "claude",
                "--print",
                "--model",
                model,
                "--append-system-prompt",
                DISPATCH_BOOTSTRAP_EXEMPTION,
                "--permission-mode",
                "acceptEdits",
                "--allowedTools",
                "Read,Glob,Grep,Edit,Write",
            ]
    raise LedgerError(
        "could not resolve the writer model from --print-model-policy; pass --dispatch-cmd explicitly"
    )


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
    ).stdout


def _diff_fingerprints(root: Path) -> dict[str, str]:
    """Per-path hash of the unstaged patch. Path sets are blind to a new edit
    on an already-dirty file (the synthesis pass leaves the skill file
    modified before apply runs), so verification compares patch content."""
    fingerprints: dict[str, str] = {}
    path = None
    chunk: list[str] = []
    for line in _git(root, "diff").splitlines(keepends=True):
        if line.startswith("diff --git "):
            if path is not None:
                fingerprints[path] = hashlib.sha256("".join(chunk).encode("utf-8")).hexdigest()
            tail = line.split()[-1]
            path = tail[2:] if tail.startswith("b/") else tail
            path = path.strip().strip('"')
            chunk = []
        chunk.append(line)
    if path is not None:
        fingerprints[path] = hashlib.sha256("".join(chunk).encode("utf-8")).hexdigest()
    return fingerprints


def _touched_paths(root: Path, before_status: set[str], before_fps: dict[str, str]) -> set[str]:
    after_status = set(_git(root, "status", "--porcelain").splitlines())
    after_fps = _diff_fingerprints(root)
    touched = {p for p, fp in after_fps.items() if before_fps.get(p) != fp}
    touched.update(p for p in before_fps if p not in after_fps)
    for line in after_status - before_status:
        touched.add(line[3:].strip().strip('"'))
    return {p for p in touched if p}


def _in_scope(path: str, skill: str) -> bool:
    return path.startswith(f"skills/{skill}/") or path == f"scripts/auditing/trigger-cases/{skill}.md"


def cmd_apply(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    auditing = root / "scripts" / "auditing"
    ledger_path = auditing / "PROPOSALS.md"
    rulings_path = rulings_record_path(auditing)
    prompt_path = auditing / "apply-prompt.md"
    logs_dir = auditing / "logs"

    entries, errors = _load_and_lint(ledger_path)
    if errors:
        for error in errors:
            print(f"proposals.py apply: {error}", file=sys.stderr)
        print("proposals.py apply: refusing to act while the ledger has problems; nothing was applied", file=sys.stderr)
        return 1
    declined = [e for e in entries if e.ruling_word == "declined"]
    approved = [e for e in entries if e.ruling_word == "approved"]
    pending = [e for e in entries if e.ruling_word == "pending"]
    if not declined and not approved:
        print(
            f"proposals.py apply: nothing to apply - {len(pending)} entr{'y' if len(pending) == 1 else 'ies'} "
            "pending a ruling"
        )
        return 0

    today = _dt.date.today().isoformat()
    failures: list[str] = []
    executed = 0

    for entry in declined:
        note = f" {entry.ruling_note}" if entry.ruling_note else ""
        append_ruling_row(rulings_path, entry, f"**Declined.**{note}", today)
        entries = [e for e in entries if e.entry_id != entry.entry_id]
        write_ledger(ledger_path, entries)
        print(f"[declined] {entry.entry_id} ({entry.skill}) -> recorded in logs/removal-rulings.md")

    dispatch_argv: list[str] | None = None
    if approved:
        try:
            if args.dispatch_cmd:
                dispatch_argv = shlex.split(args.dispatch_cmd)
            else:
                dispatch_argv = default_dispatch_argv(auditing / "run_parallel_skill_reviews.sh")
        except LedgerError as exc:
            print(f"proposals.py apply: {exc}", file=sys.stderr)
            return 1
        prompt_template = prompt_path.read_text(encoding="utf-8")

    for entry in approved:
        prompt = (
            prompt_template.replace("SKILL_DIRECTORY", f"skills/{entry.skill}")
            .replace("SKILL_NAME", entry.skill)
            .replace("PROPOSAL_TEXT", entry.text)
            .replace("RULING_NOTE", entry.ruling_note or "none")
        )
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_path = logs_dir / f"apply.{entry.entry_id}.log"
        before_status = set(_git(root, "status", "--porcelain").splitlines())
        before_fps = _diff_fingerprints(root)
        proc = subprocess.run(
            dispatch_argv, input=prompt, capture_output=True, text=True, check=False, cwd=str(root)
        )
        log_path.write_text(proc.stdout + ("\n--- stderr ---\n" + proc.stderr if proc.stderr else ""), encoding="utf-8")
        touched = _touched_paths(root, before_status, before_fps)
        out_of_scope = sorted(p for p in touched if not _in_scope(p, entry.skill))

        blocked = BLOCKED_MARKER_RE.search(proc.stdout)
        if blocked:
            failures.append(
                f"entry {entry.entry_id} ({entry.skill}): writer reported APPLY-BLOCKED:{blocked.group(1).rstrip()} "
                f"(log: {log_path.relative_to(root)})"
            )
            continue
        if proc.returncode != 0:
            failures.append(
                f"entry {entry.entry_id} ({entry.skill}): writer exited {proc.returncode} "
                f"(log: {log_path.relative_to(root)}); entry left approved for a rerun"
            )
            continue
        if out_of_scope:
            failures.append(
                f"entry {entry.entry_id} ({entry.skill}): writer touched out-of-scope path(s) "
                f"{out_of_scope} - review and revert them; entry left approved (log: {log_path.relative_to(root)})"
            )
            continue
        if not touched:
            failures.append(
                f"entry {entry.entry_id} ({entry.skill}): writer changed nothing and did not report "
                f"APPLY-BLOCKED (log: {log_path.relative_to(root)}); entry left approved"
            )
            continue
        if not APPLIED_MARKER_RE.search(proc.stdout):
            failures.append(
                f"entry {entry.entry_id} ({entry.skill}): writer made edits but its final message has no "
                f"APPLIED: line - review the diff before trusting it; entry left approved "
                f"(log: {log_path.relative_to(root)})"
            )
            continue
        note = f" {entry.ruling_note}" if entry.ruling_note else ""
        append_ruling_row(rulings_path, entry, f"**Approved, executed {today}.**{note}", today)
        entries = [e for e in entries if e.entry_id != entry.entry_id]
        write_ledger(ledger_path, entries)
        executed += 1
        print(f"[executed] {entry.entry_id} ({entry.skill}): {sorted(touched)}")

    for failure in failures:
        print(f"proposals.py apply: {failure}", file=sys.stderr)

    if executed and not args.no_audit:
        audit = subprocess.run([str(root / "scripts" / "audit-skills.sh")], cwd=str(root), check=False)
        if audit.returncode != 0:
            print(f"proposals.py apply: audit exited {audit.returncode} after applying - fix before committing", file=sys.stderr)
            return 1

    if executed:
        print(
            f"proposals.py apply: {executed} executed, {len(declined)} declined, {len(pending)} still pending. "
            "Next: review the diff, regenerate the golden snapshot if a file was added or removed "
            "(python3 scripts/tests/generate_snapshot.py), then commit."
        )
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    sub = parser.add_subparsers(dest="command", required=True)
    p_record = sub.add_parser("record", help="record proposals from a run's synthesis artifacts")
    p_record.add_argument("--logs-dir", default=str(Path(__file__).resolve().parent / "logs"))
    p_record.set_defaults(func=cmd_record)
    p_lint = sub.add_parser("lint", help="validate the ledger and report every problem")
    p_lint.set_defaults(func=cmd_lint)
    p_apply = sub.add_parser("apply", help="execute approved/declined rulings; pending is untouched")
    p_apply.add_argument("--dispatch-cmd", default=None, help="writer command reading the prompt on stdin (default: the runner's synthesis-site model policy)")
    p_apply.add_argument("--no-audit", action="store_true")
    p_apply.set_defaults(func=cmd_apply)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
