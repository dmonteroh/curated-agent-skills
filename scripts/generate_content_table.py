#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        return s[1:-1].strip()
    return s


def _parse_frontmatter(text: str) -> dict[str, str]:
    """
    Parse minimal YAML frontmatter:
      ---
      name: foo
      description: bar
      ---
    We intentionally avoid requiring PyYAML.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fm: dict[str, str] = {}
    current_scalar_key: str | None = None
    current_map_key: str | None = None
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            break

        m = re.match(r"^(\s*)([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)\s*$", line)
        if m:
            indent = len(m.group(1))
            key = m.group(2).strip()
            val = _strip_quotes(m.group(3))
            if indent == 0:
                fm[key] = val
                current_map_key = key if not val else None
                current_scalar_key = key if val else None
                continue
            if current_map_key and indent > 0:
                nested = f"{current_map_key}.{key}"
                fm[nested] = val
                current_scalar_key = nested if val else None
                continue

        # YAML continuation lines (simple scalar values only).
        if current_scalar_key is not None and (line.startswith(" ") or line.startswith("\t")):
            cont = line.strip()
            if cont:
                fm[current_scalar_key] = (fm.get(current_scalar_key, "") + " " + cont).strip()
            continue
        current_scalar_key = None
        if line and not line.startswith((" ", "\t")):
            current_map_key = None
    return fm


def _one_line(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _escape_table_cell(s: str) -> str:
    # Markdown tables use '|' as a delimiter.
    return s.replace("|", "\\|")


def load_skills() -> list[tuple[str, str, str]]:
    skills: list[tuple[str, str, str]] = []
    if not SKILLS_ROOT.is_dir():
        return skills
    for entry in sorted(SKILLS_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue

        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            continue

        text = skill_file.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)
        name = fm.get("name", entry.name).strip() or entry.name
        desc = _one_line(fm.get("description", "").strip())
        category = _one_line(fm.get("metadata.category", "").strip())
        skills.append((name, desc, category))

    skills.sort(key=lambda x: x[0].lower())
    return skills


def main() -> int:
    skills = load_skills()

    lines: list[str] = []
    lines.append("# Content Table")
    lines.append("")
    lines.append(f"Total skills: {len(skills)}")
    lines.append("")

    by_category: dict[str, list[tuple[str, str]]] = {}
    for name, desc, category in skills:
        cat = category if category else "Uncategorized"
        by_category.setdefault(cat, []).append((name, desc))

    def _cat_sort_key(cat: str) -> tuple[int, str]:
        return (1, "") if cat == "Uncategorized" else (0, cat.lower())

    for category in sorted(by_category.keys(), key=_cat_sort_key):
        heading = category if category == "Uncategorized" else category.replace("-", " ").title()
        lines.append(f"## {heading}")
        lines.append("")
        lines.append("| Skill | Summary |")
        lines.append("| --- | --- |")
        for name, desc in sorted(by_category[category], key=lambda x: x[0].lower()):
            lines.append(f"| `{_escape_table_cell(name)}` | {_escape_table_cell(desc)} |")
        lines.append("")

    (ROOT / "CONTENT_TABLE.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
