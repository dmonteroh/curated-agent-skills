#!/usr/bin/env python3
from __future__ import annotations

"""
Repo-wide skill quality/performance audit.

Checks (intentionally lightweight; no PyYAML dependency).

Issues (fail the run):
- SKILL.md has YAML frontmatter with name + description + metadata.category
- Frontmatter uses only supported top-level keys: name, description, metadata
- Frontmatter values that include `: ` are quoted (Codex skill loader is strict YAML)
- Backticked local file references inside a skill resolve (for refs like `references/x.md`),
  scanned over SKILL.md plus its references/*.md and resources/*.md, one level deep
- Repo-root-style skill paths (`skills/<name>/...`), scanned over the same files, fenced
  code included. They do not resolve once the skill is installed to ~/.codex/skills/<name>/.
- No network assumptions in SKILL.md (skills should be usable offline)
- Frontmatter name matches folder name (avoid agent confusion)
- Name + description token budget (frontmatter) stays within bounds
- A SKILL.md, references/*.md, or resources/*.md file that cannot be read
  (broken symlink, non-UTF-8 content) is reported rather than aborting the scan

Warnings (reported, do not fail):
- Entry point (SKILL.md) over 200 lines. Length follows the job; see
  scripts/auditing/SKILL_REVIEW_CHECKLIST.md section 10.
- A section heading immediately restated by its own first sentence (sediment).
- Non-canonical spelling of a known heading family (lint, not a judgment call).
- Activation cues or trigger phrases inside SKILL.md; they belong in
  scripts/auditing/trigger-cases/<skill>.md.

Heading families here and section 5 of the checklist are a parity pair; see
scripts/auditing/OPEN_ITEMS.md.
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
KV_WITH_INDENT_RE = re.compile(r"^(\s*)([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$")
REQUIRED_TOP_LEVEL_FRONTMATTER_KEYS = {"name", "description", "metadata"}
ALLOWED_FRONTMATTER_KEYS = REQUIRED_TOP_LEVEL_FRONTMATTER_KEYS

# Parity pair with section 5 of scripts/auditing/SKILL_REVIEW_CHECKLIST.md.
CANONICAL_HEADINGS = {
    "workflow": "Workflow",
    "output contract": "Output contract",
    "required inputs": "Required inputs",
    "common pitfalls": "Common pitfalls",
    "decision points": "Decision points",
    "constraints": "Constraints",
    "examples": "Examples",
    "references": "References",
    "resources": "Resources",
    "scripts": "Scripts",
}
# Word-order and plural variants only. Synonyms (Instructions vs Workflow) are a
# reviewer's call, not a lint.
HEADING_ALIASES = {
    "common pitfalls to avoid": "common pitfalls",
    "inputs required": "required inputs",
    "example": "examples",
    "reference": "references",
    "resource": "resources",
    "script": "scripts",
}
HEADING_STOPWORDS = {"the", "a", "an", "of", "to", "for", "and"}

H2_RE = re.compile(r"^## +(.*)$")
TRAILING_PAREN_RE = re.compile(r"\([^)]*\)$")
REPO_ROOT_SKILL_PATH_RE = re.compile(
    r"(?<![\w./~-])(?:\.{1,2}/)?skills/[A-Za-z0-9][A-Za-z0-9_-]*/[\w./-]*?\.(?:md|sh|py|txt|cjs|ts|js)"
)
ACTIVATION_CUE_MARKER_RE = re.compile(r"^[#*\- ]*(activation cue|trigger phrase|trigger test)", re.I)
SKILL_INTERNAL_REF_PREFIXES = ("references/", "resources/", "scripts/", "assets/", "templates/")


def _heading_findings(lines: list[str]) -> tuple[list[str], list[str]]:
    """Split by how they get resolved.

    variants:   case, plural, word order — mechanical, one right answer.
    qualifiers: a known family carrying a parenthetical. Whether it scopes the
                section or is vacuous is the reviewer's call, so it is reported
                separately rather than auto-corrected.
    """
    variants: list[str] = []
    qualifiers: list[str] = []
    for line in lines:
        m = H2_RE.match(line)
        if not m:
            continue
        raw = m.group(1).strip()
        stripped = TRAILING_PAREN_RE.sub("", raw).strip()
        key = HEADING_ALIASES.get(stripped.lower(), stripped.lower())
        canonical = CANONICAL_HEADINGS.get(key)
        if not canonical:
            continue
        if stripped != canonical:
            variants.append(f"{stripped}->{canonical}")
        if stripped != raw:
            qualifiers.append(raw)
    return variants, qualifiers


def _activation_cues(lines: list[str]) -> list[str]:
    """Activation cues belong in scripts/auditing/trigger-cases/<skill>.md."""
    return [line.strip() for line in lines if ACTIVATION_CUE_MARKER_RE.match(line.strip())]


def _headings_restated(lines: list[str]) -> list[str]:
    """Headings whose own first sentence repeats them — template sediment."""
    out: list[str] = []
    for idx, line in enumerate(lines):
        m = H2_RE.match(line)
        if not m:
            continue
        heading = m.group(1).strip()
        base = TRAILING_PAREN_RE.sub("", heading).strip().lower()
        words = [w for w in re.findall(r"[a-z]+", base) if w not in HEADING_STOPWORDS]
        if len(words) < 2:
            continue
        nxt = _first_prose_line(lines, idx + 1)
        if nxt is None:
            continue
        following = re.findall(r"[a-z]+", nxt.lower())[:14]
        if all(w in following for w in words):
            out.append(heading)
    return out


def _first_prose_line(lines: list[str], start: int) -> str | None:
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", "|", "```", ">")):
            return None
        return stripped
    return None


def _parse_frontmatter(text: str) -> dict[str, str]:
    m = FM_RE.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    current_scalar_key: str | None = None
    current_map_key: str | None = None
    for line in m.group(1).splitlines():
        mm = KV_WITH_INDENT_RE.match(line)
        if mm:
            indent = len(mm.group(1))
            key = mm.group(2)
            val = mm.group(3).strip().strip("\"'")
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
        if current_scalar_key and (line.startswith(" ") or line.startswith("\t")):
            cont = line.strip()
            if cont:
                fm[current_scalar_key] = (fm.get(current_scalar_key, "") + " " + cont).strip()
            continue
        current_scalar_key = None
        if line and not line.startswith((" ", "\t")):
            current_map_key = None
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


def _frontmatter_keys(block: str) -> set[str]:
    keys: set[str] = set()
    for line in block.splitlines():
        mm = KV_RE.match(line)
        if not mm:
            continue
        keys.add(mm.group(1))
    return keys


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


def _skill_texts(dirpath: Path) -> tuple[list[tuple[str, str]], list[str]]:
    """(skill-relative POSIX path, text) for SKILL.md, then references/*.md, then resources/*.md.

    One level deep (checklist section 9): `glob`, not `rglob`. Any of these files that cannot
    be read (broken symlink, non-UTF-8 content) is reported in the second return value as
    `<rel_file>:<ExceptionType>` instead of raising, so one bad file never crashes the library
    scan. An unreadable `references/`/`resources/` file leaves the rest of the skill's checks
    intact; an unreadable `SKILL.md` leaves no text for the caller to check at all, so it is
    still reported here but the caller treats it as the skill's only finding.
    """
    pairs: list[tuple[str, str]] = []
    unreadable: list[str] = []
    try:
        pairs.append(("SKILL.md", (dirpath / "SKILL.md").read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError) as exc:
        unreadable.append(f"SKILL.md:{type(exc).__name__}")
    for sub in ("references", "resources"):
        subdir = dirpath / sub
        if not subdir.is_dir():
            continue
        for f in sorted(subdir.glob("*.md")):
            rel = f.relative_to(dirpath).as_posix()
            try:
                pairs.append((rel, f.read_text(encoding="utf-8")))
            except (OSError, UnicodeDecodeError) as exc:
                unreadable.append(f"{rel}:{type(exc).__name__}")
    return pairs, unreadable


def _repo_root_skill_paths(skill_texts: list[tuple[str, str]]) -> list[str]:
    found: set[str] = set()
    for rel_file, text in skill_texts:
        for m in REPO_ROOT_SKILL_PATH_RE.finditer(text):
            found.add(f"{rel_file}:{m.group(0)}")
    return sorted(found)


def _missing_local_refs(dirpath: Path, skill_texts: list[tuple[str, str]]) -> list[str]:
    missing: set[str] = set()
    for rel_file, text in skill_texts:
        for ref in _find_backtick_paths(text):
            if rel_file != "SKILL.md" and not ref.startswith(SKILL_INTERNAL_REF_PREFIXES):
                continue
            p = (dirpath / ref).resolve()
            try:
                p.relative_to(dirpath.resolve())
            except Exception:
                continue
            if not p.exists():
                missing.add(f"{rel_file}:{ref}")
    return sorted(missing)


def _token_count(text: str) -> int:
    global _TOKEN_ENCODER
    if _TOKEN_ENCODER is None:
        if tiktoken is None:
            raise RuntimeError("tiktoken is required for token counting")
        _TOKEN_ENCODER = tiktoken.get_encoding(TOKEN_ENCODING)
    return len(_TOKEN_ENCODER.encode(text))


def scan_skill(dirpath: Path, *, token_checks: bool) -> tuple[list[str], list[str]]:
    skill_texts, unreadable_texts = _skill_texts(dirpath)
    if not skill_texts or skill_texts[0][0] != "SKILL.md":
        return ["unreadable_skill_file:" + ",".join(sorted(unreadable_texts))], []
    text = skill_texts[0][1]
    lines = text.splitlines()
    fm = _parse_frontmatter(text)

    issues: list[str] = []
    warnings: list[str] = []
    if unreadable_texts:
        issues.append("unreadable_skill_file:" + ",".join(sorted(unreadable_texts)))
    name = fm.get("name", "").strip()
    desc = fm.get("description", "").strip()
    category = fm.get("metadata.category", "").strip()

    if not fm:
        issues.append("missing_frontmatter")
    else:
        block = _frontmatter_block(text)
        if block:
            issues.extend(_frontmatter_needs_quotes_for_colons(block))
            keys = _frontmatter_keys(block)
            missing_required = sorted(REQUIRED_TOP_LEVEL_FRONTMATTER_KEYS - keys)
            if missing_required:
                issues.append("missing_frontmatter_keys:" + ",".join(missing_required))
            extra = sorted(keys - ALLOWED_FRONTMATTER_KEYS)
            if extra:
                issues.append("unexpected_frontmatter_keys:" + ",".join(extra))
    if not name:
        issues.append("missing_name_in_frontmatter")
    if not desc:
        issues.append("missing_description_in_frontmatter")
    if not category:
        issues.append("missing_metadata_category_in_frontmatter")

    # Length follows the job; see SKILL_REVIEW_CHECKLIST.md section 10.
    if len(lines) > 200:
        warnings.append(f"entry_over_200_lines:{len(lines)}")

    if name and name != dirpath.name:
        issues.append(f"name_folder_mismatch:{name}!={dirpath.name}")

    # Repo-root paths break once the skill is installed to ~/.codex/skills/<name>/.
    # Scanned over SKILL.md plus references/resources, fenced code included.
    repo_root_paths = _repo_root_skill_paths(skill_texts)
    if repo_root_paths:
        issues.append("repo_root_skill_path:" + ",".join(repo_root_paths))

    variants, qualifiers = _heading_findings(lines)
    if variants:
        warnings.append("heading_variant:" + ",".join(variants))
    if qualifiers:
        warnings.append("heading_qualifier:" + ",".join(qualifiers))

    restated = _headings_restated(lines)
    if restated:
        warnings.append("heading_restated:" + ",".join(restated))

    cues = _activation_cues(lines)
    if cues:
        warnings.append(f"activation_cues_in_skill_md:{len(cues)}")

    missing = _missing_local_refs(dirpath, skill_texts)
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
