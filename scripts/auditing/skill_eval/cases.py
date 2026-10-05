"""cases.py: static corpus quality linting for scripts/auditing/trigger-cases/.

Contract: DESIGN.md section 3, "cases.py" (task T2). This module never runs
an agent, opens the network, or shells out in its shipped code path; the
`git show` commands cited below for template-residue provenance were run
once, by hand, during research and are not part of this module.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import re
from pathlib import Path

from .common import (
    Case,
    Finding,
    SKILLS_DIR,
    TRIGGER_CASES_DIR,
    content_words,
    library_skills,
    longest_common_run,
    normalise_prompt,
    read_frontmatter,
)

# ---------------------------------------------------------------------------
# Thresholds. Every one below is either a chosen default (labelled) or cites
# where it was measured. None of them are tuned to make the current corpus
# pass -- the whole corpus is expected to fail several of these checks, and
# that is the finding, not a bug in the thresholds.
# ---------------------------------------------------------------------------

# Chosen default: DESIGN.md section 3 names "5 positive and 5 negative,
# overridable" as the floor below which the corpus cannot measure sensitivity
# or specificity meaningfully.
MIN_POSITIVE = 5
MIN_NEGATIVE = 5

# Chosen default, picked by measured hit rate on the current corpus (289
# negatives across 96 skills, one-off analysis during T2's build, not a
# shipped script): a negative counts as a near-miss confuser when it shares
# at least this many content words with the skill's description.
#   k=1 flags 172/289 negatives (59.5%) -- "shares any topic word" is not a
#       meaningful confuser test, it is almost every negative.
#   k=2 flags  53/289 negatives (18.3%) -- a plausible minority: negatives
#       that genuinely brush the skill's topic without triggering it.
#   k=3 flags  11/289 negatives ( 3.8%) -- too strict for a corpus this
#       sparse; would call almost every file "no near-miss" regardless of
#       intent.
# k=2 is the chosen default.
NEAR_MISS_OVERLAP_K = 2

# Chosen default, named directly in DESIGN.md section 3: a positive that
# shares a run of 4 or more content words with the description is echoing
# the description's wording rather than probing a realistic prompt.
HIGH_ECHO_RUN = 4

# Chosen default for the off-register heuristic's "short" leg (DESIGN.md:
# "tagged, or detected as short, lowercase, and without sentence
# punctuation"). Measured on the current corpus: 0 of 468 positives are
# flagged by the full heuristic (short + lowercase + no terminal punctuation)
# at any word-count threshold from 4 to 10, so the current corpus does not
# constrain this number -- it is picked for plausibility, not fit.
OFF_REGISTER_MAX_WORDS = 6

# Chosen default: two prompts of the same polarity in the same file are
# near-duplicates when their content-word Jaccard similarity is at or above
# this, and they are not already an exact (whitespace-normalised) duplicate.
NEAR_DUP_JACCARD = 0.8

# Template residue markers, derived from the generator removed in commit
# 1358f47's parent, "refactor(auditing): remove sanitizer and trigger-test
# pipeline from review runner" (scripts/auditing/run_parallel_skill_reviews.sh
# as it stood there).
# `run_trigger_case_generation`'s embedded `to_prompt()` wrapped each
# `## Use this skill when` / `## Do not use this skill when` bullet as:
#   positive: f"I need help with this: {s}. Can you guide me?"
#   negative: f"Please do this exactly now: {s}. No planning, just
#              implementation."
# and fell back to two fixed sentences when a skill had no bullets under
# that heading:
#   positive fallback: "I need help deciding an approach for an ambiguous
#     task."
#   negative fallback: "Implement this exact feature now; requirements are
#     final and no design/exploration is needed."
# Measured on the current corpus: 48 of 96 skill files still contain at
# least one of these markers verbatim.
TEMPLATE_RESIDUE_MARKERS = (
    "I need help with this:",
    "Can you guide me?",
    "Please do this exactly now:",
    "No planning, just implementation.",
    "I need help deciding an approach for an ambiguous task.",
    "Implement this exact feature now; requirements are final and no design/exploration is needed.",
)

# ---------------------------------------------------------------------------
# Parsing: tolerant of the real corpus's format variations. A file that
# cannot be parsed cleanly never raises -- every failure becomes a Finding
# and parsing continues with whatever it could recover.
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^#{1,6}\s*(.+?)\s*$")
_PROMPT_DOUBLE_RE = re.compile(r'^-\s*prompt:\s*"((?:[^"\\]|\\.)*)"\s*$')
_PROMPT_SINGLE_RE = re.compile(r"^-\s*prompt:\s*'((?:[^'\\]|\\.)*)'\s*$")
_PROMPT_BARE_RE = re.compile(r"^-\s*prompt:\s*(.+?)\s*$")
_EXPECT_RE = re.compile(r"^expect_activate:\s*(\S+)\s*$", re.I)
_TAGS_RE = re.compile(r"^tags:\s*\[(.*)\]\s*$", re.I)


def _unescape(text: str) -> str:
    return text.replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\")


def _parse_file(skill: str, path: Path) -> tuple[list[Case], list[Finding]]:
    """Parse one trigger-case file. Never raises; returns (cases, findings)."""
    if not path.exists():
        return [], [Finding("error", "missing-corpus-file",
                             f"{skill}: no trigger-case file at {path}", str(path))]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], [Finding("error", "unreadable-corpus-file",
                             f"{skill}: {exc}", str(path))]

    cases: list[Case] = []
    findings: list[Finding] = []
    section: bool | None = None  # True = positive section, False = negative, None = preamble
    pending: dict | None = None

    def flush() -> None:
        nonlocal pending
        if pending is None:
            return
        prompt = pending.get("prompt", "")
        line = pending["line"]
        if not prompt:
            findings.append(Finding("error", "unparsable-case",
                                     f"{skill}: case block at line {line} has no readable prompt text",
                                     str(path)))
            pending = None
            return
        explicit_expect = pending.get("expect")
        expect = explicit_expect
        if expect is None:
            if section is None:
                findings.append(Finding("error", "case-outside-section",
                                         f"{skill}: prompt at line {line} is not under a "
                                         "Positive/Negative heading",
                                         str(path)))
                pending = None
                return
            findings.append(Finding("warn", "missing-expect-activate",
                                     f"{skill}: case at line {line} has no expect_activate line; "
                                     "polarity inferred from its section heading",
                                     str(path)))
            expect = section
        elif section is not None and expect != section:
            # expect_activate is the source of truth for Case.expect (kept as
            # explicit_expect above); a mismatch against the section heading
            # is a smell in the file's organisation, not a parsing error.
            findings.append(Finding("warn", "expect-contradicts-section",
                                     f"{skill}: case at line {line} has expect_activate: "
                                     f"{'yes' if expect else 'no'} under a "
                                     f"{'Positive' if section else 'Negative'} heading",
                                     str(path)))
        cases.append(Case(skill=skill, prompt=prompt, expect=expect,
                           tags=pending.get("tags", []), source=str(path)))
        pending = None

    for lineno, raw in enumerate(text.splitlines(), start=1):
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            flush()
            m = _HEADING_RE.match(s)
            title = m.group(1).lower() if m else ""
            if "positive" in title:
                section = True
            elif "negative" in title:
                section = False
            # any other heading (e.g. the H1 title) leaves section as-is
            continue
        if s.startswith("- prompt:"):
            flush()
            m = _PROMPT_DOUBLE_RE.match(s) or _PROMPT_SINGLE_RE.match(s)
            if m:
                prompt = _unescape(m.group(1))
            else:
                m2 = _PROMPT_BARE_RE.match(s)
                prompt = m2.group(1).strip("\"'") if m2 else ""
                if not prompt:
                    findings.append(Finding("error", "unparsable-prompt-line",
                                             f"{skill}: line {lineno} looks like a prompt but could "
                                             f"not be parsed: {s!r}",
                                             str(path)))
            pending = {"prompt": prompt, "line": lineno}
            continue
        if pending is not None and s.lower().startswith("expect_activate:"):
            m = _EXPECT_RE.match(s)
            val = m.group(1).lower() if m else ""
            if val in ("yes", "true"):
                pending["expect"] = True
            elif val in ("no", "false"):
                pending["expect"] = False
            else:
                findings.append(Finding("error", "bad-expect-activate",
                                         f"{skill}: line {lineno}: expect_activate value {val!r} is "
                                         "neither yes nor no",
                                         str(path)))
            continue
        if pending is not None and s.lower().startswith("tags:"):
            m = _TAGS_RE.match(s)
            if m:
                pending["tags"] = [t.strip().strip("\"'") for t in m.group(1).split(",") if t.strip()]
            else:
                findings.append(Finding("warn", "unparsable-tags-line",
                                         f"{skill}: line {lineno}: tags line could not be parsed: {s!r}",
                                         str(path)))
            continue
        if s.startswith("- ") and pending is None:
            findings.append(Finding("warn", "unrecognised-list-item",
                                     f"{skill}: line {lineno}: unrecognised list item outside a "
                                     f"case block: {s!r}",
                                     str(path)))
    flush()
    return cases, findings


def load_cases(skill: str, path: Path | None = None) -> list[Case]:
    """Parse `skill`'s trigger-case file. Never raises; unparsable blocks are
    simply dropped (see `parse_findings` to see what was dropped and why)."""
    p = path if path is not None else TRIGGER_CASES_DIR / f"{skill}.md"
    cases, _ = _parse_file(skill, p)
    return cases


def parse_findings(skill: str, path: Path | None = None) -> list[Finding]:
    """Findings recorded while parsing `skill`'s trigger-case file."""
    p = path if path is not None else TRIGGER_CASES_DIR / f"{skill}.md"
    _, findings = _parse_file(skill, p)
    return findings


# ---------------------------------------------------------------------------
# Echo scoring: public, also used by judge.py generate to filter candidates.
# ---------------------------------------------------------------------------


def echo_score(prompt: str, description: str) -> float:
    """Content-word overlap between prompt and description, normalised to
    the prompt's distinct content words. 0.0 when the prompt has none."""
    p = set(content_words(prompt))
    if not p:
        return 0.0
    d = set(content_words(description))
    return len(p & d) / len(p)


def longest_echo(prompt: str, description: str) -> int:
    """Longest contiguous run of content words shared between prompt and
    description (order-sensitive, unlike `echo_score`)."""
    return longest_common_run(content_words(prompt), content_words(description))


# ---------------------------------------------------------------------------
# Per-case heuristics shared by lint() and stats()
# ---------------------------------------------------------------------------


def _residue_hits(prompt: str) -> list[str]:
    return [m for m in TEMPLATE_RESIDUE_MARKERS if m in prompt]


def _is_near_miss(case: Case, description: str) -> bool:
    if "near-miss" in case.tags:
        return True
    overlap = len(set(content_words(case.prompt)) & set(content_words(description)))
    return overlap >= NEAR_MISS_OVERLAP_K


def _is_off_register(case: Case) -> bool:
    if "off-register" in case.tags:
        return True
    prompt = case.prompt.strip()
    words = prompt.split()
    if len(words) >= OFF_REGISTER_MAX_WORDS:
        return False
    if prompt != prompt.lower():
        return False
    if re.search(r"[.!?]\s*$", prompt):
        return False
    return True


def _skill_description(skill: str) -> str:
    skill_md = SKILLS_DIR / skill / "SKILL.md"
    if not skill_md.exists():
        return ""
    return read_frontmatter(skill_md).get("description", "")


# ---------------------------------------------------------------------------
# lint(): single-skill checks
# ---------------------------------------------------------------------------


def lint(skill: str, *, min_pos: int = MIN_POSITIVE, min_neg: int = MIN_NEGATIVE,
          path: Path | None = None, description: str | None = None) -> list[Finding]:
    """Static findings for one skill's trigger-case file.

    `path` and `description` let callers (tests, and `judge.py generate`
    indirectly through `echo_score`) point at a fixture instead of the real
    corpus and library; both default to the real locations.
    """
    p = path if path is not None else TRIGGER_CASES_DIR / f"{skill}.md"
    cases, findings = _parse_file(skill, p)
    findings = list(findings)

    positives = [c for c in cases if c.expect]
    negatives = [c for c in cases if not c.expect]

    # Floor. A corpus-quality shortfall severe enough that measurement over
    # it is not meaningful: error.
    if not negatives:
        findings.append(Finding("error", "no-negative-cases",
                                 f"{skill}: zero negative cases; specificity cannot be measured at all",
                                 str(p)))
    elif len(negatives) < min_neg:
        findings.append(Finding("error", "below-floor-negative",
                                 f"{skill}: {len(negatives)} negative cases, floor is {min_neg}",
                                 str(p)))
    if len(positives) < min_pos:
        findings.append(Finding("error", "below-floor-positive",
                                 f"{skill}: {len(positives)} positive cases, floor is {min_pos}",
                                 str(p)))

    description = description if description is not None else _skill_description(skill)

    # Template residue: the corpus still carries the removed generator's
    # boilerplate instead of a real prompt. Measurement over these cases
    # tests the generator's fixed phrasing, not the skill's description, so
    # this is a corpus-quality shortfall: error.
    for c in cases:
        hits = _residue_hits(c.prompt)
        if hits:
            findings.append(Finding("error", "template-residue",
                                     f"{skill}: case still carries the removed generator's template "
                                     f"wording ({', '.join(hits)}): {c.prompt!r}",
                                     str(p)))

    # No near-miss negative: heuristically detected (or tagged), so a false
    # negative here is possible. Weakens the corpus without making it
    # meaningless: warn.
    if negatives and not any(_is_near_miss(c, description) for c in negatives):
        findings.append(Finding("warn", "no-near-miss-negative",
                                 f"{skill}: no negative case is tagged near-miss or shares "
                                 f">= {NEAR_MISS_OVERLAP_K} content words with the description; "
                                 "specificity is untested against a plausible confuser",
                                 str(p)))

    # No off-register positive: parallel to no-near-miss-negative. A positive
    # that reads as a keyword fragment rather than a realistic prompt (tagged,
    # or detected as short, lowercase, and unpunctuated) probes register
    # variation. A corpus with none of them never tests that. Heuristic: warn.
    if positives and not any(_is_off_register(c) for c in positives):
        findings.append(Finding("warn", "no-off-register-positive",
                                 f"{skill}: no positive case is tagged off-register or reads as a "
                                 "short, lowercase keyword fragment; register variation against a "
                                 "terse or informal phrasing is untested",
                                 str(p)))

    # High echo: inflates measured activation by testing vocabulary overlap
    # instead of intent recognition. Heuristic (a run-length threshold): warn.
    for c in positives:
        run = longest_echo(c.prompt, description)
        if run >= HIGH_ECHO_RUN:
            findings.append(Finding("warn", "high-echo-positive",
                                     f"{skill}: positive case echoes a run of {run} content words "
                                     f"from the description (threshold {HIGH_ECHO_RUN}): {c.prompt!r}",
                                     str(p)))

    # Duplicate / near-duplicate prompts within this file: warn.
    seen: dict[str, Case] = {}
    for c in cases:
        norm = normalise_prompt(c.prompt)
        if norm in seen:
            findings.append(Finding("warn", "duplicate-prompt",
                                     f"{skill}: duplicate prompt (case {c.id} repeats case "
                                     f"{seen[norm].id})",
                                     str(p)))
        else:
            seen[norm] = c
    for group in (positives, negatives):
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                if normalise_prompt(a.prompt) == normalise_prompt(b.prompt):
                    continue  # already reported as an exact duplicate above
                wa, wb = set(content_words(a.prompt)), set(content_words(b.prompt))
                if not wa or not wb:
                    continue
                jac = len(wa & wb) / len(wa | wb)
                if jac >= NEAR_DUP_JACCARD:
                    findings.append(Finding("warn", "near-duplicate-prompt",
                                             f"{skill}: cases {a.id} and {b.id} are near-duplicates "
                                             f"(jaccard={jac:.2f})",
                                             str(p)))

    return findings


# ---------------------------------------------------------------------------
# lint_all(): adds cross-skill collision checks
# ---------------------------------------------------------------------------


def lint_all(skills: list[str] | None = None, *, min_pos: int = MIN_POSITIVE,
             min_neg: int = MIN_NEGATIVE,
             cases_dir: Path | None = None) -> dict[str, list[Finding]]:
    """Per-skill findings, `lint()` plus cross-skill collisions.

    Same normalised prompt marked positive for two or more skills: warn,
    a real corpus ambiguity two skills both claim. Same normalised prompt
    positive for one skill and negative for another: info, a useful
    competitive probe by design (DESIGN.md section 3).

    `cases_dir` overrides where each skill's `<skill>.md` is read from
    (default `TRIGGER_CASES_DIR`); tests use it to point at fixtures without
    touching the real corpus.
    """
    names = skills if skills is not None else library_skills()
    base_dir = cases_dir if cases_dir is not None else TRIGGER_CASES_DIR
    results: dict[str, list[Finding]] = {}
    prompt_index: dict[str, dict[str, bool]] = {}

    for skill in names:
        p = base_dir / f"{skill}.md"
        results[skill] = lint(skill, min_pos=min_pos, min_neg=min_neg, path=p)
        for c in load_cases(skill, path=p):
            norm = normalise_prompt(c.prompt)
            prompt_index.setdefault(norm, {})[skill] = c.expect

    for norm, by_skill in prompt_index.items():
        if len(by_skill) < 2:
            continue
        positives = sorted(s for s, e in by_skill.items() if e)
        negatives = sorted(s for s, e in by_skill.items() if not e)
        if len(positives) >= 2:
            f = Finding("warn", "cross-skill-positive-collision",
                        f"prompt marked positive for {len(positives)} skills "
                        f"({', '.join(positives)}): {norm!r}")
            for s in positives:
                results[s].append(f)
        if positives and negatives:
            f = Finding("info", "cross-skill-competitive-probe",
                        f"prompt is positive for {positives} and negative for {negatives}: {norm!r}")
            for s in positives + negatives:
                results[s].append(f)

    return results


# ---------------------------------------------------------------------------
# stats(): per-skill counts
# ---------------------------------------------------------------------------


def stats(skills: list[str] | None = None) -> dict[str, dict]:
    names = skills if skills is not None else library_skills()
    out: dict[str, dict] = {}
    for skill in names:
        cases = load_cases(skill)
        positives = [c for c in cases if c.expect]
        negatives = [c for c in cases if not c.expect]
        description = _skill_description(skill)
        out[skill] = {
            "positive": len(positives),
            "negative": len(negatives),
            "tagged": sum(1 for c in cases if c.tags),
            "near_miss": sum(1 for c in negatives if _is_near_miss(c, description)),
            "off_register": sum(1 for c in positives if _is_off_register(c)),
            "residue": sum(1 for c in cases if _residue_hits(c.prompt)),
            "max_echo": max((longest_echo(c.prompt, description) for c in positives), default=0),
        }
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_SEVERITY_RANK = {"error": 0, "warn": 1, "info": 2}


def _print_lint_table(results: dict[str, list[Finding]]) -> None:
    rows = [(skill, f.severity, f.code, f.message)
            for skill in sorted(results) for f in results[skill]]
    if not rows:
        print("cases lint: no findings")
        return
    rows.sort(key=lambda r: (_SEVERITY_RANK.get(r[1], 9), r[0], r[2]))
    w_skill = max(len(r[0]) for r in rows)
    w_sev = max(len(r[1]) for r in rows)
    w_code = max(len(r[2]) for r in rows)
    for skill, sev, code, msg in rows:
        print(f"{skill:<{w_skill}}  {sev:<{w_sev}}  {code:<{w_code}}  {msg}")
    counts = {}
    for _, sev, _, _ in rows:
        counts[sev] = counts.get(sev, 0) + 1
    print()
    print("totals: " + ", ".join(f"{sev}={counts.get(sev, 0)}" for sev in ("error", "warn", "info")))


def _cmd_lint(args: argparse.Namespace) -> int:
    skills = args.skill if args.skill else library_skills()
    results = lint_all(skills, min_pos=args.min_pos, min_neg=args.min_neg)
    if args.json:
        payload = {s: [dataclasses.asdict(f) for f in fs] for s, fs in results.items()}
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_lint_table(results)
    any_error = any(f.severity == "error" for fs in results.values() for f in fs)
    return 1 if any_error else 0


def _print_stats_table(data: dict[str, dict]) -> None:
    headers = ("skill", "pos", "neg", "tagged", "near_miss", "off_register", "residue", "max_echo")
    rows = [headers]
    for skill in sorted(data):
        d = data[skill]
        rows.append((skill, str(d["positive"]), str(d["negative"]), str(d["tagged"]),
                     str(d["near_miss"]), str(d["off_register"]), str(d["residue"]),
                     str(d["max_echo"])))
    widths = [max(len(r[i]) for r in rows) for i in range(len(headers))]
    for r in rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(r)))


def _cmd_stats(args: argparse.Namespace) -> int:
    skills = args.skill if args.skill else library_skills()
    data = stats(skills)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        _print_stats_table(data)
    return 0


def add_subparser(subparsers) -> None:
    parser = subparsers.add_parser("cases", help="lint the trigger-case corpus")
    sub = parser.add_subparsers(dest="cases_command", required=True)

    lint_p = sub.add_parser("lint", help="lint trigger-case files")
    lint_p.add_argument("--skill", action="append", default=[],
                        help="lint one skill (repeatable); default is the whole library")
    lint_p.add_argument("--all", action="store_true",
                        help="lint every skill in the library (default when --skill is omitted)")
    lint_p.add_argument("--json", action="store_true")
    lint_p.add_argument("--min-pos", type=int, default=MIN_POSITIVE, dest="min_pos")
    lint_p.add_argument("--min-neg", type=int, default=MIN_NEGATIVE, dest="min_neg")
    lint_p.set_defaults(func=_cmd_lint)

    stats_p = sub.add_parser("stats", help="per-skill trigger-case counts")
    stats_p.add_argument("--skill", action="append", default=[],
                         help="report one skill (repeatable); default is the whole library")
    stats_p.add_argument("--json", action="store_true")
    stats_p.set_defaults(func=_cmd_stats)
