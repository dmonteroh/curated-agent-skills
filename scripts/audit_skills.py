#!/usr/bin/env python3
from __future__ import annotations

"""
Repo-wide skill quality/performance audit.

Checks (intentionally lightweight; no PyYAML dependency):
- SKILL.md has YAML frontmatter with name + description
- Entry point (SKILL.md) is <= 200 lines (performance guardrail)
- Backticked local file references inside a skill resolve (for refs like `references/x.md`)
- No network assumptions in SKILL.md (skills should be usable offline)
- Frontmatter name matches folder name (avoid agent confusion)
"""

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "scripts"}

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
KV_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$")


def _parse_frontmatter(text: str) -> dict[str, str]:
    m = FM_RE.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    current: str | None = None
    for line in m.group(1).splitlines():
        if current and (line.startswith(" ") or line.startswith("\t")):
            cont = line.strip()
            if cont:
                fm[current] = (fm.get(current, "") + " " + cont).strip()
            continue
        mm = KV_RE.match(line)
        if not mm:
            current = None
            continue
        key = mm.group(1)
        val = mm.group(2).strip().strip("\"'")
        fm[key] = val
        current = key
    return fm


def _find_backtick_paths(text: str) -> set[str]:
    out: set[str] = set()
    for m in re.finditer(r"`([^`]+)`", text):
        val = m.group(1)
        if " " in val:
            continue
        if "/" in val and any(
            val.endswith(ext) for ext in (".md", ".sh", ".py", ".txt", ".cjs", ".ts", ".js")
        ):
            if not val.startswith("http"):
                out.add(val)
    return out


def scan_skill(dirpath: Path) -> list[str]:
    skill_file = dirpath / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    fm = _parse_frontmatter(text)

    issues: list[str] = []
    name = fm.get("name", "").strip()
    desc = fm.get("description", "").strip()

    if not fm:
        issues.append("missing_frontmatter")
    if not name:
        issues.append("missing_name_in_frontmatter")
    if not desc:
        issues.append("missing_description_in_frontmatter")

    if len(lines) > 200:
        issues.append(f"entry_over_200_lines:{len(lines)}")

    if name and name != dirpath.name:
        issues.append(f"name_folder_mismatch:{name}!=${dirpath.name}")

    missing = []
    for rel in sorted(_find_backtick_paths(text)):
        p = (dirpath / rel).resolve()
        try:
            p.relative_to(dirpath.resolve())
        except Exception:
            # Ignore paths that escape the skill dir.
            continue
        if not p.exists():
            missing.append(rel)
    if missing:
        issues.append("missing_local_refs:" + ",".join(missing))

    if re.search(r"\bWebFetch\b|https?://raw\.githubusercontent\.com", text, re.I):
        issues.append("network_assumption")

    return issues


def main() -> int:
    skills: list[tuple[str, list[str]]] = []
    for entry in sorted(ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name in SKIP_DIRS:
            continue
        if not (entry / "SKILL.md").is_file():
            continue
        skills.append((entry.name, scan_skill(entry)))

    bad = [(name, issues) for name, issues in skills if issues]

    print(f"skills: {len(skills)}")
    print(f"skills_with_issues: {len(bad)}")
    if not bad:
        return 0

    for name, issues in bad:
        print(f"- {name}: {issues}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

