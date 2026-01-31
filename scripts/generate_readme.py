#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
    current_key: str | None = None
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            break

        # YAML continuation lines (e.g. folded multiline description):
        #   description: first line
        #     second line
        # We only need this for simple scalar values; keep it minimal.
        if current_key is not None and (line.startswith(" ") or line.startswith("\t")):
            cont = line.strip()
            if cont:
                fm[current_key] = (fm.get(current_key, "") + " " + cont).strip()
            continue

        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)\s*$", line)
        if not m:
            current_key = None
            continue
        key = m.group(1).strip()
        val = _strip_quotes(m.group(2))
        fm[key] = val
        current_key = key
    return fm


def _one_line(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _escape_table_cell(s: str) -> str:
    # Markdown tables use '|' as a delimiter.
    return s.replace("|", "\\|")


def load_skills() -> list[tuple[str, str]]:
    skills: list[tuple[str, str]] = []
    for entry in sorted(ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if entry.name == "scripts":
            continue

        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            continue

        text = skill_file.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)
        name = fm.get("name", entry.name).strip() or entry.name
        desc = _one_line(fm.get("description", "").strip())
        skills.append((name, desc))

    skills.sort(key=lambda x: x[0].lower())
    return skills


def main() -> int:
    skills = load_skills()

    lines: list[str] = []
    lines.append("# codex-curated-skills")
    lines.append("")
    lines.append(
        f"This repo contains {len(skills)} skills. Each folder is a skill with a `SKILL.md` definition."
    )
    lines.append("")
    lines.append("## Skills")
    lines.append("")
    lines.append("| Skill | Summary |")
    lines.append("| --- | --- |")
    for name, desc in skills:
        lines.append(f"| `{_escape_table_cell(name)}` | {_escape_table_cell(desc)} |")
    lines.append("")

    (ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
