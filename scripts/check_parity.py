#!/usr/bin/env python3
from __future__ import annotations

"""
Mechanical parity checker for the two register families that are
mechanically checkable today (Families 3 and 4 in
scripts/auditing/OPEN_ITEMS.md's parity register):

- canonical-headings: SKILL_REVIEW_CHECKLIST.md section 5's canonical-heading
  paragraph vs CANONICAL_HEADINGS in audit_skills.py.
- check-names: SKILL_REVIEW_CHECKLIST.md section 12's table vs the check
  names audit_skills.list_check_names() reports.

Exit codes:
  0 - both families in parity.
  1 - a mismatch was found; both sides are named in the output.
  2 - a marked region could not be extracted (missing/unbalanced/duplicated/
      empty marker pair). Never reported as parity.

Takes no arguments.
"""

import re
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).parent))

import audit_skills  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKLIST_PATH = REPO_ROOT / "scripts" / "auditing" / "SKILL_REVIEW_CHECKLIST.md"
PROCESS_DOC_PATH = REPO_ROOT / "scripts" / "auditing" / "SUBAGENT_REVIEW_PROCESS.md"
REVIEWER_PROMPT_PATH = REPO_ROOT / "scripts" / "auditing" / "reviewer-prompt.md"
SYNTHESIS_PROMPT_PATH = REPO_ROOT / "scripts" / "auditing" / "synthesis-prompt.md"
RESULT_TOOL_PATH = REPO_ROOT / "scripts" / "auditing" / "review-result.sh"

MARKER_RE = re.compile(r"^(?:#\s*)?<!-- parity:([a-z][a-z-]*):(start|end) -->\s*$", re.M)
BACKTICK_RE = re.compile(r"`([^`]+)`")
TABLE_ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*§(\d+)\s*\|")
SECTION_HEADING_RE = re.compile(r"^## (\d+)\.", re.M)
BULLET_RE = re.compile(r"^- ")
STATUS_FLAG_RE = re.compile(r"--status\s+<?([a-z][a-z-]*(?:\|[a-z][a-z-]*)*)>?")
SHELL_ALTERNATION_RE = re.compile(r"^\s*\(?([a-z][a-z-]*(?:\|[a-z][a-z-]*)+)\)", re.M)

# Members extracted by heading span (to end of file) instead of a marker
# pair. synthesis-prompt.md's render step substitutes placeholders with no
# marker-strip, so a marker there would be dispatched verbatim.
HEADING_SPAN_MEMBERS = {"SYNTHESIS_PROMPT_PATH": "## Output"}

FAMILY_LABELS = {
    "canonical-headings": (
        "SKILL_REVIEW_CHECKLIST.md §5 canonical-heading paragraph",
        "CANONICAL_HEADINGS in scripts/audit_skills.py",
    ),
    "check-names": (
        "SKILL_REVIEW_CHECKLIST.md §12 table",
        "list_check_names() in scripts/audit_skills.py",
    ),
}

PROSE_FAMILIES = {
    "removal-authority": {
        "anchors": {
            "delete:own-heading": "own heading",
            "delete:frontmatter-description": "frontmatter description",
            "delete:duplicate-rule": "rule already",
            "delete:heading-qualifier": "heading qualifier",
            "delete:output-contract-step": "output contract",
            "propose:whole-section": "whole section",
            "propose:references-or-scripts": "references/ or scripts/",
            "propose:skill-itself": "the skill itself",
            "propose:activation-cues": "activation cues found in",
        },
        "members": [
            ("SKILL_REVIEW_CHECKLIST.md §4", "CHECKLIST_PATH"),
            ("SUBAGENT_REVIEW_PROCESS.md \"Removal authority\"", "PROCESS_DOC_PATH"),
            ("reviewer-prompt.md delete/propose block", "REVIEWER_PROMPT_PATH"),
        ],
        "canonical": ("SKILL_REVIEW_CHECKLIST.md §4", 5),
    },
    "verdict-enum": {
        "declared": frozenset({"no-change", "changed", "questions"}),
        "flag_anchors": ("--differentiation", "--removals"),
        "members": [
            ("SKILL_REVIEW_CHECKLIST.md \"Verdicts\"", "CHECKLIST_PATH", "status-flag"),
            ("SUBAGENT_REVIEW_PROCESS.md \"Verdicts\"", "PROCESS_DOC_PATH", "status-flag"),
            ("reviewer-prompt.md Output block", "REVIEWER_PROMPT_PATH", "status-flag"),
            ("synthesis-prompt.md \"Output\"", "SYNTHESIS_PROMPT_PATH", "status-flag"),
            ("review-result.sh --status enum", "RESULT_TOOL_PATH", "shell-alternation"),
        ],
    },
}


class ParityExtractionError(Exception):
    def __init__(self, family_id: str, reason: str):
        self.family_id = family_id
        self.reason = reason
        super().__init__(f"{family_id}: {reason}")


class FamilyResult(NamedTuple):
    family_id: str
    ok: bool
    only_a: tuple[str, ...]
    only_b: tuple[str, ...]
    bad_sections: tuple[str, ...] = ()


class ProseMemberResult(NamedTuple):
    label: str
    missing: tuple[str, ...]
    duplicated: tuple[str, ...]
    bad_bullet_count: tuple[int, int] | None = None
    unexpected: tuple[str, ...] = ()
    missing_flags: tuple[str, ...] = ()


class ProseFamilyResult(NamedTuple):
    family_id: str
    ok: bool
    members: tuple[ProseMemberResult, ...]


def _region_lines(text: str, family_id: str) -> list[str]:
    starts = [m for m in MARKER_RE.finditer(text) if m.group(1) == family_id and m.group(2) == "start"]
    ends = [m for m in MARKER_RE.finditer(text) if m.group(1) == family_id and m.group(2) == "end"]
    if not starts or not ends:
        raise ParityExtractionError(family_id, "missing start or end marker")
    if len(starts) > 1 or len(ends) > 1:
        raise ParityExtractionError(family_id, "more than one marker pair")
    start, end = starts[0], ends[0]
    if end.start() < start.start():
        raise ParityExtractionError(family_id, "end marker before start marker")
    region = text[start.end():end.start()]
    return region.splitlines()


def _heading_span(text: str, heading: str, family_id: str) -> list[str]:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == heading:
            return lines[i + 1:]
    raise ParityExtractionError(family_id, f"heading {heading!r} not found")


def _family3_members(lines: list[str]) -> set[str]:
    members = set(BACKTICK_RE.findall("\n".join(lines)))
    if not members:
        raise ParityExtractionError("canonical-headings", "zero extracted members")
    return members


def _family4_rows(lines: list[str]) -> list[tuple[str, str]]:
    rows = []
    for line in lines:
        m = TABLE_ROW_RE.match(line.strip())
        if m:
            rows.append((m.group(1), m.group(2)))
    if not rows:
        raise ParityExtractionError("check-names", "zero extracted members")
    return rows


def check_family3(text: str) -> FamilyResult:
    members = _family3_members(_region_lines(text, "canonical-headings"))
    expected = set(audit_skills.CANONICAL_HEADINGS.values())
    only_a = members - expected
    only_b = expected - members
    return FamilyResult(
        "canonical-headings",
        not (only_a or only_b),
        tuple(sorted(only_a)),
        tuple(sorted(only_b)),
    )


def check_family4(text: str) -> FamilyResult:
    rows = _family4_rows(_region_lines(text, "check-names"))
    table_names = {name for name, _ in rows}
    expected = set(audit_skills.list_check_names())
    only_a = table_names - expected
    only_b = expected - table_names
    section_numbers = set(SECTION_HEADING_RE.findall(text))
    bad_sections = tuple(sorted({name for name, section in rows if section not in section_numbers}))
    return FamilyResult(
        "check-names",
        not (only_a or only_b or bad_sections),
        tuple(sorted(only_a)),
        tuple(sorted(only_b)),
        bad_sections,
    )


def _normalize(lines: list[str]) -> str:
    text = "\n".join(lines)
    text = text.replace("`", "")
    text = text.replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.lower()


def _extract_tokens(kind: str, lines: list[str]) -> frozenset[str]:
    if kind == "shell-alternation":
        matches = SHELL_ALTERNATION_RE.finditer("\n".join(lines))
    else:
        matches = STATUS_FLAG_RE.finditer(_normalize(lines))
    tokens: set[str] = set()
    for m in matches:
        tokens.update(m.group(1).split("|"))
    return frozenset(tokens)


def check_prose_family(family_id: str) -> ProseFamilyResult:
    spec = PROSE_FAMILIES[family_id]
    declared = spec.get("declared")
    flag_anchors = spec.get("flag_anchors", ())
    anchors = spec.get("anchors")
    canonical_label, canonical_count = spec.get("canonical", (None, None))
    member_results = []
    ok = True
    for member in spec["members"]:
        label, const_name = member[0], member[1]
        kind = member[2] if len(member) > 2 else None
        path = globals()[const_name]
        text = path.read_text(encoding="utf-8")
        heading = HEADING_SPAN_MEMBERS.get(const_name)
        lines = _heading_span(text, heading, family_id) if heading else _region_lines(text, family_id)

        if declared is not None:
            tokens = _extract_tokens(kind, lines)
            missing = declared - tokens
            unexpected = tokens - declared
            missing_flags: tuple[str, ...] = ()
            if kind != "shell-alternation":
                normalized = _normalize(lines)
                missing_flags = tuple(f for f in flag_anchors if f not in normalized)
            member_ok = not missing and not unexpected and not missing_flags
            ok = ok and member_ok
            member_results.append(
                ProseMemberResult(
                    label,
                    tuple(sorted(missing)),
                    (),
                    None,
                    tuple(sorted(unexpected)),
                    missing_flags,
                )
            )
            continue

        normalized = _normalize(lines)
        missing = []
        duplicated = []
        for key, phrase in anchors.items():
            count = normalized.count(phrase)
            if count == 0:
                missing.append(key)
            elif count > 1:
                duplicated.append(key)
        bad_bullet_count = None
        if label == canonical_label:
            bullet_count = sum(1 for line in lines if BULLET_RE.match(line))
            if bullet_count != canonical_count:
                bad_bullet_count = (bullet_count, canonical_count)
        member_ok = not missing and not duplicated and bad_bullet_count is None
        ok = ok and member_ok
        member_results.append(
            ProseMemberResult(label, tuple(sorted(missing)), tuple(sorted(duplicated)), bad_bullet_count)
        )
    return ProseFamilyResult(family_id, ok, tuple(member_results))


def _report_prose(result: ProseFamilyResult) -> None:
    print(f"PARITY FAIL: {result.family_id}")
    for member in result.members:
        if (
            not member.missing
            and not member.duplicated
            and member.bad_bullet_count is None
            and not member.unexpected
            and not member.missing_flags
        ):
            continue
        parts = []
        if member.missing:
            parts.append(f"missing {list(member.missing)}")
        if member.duplicated:
            parts.append(f"duplicated {list(member.duplicated)}")
        if member.bad_bullet_count is not None:
            actual, expected = member.bad_bullet_count
            parts.append(f"bullet count {actual} != expected {expected}")
        if member.unexpected:
            parts.append(f"unexpected {list(member.unexpected)}")
        if member.missing_flags:
            parts.append(f"missing-flags {list(member.missing_flags)}")
        print(f"  member {member.label}: " + " ".join(parts))


def _report(result: FamilyResult) -> None:
    label_a, label_b = FAMILY_LABELS[result.family_id]
    print(f"PARITY FAIL: {result.family_id}")
    print(f"  member A: {label_a}")
    print(f"  member B: {label_b}")
    if result.only_a:
        print(f"  only in A ({label_a}): {list(result.only_a)}")
    if result.only_b:
        print(f"  only in B ({label_b}): {list(result.only_b)}")
    if result.bad_sections:
        print(f"  rows citing a section that does not exist: {list(result.bad_sections)}")


def main() -> int:
    text = CHECKLIST_PATH.read_text(encoding="utf-8")
    try:
        results = [check_family3(text), check_family4(text)]
        prose_results = [check_prose_family(family_id) for family_id in PROSE_FAMILIES]
    except ParityExtractionError as exc:
        print(f"PARITY EXTRACTION ERROR: {exc}", file=sys.stderr)
        return 2

    ok = all(result.ok for result in results) and all(result.ok for result in prose_results)
    for result in results:
        if not result.ok:
            _report(result)
    for result in prose_results:
        if not result.ok:
            _report_prose(result)
    if ok:
        ids = ["canonical-headings", "check-names", *PROSE_FAMILIES]
        print(f"parity: ok ({', '.join(ids)})")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
