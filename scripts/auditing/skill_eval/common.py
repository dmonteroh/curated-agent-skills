"""Shared contract for the skill_eval package.

Every module in this package builds against the types and helpers here. Keep
this file stdlib-only and free of side effects on import: tests import it
directly, and the vendor, integrity, activation, and judge modules all depend
on it.

Contract owner: the controller that wrote DESIGN.md. Workers read it and never
change it; a missing helper is a QUESTIONS return, not an edit.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Iterable, Iterator

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PACKAGE_DIR = Path(__file__).resolve().parent
AUDITING_DIR = PACKAGE_DIR.parent
REPO_ROOT = AUDITING_DIR.parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
TRIGGER_CASES_DIR = AUDITING_DIR / "trigger-cases"
# Sealed evaluation material and the holdout ledger are tracked in git so they
# cannot be lost with tmp/. Sealed payloads are encoded so that grep, glob, and
# casual reads by an authoring agent never surface the plaintext.
SEALED_DIR = AUDITING_DIR / "sealed"
HOLDOUT_LEDGER = SEALED_DIR / "holdout-ledger.jsonl"
# Arm homes and working directories live outside the repository, so no arm
# boots under this repo's CLAUDE.md/AGENTS.md or its .agent/ node.
SCRATCH_ROOT = Path(os.environ.get("SKILL_EVAL_SCRATCH", "/tmp/skill-eval"))
# Run output carries prompts, grades, judge reasons, and full traces, so it
# stays outside the repository (where an authoring agent could grep it) and
# outside SCRATCH_ROOT (where every shell-capable arm already browses). Under
# the real home, an arm that reads it by absolute path is caught as an
# outside-read. Point SKILL_EVAL_RUNS_DIR somewhere durable to keep runs
# across a container rebuild.
RUNS_DIR = Path(os.environ.get("SKILL_EVAL_RUNS_DIR",
                               Path.home() / ".cache" / "skill-eval" / "runs"))

VENDORS = ("claude", "codex")

# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class Case:
    """One activation probe. `expect` is True when the skill should load."""

    skill: str
    prompt: str
    expect: bool
    tags: list[str] = dataclasses.field(default_factory=list)
    source: str = ""
    id: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            self.id = case_id(self.skill, self.prompt)

    @property
    def polarity(self) -> str:
        return "positive" if self.expect else "negative"


@dataclasses.dataclass
class TraceRecord:
    """One agent run, normalised across vendors (see trace.py)."""

    vendor: str
    model: str = ""
    ok: bool = True
    error: str = ""
    # Skills that loaded, in first-activation order, without duplicates.
    activated: list[str] = dataclasses.field(default_factory=list)
    # skill name -> signal kind: skill_tool | file_read | command_read
    activation_signals: dict[str, str] = dataclasses.field(default_factory=dict)
    # Skills the agent could see at start-up (claude init event); None when the
    # vendor does not report them.
    visible_skills: list[str] | None = None
    # Tools the agent could see at start-up (claude init event); None otherwise.
    visible_tools: list[str] | None = None
    # Absolute paths the agent referenced (tool inputs, shell commands) outside
    # its own home and cwd; empty when parse_trace was given no roots.
    outside_reads: list[str] = dataclasses.field(default_factory=list)
    files_read: list[str] = dataclasses.field(default_factory=list)
    # Tool invocations the agent actually made; Claude's StructuredOutput
    # call, which is how --json-schema returns its answer, is not counted.
    tool_calls: int = 0
    # Executions of a file under a skill's scripts/ directory, as
    # "skills/<name>/scripts/<path>", one entry per run, whatever the exit
    # code: a gate that reports violations still ran (trace.script_runs_in).
    script_runs: list[str] = dataclasses.field(default_factory=list)
    text: str = ""
    cost_usd: float | None = None  # claude only; never converted
    tokens: dict | None = None     # codex only; never converted
    trace_path: str = ""

    @property
    def first_activated(self) -> str | None:
        return self.activated[0] if self.activated else None


@dataclasses.dataclass
class Finding:
    """A contamination, isolation, or corpus-quality finding."""

    severity: str  # "error" blocks a run; "warn" is reported; "info" is context
    code: str      # stable kebab-case identifier, e.g. "instruction-file-in-cwd"
    message: str
    path: str = ""


def to_json(obj) -> str:
    """Serialise a record (dataclass, list, or dict) as one JSON line."""
    if dataclasses.is_dataclass(obj):
        obj = dataclasses.asdict(obj)
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def write_jsonl(path: Path, records: Iterable) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(to_json(r) + "\n")


def append_jsonl(path: Path, record) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(to_json(record) + "\n")


def read_jsonl(path: Path) -> Iterator[dict]:
    if not path.exists():
        return
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


# ---------------------------------------------------------------------------
# Identity and hashing
# ---------------------------------------------------------------------------


def normalise_prompt(prompt: str) -> str:
    return " ".join(prompt.split()).strip()


def case_id(skill: str, prompt: str) -> str:
    """Stable id: survives reordering and whitespace edits, changes with wording."""
    h = hashlib.sha256(f"{skill}\x00{normalise_prompt(prompt)}".encode()).hexdigest()
    return h[:12]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_id(label: str = "") -> str:
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    salt = hashlib.sha256(os.urandom(8)).hexdigest()[:6]
    return f"{stamp}-{label}-{salt}" if label else f"{stamp}-{salt}"


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Train / holdout split
# ---------------------------------------------------------------------------

# Chosen default, not a measured threshold: skill-creator's run_loop.py holds
# out 40%; this package holds out a third so small corpora keep a train set.
DEFAULT_HOLDOUT_FRACTION = 1 / 3


def split_key(case: Case) -> str:
    """The id a case is split by: a paraphrase follows its parent's split."""
    for tag in case.tags:
        if tag.startswith("paraphrase-of:"):
            return tag.split(":", 1)[1]
    return case.id


def split_of(case: Case, fraction: float = DEFAULT_HOLDOUT_FRACTION,
             salt: str = "skill-eval") -> str:
    """Per-case assignment by salted hash, independent of every other case.

    Adding, removing, or editing one case never moves another, which a
    rank-based split cannot promise. The cost is that the holdout share is
    only approximately `fraction` on small corpora.
    """
    h = int(hashlib.sha256(f"{salt}:{split_key(case)}".encode()).hexdigest(), 16)
    return "holdout" if h / 2 ** 256 < fraction else "train"


def split_cases(cases: list[Case], fraction: float = DEFAULT_HOLDOUT_FRACTION,
                salt: str = "skill-eval") -> dict[str, list[Case]]:
    """Split visible cases into train and dev ("holdout" key kept for callers).

    Cases in trigger-cases/ are plaintext in the tree, so an authoring agent
    can read every one of them: a split of them is a dev set, useful against
    tuning noise but not against deliberate or accidental fitting. The real
    holdout is a sealed set (integrity.py), which never enters this split.
    """
    out: dict[str, list[Case]] = {"train": [], "holdout": []}
    for c in cases:
        out[split_of(c, fraction, salt)].append(c)
    return out


# ---------------------------------------------------------------------------
# Holdout ledger: every holdout evaluation consumes it a little
# ---------------------------------------------------------------------------

# Chosen default. Each distinct description measured on the holdout set leaks
# information about it; after this many, the holdout is a second train set.
HOLDOUT_LOOK_BUDGET = 3


def record_holdout_look(skill: str, description_sha: str, run: str,
                        ledger: Path = HOLDOUT_LEDGER) -> None:
    append_jsonl(ledger, {"skill": skill, "description_sha": description_sha,
                          "run_id": run, "at": utc_now()})


def holdout_looks(skill: str, ledger: Path = HOLDOUT_LEDGER) -> list[str]:
    """Distinct description hashes already measured on this skill's holdout."""
    seen: list[str] = []
    for row in read_jsonl(ledger):
        if row.get("skill") == skill and row.get("description_sha") not in seen:
            seen.append(row["description_sha"])
    return seen


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval; (0.0, 1.0) when n is zero."""
    if n <= 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def rate(successes: int, n: int) -> float | None:
    return successes / n if n else None


# ---------------------------------------------------------------------------
# Text: tokens and n-grams, shared by echo scoring and leak scanning
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[a-z0-9]+(?:['\-][a-z0-9]+)*")

STOPWORDS = frozenset(
    """a an and are as at be but by can do does for from has have how i if in
    into is it its me my no not of on or our so than that the their them then
    there these they this to up us was we were what when where which who why
    will with you your""".split()
)


def tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def content_words(text: str) -> list[str]:
    return [w for w in tokenize(text) if w not in STOPWORDS and len(w) > 1]


def ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)} if n > 0 else set()


def longest_common_run(a: list[str], b: list[str]) -> int:
    """Length of the longest shared contiguous token run between a and b."""
    if not a or not b:
        return 0
    best = 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        ai = a[i - 1]
        for j in range(1, len(b) + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


# ---------------------------------------------------------------------------
# Skill frontmatter
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    """Top-level scalar keys only (name, description). Enough for this package."""
    text = Path(skill_md).read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip()
        if val in (">", ">-", "|", "|-"):
            raise ValueError(f"{skill_md}: block-scalar {key.strip()} is not supported; use a quoted string")
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = json.loads(val) if val[0] == '"' else val[1:-1]
        out[key.strip()] = val
    return out


def replace_description(skill_md_text: str, description: str) -> str:
    """Return SKILL.md text with the frontmatter description swapped.

    The new value is written as a JSON string, which is valid YAML. Raises
    ValueError when no top-level description line exists, so a variant can
    never silently run with the original description.
    """
    m = _FM_RE.match(skill_md_text)
    if not m:
        raise ValueError("SKILL.md has no frontmatter")
    lines = m.group(1).splitlines()
    for i, line in enumerate(lines):
        if line.startswith("description:"):
            lines[i] = "description: " + json.dumps(description, ensure_ascii=False)
            # drop YAML continuation lines of a folded/multi-line value
            j = i + 1
            while j < len(lines) and lines[j][:1].isspace():
                j += 1
            del lines[i + 1:j]
            fm = "\n".join(lines)
            return f"---\n{fm}\n---\n" + skill_md_text[m.end():]
    raise ValueError("SKILL.md frontmatter has no description line")


def skill_dir(name: str) -> Path:
    return SKILLS_DIR / name


def library_skills() -> list[str]:
    return sorted(p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md"))
