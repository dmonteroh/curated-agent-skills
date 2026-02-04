#!/usr/bin/env python3
from __future__ import annotations

"""
Repo-wide skill quality/performance audit.

Checks (intentionally lightweight; no PyYAML dependency):
- SKILL.md has YAML frontmatter with name + description
- Frontmatter values that include `: ` are quoted (Codex skill loader is strict YAML)
- Entry point (SKILL.md) is <= 200 lines (performance guardrail)
- Backticked local file references inside a skill resolve (for refs like `references/x.md`)
- No network assumptions in SKILL.md (skills should be usable offline)
- Frontmatter name matches folder name (avoid agent confusion)
- Name + description token budget (frontmatter) stays within bounds
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import tiktoken  # type: ignore
except ModuleNotFoundError:
    tiktoken = None

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
SKIP_DIRS = {".git", "scripts"}
TOKEN_SOFT_LIMIT = 110
TOKEN_HARD_LIMIT = 120
TOKEN_ENCODING = "cl100k_base"
SKILL_MD_SOFT_TOKEN_LIMIT = 4500
SKILL_MD_HARD_TOKEN_LIMIT = 5001
_TOKEN_ENCODER = None

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


def _frontmatter_block(text: str) -> str | None:
    m = FM_RE.match(text)
    return None if not m else m.group(1)


def _frontmatter_needs_quotes_for_colons(block: str) -> list[str]:
    """
    Codex's skill loader expects strict YAML.

    YAML "plain scalars" become ambiguous/invalid if they contain `: ` (colon + space) unquoted:
      description: Foo: bar

    This is the root cause of several "invalid YAML: mapping values are not allowed in this context"
    failures when loading skills.
    """
    issues: list[str] = []
    for line in block.splitlines():
        mm = KV_RE.match(line)
        if not mm:
            continue
        key = mm.group(1)
        raw_value = mm.group(2).strip()
        if not raw_value:
            continue
        if raw_value.startswith(("'", '"', "|", ">")):
            continue
        if ": " in raw_value:
            # Special-case description because it's the common failure mode.
            if key == "description":
                issues.append("description_requires_quotes_for_colons")
            else:
                issues.append(f"frontmatter_unquoted_colon:{key}")
    return issues


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


def _token_count(text: str) -> int:
    global _TOKEN_ENCODER
    if _TOKEN_ENCODER is None:
        if tiktoken is None:
            raise RuntimeError("tiktoken is required for token counting")
        _TOKEN_ENCODER = tiktoken.get_encoding(TOKEN_ENCODING)
    return len(_TOKEN_ENCODER.encode(text))


def scan_skill(dirpath: Path, *, token_checks: bool) -> tuple[list[str], list[str]]:
    skill_file = dirpath / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    fm = _parse_frontmatter(text)

    issues: list[str] = []
    warnings: list[str] = []
    name = fm.get("name", "").strip()
    desc = fm.get("description", "").strip()
    category = fm.get("category", "").strip()

    if not fm:
        issues.append("missing_frontmatter")
    else:
        block = _frontmatter_block(text)
        if block:
            issues.extend(_frontmatter_needs_quotes_for_colons(block))
    if not name:
        issues.append("missing_name_in_frontmatter")
    if not desc:
        issues.append("missing_description_in_frontmatter")
    if not category:
        issues.append("missing_category_in_frontmatter")

    if len(lines) > 200:
        issues.append(f"entry_over_200_lines:{len(lines)}")

    if name and name != dirpath.name:
        issues.append(f"name_folder_mismatch:{name}!={dirpath.name}")

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

    if token_checks and (name or desc):
        token_count = _token_count(f"{name} {desc}".strip())
        if token_count > TOKEN_HARD_LIMIT:
            issues.append(f"frontmatter_tokens_over_hard_limit:{token_count}")
        elif token_count > TOKEN_SOFT_LIMIT:
            warnings.append(f"frontmatter_tokens_over_soft_limit:{token_count}")

    if token_checks:
        skill_tokens = _token_count(text)
        if skill_tokens > SKILL_MD_HARD_TOKEN_LIMIT:
            issues.append(f"skill_md_tokens_over_hard_limit:{skill_tokens}")
        elif skill_tokens > SKILL_MD_SOFT_TOKEN_LIMIT:
            warnings.append(f"skill_md_tokens_over_soft_limit:{skill_tokens}")

    return issues, warnings


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="audit-skills",
        description="Repo-wide skill quality/performance audit.",
    )
    parser.add_argument(
        "--no-token-checks",
        action="store_true",
        help="Skip token checks even if tiktoken is available.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    token_checks = not args.no_token_checks
    if token_checks and tiktoken is None:
        msg = (
            "error: tiktoken is required for token checks.\n"
            "Install dependencies:\n"
            "  python3 -m pip install -r scripts/requirements-audit.txt\n"
            "Or run with --no-token-checks to skip token-based checks."
        )
        print(msg, file=sys.stderr)
        return 2
    skills: list[tuple[str, list[str], list[str]]] = []
    if not SKILLS_ROOT.is_dir():
        print("error: skills/ folder not found")
        return 1
    for entry in sorted(SKILLS_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name in SKIP_DIRS:
            continue
        if not (entry / "SKILL.md").is_file():
            continue
        issues, warnings = scan_skill(entry, token_checks=token_checks)
        skills.append((entry.name, issues, warnings))

    bad = [(name, issues) for name, issues, _ in skills if issues]
    warn = [(name, warnings) for name, _, warnings in skills if warnings]

    print(f"skills: {len(skills)}")
    print(f"skills_with_issues: {len(bad)}")
    print(f"skills_with_warnings: {len(warn)}")
    if not bad:
        if warn:
            for name, warnings in warn:
                print(f"- {name}: {warnings}")
        return 0

    for name, issues in bad:
        print(f"- {name}: {issues}")
    if warn:
        for name, warnings in warn:
            print(f"- {name}: {warnings}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
