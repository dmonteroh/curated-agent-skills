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

MARKER_RE = re.compile(r"^<!-- parity:([a-z][a-z-]*):(start|end) -->\s*$", re.M)
BACKTICK_RE = re.compile(r"`([^`]+)`")
TABLE_ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*§(\d+)\s*\|")
SECTION_HEADING_RE = re.compile(r"^## (\d+)\.", re.M)
BULLET_RE = re.compile(r"^- ")

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


def check_prose_family(family_id: str) -> ProseFamilyResult:
    spec = PROSE_FAMILIES[family_id]
    anchors = spec["anchors"]
    canonical_label, canonical_count = spec["canonical"]
    member_results = []
    ok = True
    for label, const_name in spec["members"]:
        path = globals()[const_name]
        text = path.read_text(encoding="utf-8")
        lines = _region_lines(text, family_id)
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
        if not member.missing and not member.duplicated and member.bad_bullet_count is None:
            continue
        parts = []
        if member.missing:
            parts.append(f"missing {list(member.missing)}")
        if member.duplicated:
            parts.append(f"duplicated {list(member.duplicated)}")
        if member.bad_bullet_count is not None:
            actual, expected = member.bad_bullet_count
            parts.append(f"bullet count {actual} != expected {expected}")
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
