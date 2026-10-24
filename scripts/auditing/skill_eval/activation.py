"""activation.py: multi-vendor activation runner (task T3).

Design contract: DESIGN.md sec 2 (all three threats) and sec 3 "activation.py".
Measures, from traces, whether a skill's description makes it load: isolated
(only the target skill installed) or competitive (neighbours or the whole
library installed alongside it). Reports rates with repeats over a Wilson
interval, keeps train and holdout apart, guards the holdout with a ledger,
gives class-level (never per-prompt, for holdout) feedback, and ships a
self-test that proves it can fail (DESIGN.md T-C: "confirm a test can fail
before trusting it").

This module never imports the network or subprocess at import time. Every
live call goes through `vendors.exec_agent` / `vendors.build_home` /
`vendors.builtin_baseline` / `trace.parse_trace`, which tests stub out
entirely (see scripts/tests/test_skill_eval_activation.py).

Round 2 review fix: every call -- not just the run -- now builds, verifies,
and tears down its own home (DESIGN.md sec 2 T-A item "fresh home per
call"): a home reused across calls carries sync downloads and session state
from one call to the next, which is how the intermittent org-skill leak
happened, and made repeats dependent on each other.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import json
import os
import re
import shutil
import sys
import threading
from pathlib import Path
from typing import Iterable

from . import common
from .common import (
    Case,
    Finding,
    HOLDOUT_LOOK_BUDGET,
    RUNS_DIR,
    SCRATCH_ROOT,
    TraceRecord,
    library_skills,
    read_frontmatter,
    run_id,
    sha256_text,
    skill_dir,
    split_cases,
    wilson_interval,
)

SHAPES = ("isolated", "competitive")
# DESIGN.md sec 2 T-C: three case sets, never pooled except "visible" (train +
# dev, reported separately). "holdout" here means ONLY the sealed set,
# loaded through integrity.unseal(); it is never mixed with train/dev cases
# in one run. "dev" is common.split_cases()'s "holdout" key, renamed here
# because that key is the plaintext visible set, not the sealed one.
SPLITS = ("train", "dev", "holdout", "visible")

# Chosen default (DESIGN.md sec 3: "the writing-style campaign measured 3 as
# too few to rank close variants, where 4 trials across 5 probes was the
# floor"). 3 is the run default; `compare` warns below 4.
DEFAULT_REPEATS = 3
DEFAULT_CONCURRENCY = 4

# Chosen default, labelled: a vendor arm whose failure rate exceeds this
# fraction of its calls is flagged in the summary, loudly, rather than
# silently averaged away.
FAILURE_RATE_WARN = 0.2

# Chosen default, cited directly from DESIGN.md sec 3 / LEARNINGS.md sec 6:
# "4 trials across 5 probes is the floor for ranking close variants". compare()
# warns when either side of an A/B run has a valid n below this floor for a
# compared case (round 2 fix: valid n, never the planned --repeats, since a
# failed/contaminated call never produced a usable trial).
MIN_REPEATS_FOR_COMPARE = 4

# Chosen defaults for selftest()'s two thresholds (DESIGN.md sec 3, point 9).
SELFTEST_MIN_DROP = 0.5
SELFTEST_POSITIVE_CONTROL_MIN_RATE = 0.5

# The negative control's replacement description: fixed, unrelated to any
# skill in this library, so a description that "passes" against it is
# passing against noise, not against a plausible confuser. A module
# constant, never derived from the skill under test.
SELFTEST_UNRELATED_DESCRIPTION = (
    "Convert a numeric temperature value between Celsius, Fahrenheit, and "
    "Kelvin, given the value and its source unit. Use for unit-conversion "
    "arithmetic only."
)

# Round 2 finding 4: the negative control used to keep the skill's own name,
# so an agent could activate it on name-recognition alone even when the
# description said nothing relevant -- that makes the control fail
# spuriously (a false "the description discriminates" verdict) or pass
# spuriously (a name match that has nothing to do with the description under
# test). Installing the same body under this neutral name means only the
# description and name differ from the real skill, never the body.
SELFTEST_NEGATIVE_CONTROL_NAME = "unit-converter"

DEFAULT_TIMEOUT = 600

# Text a holdout trace file is scanned for and replaced (DESIGN.md sec 2 T-C
# item 1c): holdout traces and records carry no prompt text.
_HOLDOUT_REDACTION_MARKER = "[holdout prompt redacted]"

# Round 3 finding I3 (blocker): a holdout call's own `error` field can BE the
# model's reply (a claude is_error result's "error" text is the completion
# itself), so a literal-substring scrub against the known prompt is not
# enough -- the model can paraphrase. Any error on a holdout call is replaced
# outright; holdout failures are reported as counts only, never text.
_HOLDOUT_ERROR_REDACTION_MARKER = "[holdout error redacted]"

# Round 3 finding O1: the default fresh-cwd fixture. "git" measured (R3):
# the task prompt "Draft the PR description for this branch against main."
# activated 2/2 in the git fixture, 0/1 empty -- an empty cwd can itself
# suppress activation, which would be misread as a bad description.
DEFAULT_WORKSPACE = "git"


# ---------------------------------------------------------------------------
# Planning: pure, no side effects, no IO. Every input is already loaded.
# ---------------------------------------------------------------------------


def plan_run(*, skill: str, shape: str, installed_skills: list[str],
             vendors_models: dict[str, str], repeats: int, split: str,
             cases_by_split: dict[str, list[Case]], description_sha: str | None = None,
             description_file: str | None = None, case_ids: list[str] | None = None,
             limit: int | None = None, max_calls: int | None = None,
             max_cost_usd: float | None = None, max_codex_tokens: int | None = None,
             allow_holdout_reuse: bool = False,
             neighbors: list[str] | None = None, library: bool = False,
             workspace: str = DEFAULT_WORKSPACE) -> dict:
    """Build the whole call list (case x vendor/model x repeat).

    Pure: given already-loaded cases and already-resolved vendor/model pairs,
    this never touches the filesystem, network, or a subprocess. `--dry-run`
    is exactly "call this and print the result".
    """
    if shape not in SHAPES:
        raise ValueError(f"plan_run: unknown shape {shape!r}")
    if split not in SPLITS:
        raise ValueError(f"plan_run: unknown split {split!r}")
    if repeats < 1:
        raise ValueError("plan_run: repeats must be >= 1")
    if not vendors_models:
        raise ValueError("plan_run: at least one vendor is required")

    splits = ["train", "dev"] if split == "visible" else [split]
    case_id_filter = set(case_ids) if case_ids else None

    selected: list[tuple[str, Case]] = []
    for sp in splits:
        group = sorted(cases_by_split.get(sp, []), key=lambda c: c.id)
        if case_id_filter is not None:
            group = [c for c in group if c.id in case_id_filter]
        elif limit is not None:
            pos = [c for c in group if c.expect][:limit]
            neg = [c for c in group if not c.expect][:limit]
            group = pos + neg
        selected.extend((sp, c) for c in group)

    case_rows = [
        {"id": c.id, "skill": c.skill, "expect": c.expect, "polarity": c.polarity,
         "tags": list(c.tags), "split": sp}
        for sp, c in selected
    ]

    calls: list[dict] = []
    call_count_per_vendor = {v: 0 for v in vendors_models}
    for sp, c in selected:
        for vendor, model in vendors_models.items():
            for repeat in range(repeats):
                calls.append({
                    "case_id": c.id, "skill": c.skill, "split": sp,
                    "vendor": vendor, "model": model, "repeat": repeat,
                })
                call_count_per_vendor[vendor] += 1

    return {
        "skill": skill,
        "shape": shape,
        "neighbors": list(neighbors) if neighbors else [],
        "library": bool(library),
        "installed_skills": sorted(set(installed_skills)),
        "vendors": dict(vendors_models),
        "repeats": repeats,
        "split": split,
        "description_file": str(description_file) if description_file else None,
        "description_sha": description_sha,
        "workspace": workspace,
        "workspace_sha": None,  # filled in by the preflight check, once per run
        "allow_holdout_reuse": bool(allow_holdout_reuse),
        "max_calls": max_calls,
        "max_cost_usd": max_cost_usd,
        "max_codex_tokens": max_codex_tokens,
        "cases": case_rows,
        "calls": calls,
        "call_count_per_vendor": call_count_per_vendor,
        "call_count_total": len(calls),
    }


def _resolve_models(vendor_names: list[str], overrides: dict[str, str]) -> dict[str, str]:
    from . import vendors as vendors_mod
    out = {}
    for v in vendor_names:
        out[v] = overrides.get(v) or vendors_mod.DEFAULT_MODELS.get(v)
        if not out[v]:
            raise ValueError(f"no model resolved for vendor {v!r}")
    return out


def _parse_kv_list(raw: str) -> dict[str, str]:
    out = {}
    for part in (raw or "").split(","):
        part = part.strip()
        if not part:
            continue
        k, _, v = part.partition("=")
        if not v:
            raise ValueError(f"malformed --models entry {part!r}, expected vendor=model")
        out[k.strip()] = v.strip()
    return out


def _load_all_cases(skill: str, include_paraphrases: Path | None) -> list[Case]:
    from . import cases as cases_mod
    cases = list(cases_mod.load_cases(skill))
    if include_paraphrases is not None:
        seen = {c.id for c in cases}
        for c in cases_mod.load_cases(skill, path=Path(include_paraphrases)):
            if c.id not in seen:
                cases.append(c)
                seen.add(c.id)
    return cases


def _description_text(skill: str, description_file: Path | None) -> str:
    if description_file is not None:
        # Stripped like a frontmatter value, so the same text hashes the same
        # in both places and the holdout ledger counts it once.
        return Path(description_file).read_text(encoding="utf-8").strip()
    return read_frontmatter(skill_dir(skill) / "SKILL.md").get("description", "")


# ---------------------------------------------------------------------------
# Holdout ledger guard
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class HoldoutDecision:
    proceed: bool
    is_new_look: bool
    warning: str = ""
    refusal: str = ""


def check_holdout_budget(skill: str, description_sha: str, *, ledger: Path,
                          allow_reuse: bool, budget: int = HOLDOUT_LOOK_BUDGET) -> HoldoutDecision:
    existing = common.holdout_looks(skill, ledger=ledger)
    if description_sha in existing:
        return HoldoutDecision(proceed=True, is_new_look=False)
    new_count = len(existing) + 1
    if new_count > budget:
        if not allow_reuse:
            return HoldoutDecision(
                proceed=False, is_new_look=True,
                refusal=(f"holdout look budget exceeded for '{skill}': {new_count} distinct "
                         f"descriptions measured (budget {budget}); pass --allow-holdout-reuse "
                         "to override, on purpose"),
            )
        return HoldoutDecision(
            proceed=True, is_new_look=True,
            warning=(f"holdout look budget exceeded for '{skill}' ({new_count} > {budget}); "
                     "proceeding only because --allow-holdout-reuse was given"),
        )
    if new_count == budget:
        return HoldoutDecision(
            proceed=True, is_new_look=True,
            warning=(f"holdout look budget reached for '{skill}': this is look {new_count} "
                     f"of {budget}; the holdout is close to becoming a second train set"),
        )
    return HoldoutDecision(proceed=True, is_new_look=True)


def _resolve_holdout_ledger() -> Path:
    """Round 2 finding 3a: no CLI flag for this. Anyone who could point the
    runner at an empty ledger file could bypass the look budget outright.
    Tests override it only through this environment variable, never a flag
    the CLI itself exposes."""
    override = os.environ.get("SKILL_EVAL_HOLDOUT_LEDGER")
    return Path(override) if override else common.HOLDOUT_LEDGER


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def _known_skills_for(installed_skills: list[str]) -> set[str]:
    return set(installed_skills)


def _is_within(path: Path, root: Path) -> bool:
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except (ValueError, OSError):
        return False


_GLOB_CHARS = set("*?[")


def _is_unlistable_probe(path: str) -> bool:
    """A scratch path that can only reach other arms' material by listing a
    traverse-only directory: SCRATCH_ROOT itself, one of its containers, or
    a glob directly under either. With the scratch root hardened such a
    reference resolves to nothing, so it is recorded, not counted as
    contamination. A concrete path into another arm's home or cwd is still
    contamination, because a known path opens without listing."""
    try:
        rel = Path(path).relative_to(SCRATCH_ROOT)
    except ValueError:
        return False
    parts = rel.parts
    from . import vendors as vendors_mod
    if not parts:
        return True
    if any(c in parts[0] for c in _GLOB_CHARS):
        return True
    if parts[0] not in vendors_mod.SCRATCH_CONTAINERS:
        return False
    return len(parts) == 1 or any(c in parts[1] for c in _GLOB_CHARS)


def _check_contamination(record: TraceRecord, vendor: str, expected: set[str],
                          builtin: list[str], *, tool_role: str = "activation") -> tuple[list[str], list[str], list[str]]:
    """Contamination check (DESIGN.md sec 2 T-A, item 5; round 2 findings 2).

    Allowed-visible = expected installed skills union the measured
    `builtin_baseline()` for this vendor+model union the static
    `vendors.KNOWN_BUILTINS[vendor]` fallback. Anything else visible --
    including any `anthropic-skills:*` or other namespaced org skill -- is
    foreign and marks the record contaminated, even when the baseline lists
    it: a namespaced name is always foreign (DESIGN.md T-A item "any visible
    skill containing ':' is foreign").

    Round 2 additions:
    - a claude record whose `visible_tools` (when reported) differs as a set
      from `vendors.CLAUDE_ARM_TOOLS` is contaminated (`tools-mismatch`);
    - a record whose `outside_reads` touches the repository or the real user
      home is contaminated (`outside-read`); other outside reads are
      returned separately so callers can report them as a warning count
      instead of silently dropping them.

    Round 3 finding I5: `outside_reads` is already filtered to paths outside
    the arm's own home and cwd (`trace.parse_trace(..., roots=[home, cwd])`),
    so anything left that also falls under `SCRATCH_ROOT` (another arm's
    home or cwd, a selftest negative-control dir, ...) or under `RUNS_DIR`
    (run records, traces, the holdout ledger) is a read of another arm's or
    the harness's own material, not an unrelated system path -- contaminated
    (`scratch-read`), same tier as `outside-read`.

    Returns (reasons, foreign_skill_names, other_outside_reads).
    """
    reasons: list[str] = []
    foreign: list[str] = []

    if record.visible_skills is not None:
        from . import vendors as vendors_mod

        allowed = expected | set(builtin) | set(vendors_mod.KNOWN_BUILTINS.get(vendor, ()))
        visible = set(record.visible_skills)
        unexpected = visible - allowed
        namespaced = {name for name in visible if ":" in name}
        foreign = sorted(unexpected | namespaced)
        if foreign:
            reasons.append(f"unexpected visible skills: {foreign}")
        missing = expected - visible
        if missing:
            reasons.append(f"expected skills missing from visible set: {sorted(missing)}")

    if vendor == "claude" and record.visible_tools is not None:
        from . import vendors as vendors_mod

        expected_tools_raw = (vendors_mod.CLAUDE_TASK_TOOLS if tool_role == "task" else
                              getattr(vendors_mod, "CLAUDE_ARM_TOOLS", "Read,Glob,Grep,Bash,Skill"))
        expected_tools = {t.strip() for t in expected_tools_raw.split(",") if t.strip()}
        actual_tools = set(record.visible_tools)
        if actual_tools != expected_tools:
            reasons.append(
                f"tools-mismatch: visible tools {sorted(actual_tools)} != expected "
                f"{sorted(expected_tools)}"
            )

    other_outside_reads: list[str] = []
    if record.outside_reads:
        real_home = Path.home()
        bad_reads = []
        scratch_reads = []
        hardened = None
        for p in record.outside_reads:
            if _is_within(p, common.REPO_ROOT) or _is_within(p, real_home):
                bad_reads.append(p)
            elif _is_within(p, SCRATCH_ROOT) or _is_within(p, RUNS_DIR):
                if hardened is None:
                    from . import vendors as vendors_mod
                    hardened = vendors_mod.scratch_is_hardened()
                if hardened and _is_unlistable_probe(p):
                    other_outside_reads.append(p)
                else:
                    scratch_reads.append(p)
            else:
                other_outside_reads.append(p)
        if bad_reads:
            reasons.append(f"outside-read: {sorted(bad_reads)}")
        if scratch_reads:
            reasons.append(f"scratch-read: {sorted(scratch_reads)}")

    return reasons, foreign, other_outside_reads


class _RunState:
    """Shared, lock-guarded state for the thread pool: cost/call/token caps.

    Round 2 finding 5: reservation happens once, atomically, under the lock,
    and the caller never dispatches a call after the reservation is refused
    (see `run_activation`'s submission loop) -- the overshoot bound is then
    only the calls already in flight when a cap trips, never every remaining
    call in the plan.
    """

    def __init__(self, max_calls: int | None, max_cost_usd: float | None,
                 max_codex_tokens: int | None):
        self._lock = threading.Lock()
        self.max_calls = max_calls
        self.max_cost_usd = max_cost_usd
        self.max_codex_tokens = max_codex_tokens
        self.calls_issued = 0
        self.cost_usd = 0.0
        self.codex_tokens = 0
        self.stopped_by_cap = False
        self.stop_reason = ""

    def try_reserve(self, n: int = 1) -> bool:
        """Reserve `n` calls at once, or none: selftest reserves a real and
        a negative call together so a cap never splits a pair."""
        with self._lock:
            if self.stopped_by_cap:
                return False
            if self.max_calls is not None and self.calls_issued + n > self.max_calls:
                self.stopped_by_cap = True
                self.stop_reason = f"--max-calls {self.max_calls} reached"
                return False
            if self.max_cost_usd is not None and self.cost_usd >= self.max_cost_usd:
                self.stopped_by_cap = True
                self.stop_reason = f"--max-cost-usd {self.max_cost_usd} reached"
                return False
            if self.max_codex_tokens is not None and self.codex_tokens >= self.max_codex_tokens:
                self.stopped_by_cap = True
                self.stop_reason = f"--max-codex-tokens {self.max_codex_tokens} reached"
                return False
            self.calls_issued += n
            return True

    def add_cost(self, cost_usd: float | None) -> None:
        if cost_usd is None:
            return
        with self._lock:
            self.cost_usd += cost_usd

    def add_codex_tokens(self, tokens: dict | None) -> None:
        """`--max-cost-usd` never applies to codex (it reports tokens, never
        a dollar cost), so codex's own cap is the sum of input + output
        tokens across records (DESIGN.md carries cost "per vendor in the
        vendor's own unit and never converted")."""
        if not tokens:
            return
        total = (tokens.get("input") or 0) + (tokens.get("output") or 0)
        with self._lock:
            self.codex_tokens += total


def _scrub_holdout_trace(trace_path: Path, prompt: str) -> None:
    """Holdout traces carry no prompt text (DESIGN.md sec 2 T-C item 1c).

    Claude's stream-json format has no user-event echo, but the model's own
    answer can quote the prompt back verbatim, so the raw trace file is
    checked for the literal prompt string after parsing and scrubbed if
    found. Round 3 finding I3: a literal match is not enough on its own --
    `_redact_tool_inputs_in_trace` (called right after this, by every
    caller) additionally strips tool-call inputs line by line, because a
    Skill-tool `args` value or a Bash/Read argument can carry a
    prompt-derived path or fragment (the reviewer's example:
    `docs/briefs/checklist-export.md` survived a literal-prompt scrub
    because the agent had paraphrased the path into its own words)."""
    if not prompt:
        return
    try:
        text = trace_path.read_text(encoding="utf-8")
    except OSError:
        return
    if prompt in text:
        trace_path.write_text(text.replace(prompt, _HOLDOUT_REDACTION_MARKER), encoding="utf-8")


def _redact_tool_inputs_event(ev: dict) -> bool:
    """Mutate one parsed trace event in place, redacting tool inputs. Returns
    True when something was changed. Best-effort and format-tolerant: an
    event shaped unexpectedly is simply left alone rather than raising,
    since this runs over every holdout trace line unconditionally."""
    changed = False
    message = ev.get("message") if isinstance(ev, dict) else None
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use" and "input" in block:
                    block["input"] = _HOLDOUT_REDACTION_MARKER
                    changed = True
    item = ev.get("item") if isinstance(ev, dict) else None
    if isinstance(item, dict) and item.get("type") == "command_execution":
        for key in ("command", "aggregated_output"):
            if key in item:
                item[key] = _HOLDOUT_REDACTION_MARKER
                changed = True
    return changed


def _redact_tool_inputs_in_trace(trace_path: Path) -> None:
    """Round 3 finding I3: strip every tool-call input (Skill-tool `args`, a
    Bash `command`, a Read `file_path`, codex's `command_execution.command`)
    from a holdout trace, unconditionally -- these can carry prompt-derived
    fragments a literal-substring scrub never catches. Parsed and rewritten
    line by line so one malformed line never breaks the run; a line that is
    not JSON, or not a tool-bearing event, passes through unchanged."""
    try:
        raw = trace_path.read_text(encoding="utf-8")
    except OSError:
        return
    lines = raw.split("\n")
    trailing_newline = raw.endswith("\n")
    if trailing_newline and lines and lines[-1] == "":
        lines = lines[:-1]
    changed = False
    out_lines = []
    for line in lines:
        if not line.strip():
            out_lines.append(line)
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            out_lines.append(line)
            continue
        if isinstance(ev, dict) and _redact_tool_inputs_event(ev):
            changed = True
            out_lines.append(json.dumps(ev, ensure_ascii=False))
        else:
            out_lines.append(line)
    if changed:
        text = "\n".join(out_lines)
        if trailing_newline:
            text += "\n"
        trace_path.write_text(text, encoding="utf-8")


def _scrub_holdout_stderr(stderr_path: Path, prompt: str) -> None:
    """Round 3 finding I3: the `.err` file of a holdout trace is plain text,
    not JSON, so a literal-substring scrub against the known prompt is the
    whole fix here (there are no tool-input fields to walk)."""
    if not prompt:
        return
    try:
        text = stderr_path.read_text(encoding="utf-8")
    except OSError:
        return
    if prompt in text:
        stderr_path.write_text(text.replace(prompt, _HOLDOUT_REDACTION_MARKER), encoding="utf-8")


def _execute_one(*, vendor: str, model: str, skills_map: dict[str, Path],
                  description_overrides: dict[str, str] | None, run_label: str, label: str,
                  prompt: str, run_dir: Path, known_skills: set[str], timeout: int, effort: str,
                  keep_home: bool, trace_subdir: str | None = None,
                  workspace_kind: str = DEFAULT_WORKSPACE,
                  collect=None, tools: str = "activation") -> tuple[TraceRecord, dict, list[Finding]]:
    """Run exactly one agent call in a fresh, single-purpose home.

    Round 2 finding 1 (critical): every call gets its own home, named for the
    run, vendor, case, and repeat, built and destroyed around that one call.
    A home reused across calls carries sync downloads and session state from
    one call to the next -- that is how the intermittent org-skill leak
    happened, and it makes repeats dependent on each other instead of
    independent trials. `verify_environment` runs against this fresh home
    before the call spends anything; an error there fails the call without
    ever invoking `exec_agent`. `cleanup_home` always runs in `finally`,
    unless `keep_home` is set for debugging.
    """
    from . import vendors as vendors_mod
    from . import trace as trace_mod

    home = SCRATCH_ROOT / "homes" / f"{run_label}-{vendor}-{label}"
    cwd = vendors_mod.neutral_cwd(f"call-{run_label}-{label}")
    trace_dir = (run_dir / "traces" / trace_subdir) if trace_subdir else (run_dir / "traces")
    trace_dir.mkdir(parents=True, exist_ok=True)
    if trace_subdir:
        # Holdout traces carry the closest thing to prompt-adjacent material
        # this package ever writes to disk; 0700 keeps them unreadable by
        # anyone but this process's owner (DESIGN.md sec 2 T-C item 1c).
        os.chmod(trace_dir, 0o700)
    trace_out = trace_dir / f"{label}-{vendor}.jsonl"

    try:
        try:
            vendors_mod.build_home(vendor, home, skills_map, description_overrides=description_overrides)
        except vendors_mod.CredentialError as exc:
            record = TraceRecord(vendor=vendor, ok=False, error=f"credential: {exc}")
            return record, {"exit_code": None, "duration_s": 0.0, "trace_path": "", "stderr_path": "",
                            "cmd": [], "workspace_sha": None}, []
        # Round 3 finding O1: the fresh cwd is prepared BEFORE
        # verify_environment runs, so an isolation error (an instruction
        # file the fixture itself might carry, say) is caught the same way
        # a bad home is. workspace_sha lets a caller (run, selftest,
        # compare) confirm two runs measured the same condition.
        workspace_sha = vendors_mod.prepare_workspace(cwd, kind=workspace_kind)
        findings = vendors_mod.verify_environment(vendor, home, cwd, set(skills_map))
        errors = [f for f in findings if f.severity == "error"]
        if errors:
            record = TraceRecord(
                vendor=vendor, ok=False,
                error="per-call verify_environment failed: "
                      + "; ".join(f"{f.code}={f.message}" for f in errors),
            )
            result = {"exit_code": None, "duration_s": 0.0, "trace_path": "",
                      "stderr_path": "", "cmd": [], "workspace_sha": workspace_sha}
            return record, result, findings

        result = vendors_mod.exec_agent(vendor, home, cwd, prompt, trace_out, model=model,
                                         effort=effort, timeout=timeout, tools=tools)
        result["workspace_sha"] = workspace_sha
        record = trace_mod.parse_trace(Path(result["trace_path"]), vendor, known_skills=known_skills,
                                        exit_code=result.get("exit_code"), roots=[home, cwd])
        if collect is not None:
            result["evidence"] = collect(cwd, record.text)
        return record, result, findings
    finally:
        if not keep_home:
            vendors_mod.cleanup_home(home)
            # Round 3 finding I7 (minor): cwds under SCRATCH_ROOT were never
            # removed, so a long run left one fixture-sized directory per
            # call behind. Torn down with the home, same --keep-homes gate.
            shutil.rmtree(cwd, ignore_errors=True)


def _prompt_for_case(case_row: dict, all_cases_by_id: dict[str, Case]) -> str:
    return all_cases_by_id[case_row["case_id"]].prompt


def run_activation(plan: dict, *, run_dir: Path, skills_map: dict[str, Path],
                    description_overrides: dict[str, str] | None, run_label: str,
                    all_cases_by_id: dict[str, Case], concurrency: int,
                    timeout: int = DEFAULT_TIMEOUT, effort: str = "medium",
                    keep_homes: bool = False,
                    workspace_kind: str = DEFAULT_WORKSPACE) -> list[dict]:
    """Execute every call in `plan['calls']`, returning result rows.

    Does not write files; callers persist the rows and build the summary.
    Isolated from `_cmd_run` so tests can call it directly with a plan built
    by `plan_run` (and a stubbed `vendors.exec_agent` / `trace.parse_trace`).
    Every call builds and tears down its own home (see `_execute_one`); this
    function only owns the call list, the cap reservation, and the pool.
    """
    from . import vendors as vendors_mod

    expected = _known_skills_for(plan["installed_skills"])
    state = _RunState(plan.get("max_calls"), plan.get("max_cost_usd"), plan.get("max_codex_tokens"))

    builtin_cache: dict[tuple[str, str], list[str]] = {}
    for vendor, model in plan["vendors"].items():
        # An uncached builtin-baseline probe is a real agent call and counts
        # against --max-calls, the same as any other call in the plan --
        # without reservation, a run could spend one call per vendor beyond
        # the stated cap the first time it runs for a given (vendor, model).
        # Reserved, never skipped: the baseline is load-bearing for every
        # contamination check downstream, so it always runs; the reservation
        # only ensures it counts against the budget the rest of the plan
        # then respects.
        if not vendors_mod.baseline_cache_path(vendor, model).exists():
            state.try_reserve()
        builtin_cache[(vendor, model)] = vendors_mod.builtin_baseline(vendor, model)

    rows: list[dict] = [None] * len(plan["calls"])  # type: ignore[list-item]
    rows_lock = threading.Lock()

    def _skip_row(i: int, call: dict, case_row: dict, reason: str) -> None:
        base = {
            "call_index": i, "case_id": call["case_id"], "skill": call["skill"],
            "split": call["split"], "vendor": call["vendor"], "model": call["model"],
            "repeat": call["repeat"], "expect": case_row["expect"], "polarity": case_row["polarity"],
            "tags": case_row["tags"],
        }
        with rows_lock:
            rows[i] = {**base, "skipped_by_cap": True, "ok": False,
                       "error": reason, "activated": [], "first_activated": None,
                       "hit": None, "contaminated": False, "cost_usd": None, "tokens": None,
                       "trace_path": "", "visible_skills": None, "activation_signals": {},
                       "stolen": [], "foreign_skills": [], "other_outside_reads_count": 0}

    def worker(i: int, call: dict) -> None:
        case_row = next(c for c in plan["cases"] if c["id"] == call["case_id"] and c["split"] == call["split"])
        base = {
            "call_index": i, "case_id": call["case_id"], "skill": call["skill"],
            "split": call["split"], "vendor": call["vendor"], "model": call["model"],
            "repeat": call["repeat"], "expect": case_row["expect"], "polarity": case_row["polarity"],
            "tags": case_row["tags"],
        }

        prompt = _prompt_for_case(call, all_cases_by_id)
        label = f"{i:05d}-{call['case_id']}-r{call['repeat']}"
        trace_subdir = "holdout" if call["split"] == "holdout" else None
        record, exec_result, _pf_findings = _execute_one(
            vendor=call["vendor"], model=call["model"], skills_map=skills_map,
            description_overrides=description_overrides, run_label=run_label, label=label,
            prompt=prompt, run_dir=run_dir, known_skills=expected, timeout=timeout, effort=effort,
            keep_home=keep_homes, trace_subdir=trace_subdir, workspace_kind=workspace_kind,
        )

        if call["split"] == "holdout":
            if record.trace_path:
                trace_path = Path(record.trace_path)
                _scrub_holdout_trace(trace_path, prompt)
                _redact_tool_inputs_in_trace(trace_path)
            stderr_path = exec_result.get("stderr_path")
            if stderr_path:
                _scrub_holdout_stderr(Path(stderr_path), prompt)
            if record.text and prompt in record.text:
                record.text = record.text.replace(prompt, _HOLDOUT_REDACTION_MARKER)
            # Round 3 finding I3 (blocker): a holdout call's `error` field
            # can be the model's own reply (claude's is_error result), not
            # merely an echo of the prompt, so it is replaced outright
            # rather than scrubbed by substring match -- the scrub at the
            # line above cleans `record.text`, never `record.error`, and a
            # failed holdout row's `error` text was reaching records.jsonl
            # (and from there summary.json / summary.md) verbatim.
            if record.error:
                record.error = _HOLDOUT_ERROR_REDACTION_MARKER

        state.add_cost(record.cost_usd)
        state.add_codex_tokens(record.tokens)

        contamination_reasons, foreign_skills, other_outside_reads = _check_contamination(
            record, call["vendor"], expected, builtin_cache.get((call["vendor"], call["model"]), []),
        )
        hit = call["skill"] in record.activated
        stolen = [s for s in record.activated if s != call["skill"]] if case_row["expect"] else []

        with rows_lock:
            rows[i] = {
                **base,
                "skipped_by_cap": False,
                "ok": record.ok,
                "error": record.error,
                "activated": list(record.activated),
                "first_activated": record.first_activated,
                "activation_signals": dict(record.activation_signals),
                "hit": hit,
                "stolen": stolen,
                "contaminated": bool(contamination_reasons),
                "contamination_reasons": contamination_reasons,
                "foreign_skills": foreign_skills,
                "other_outside_reads_count": len(other_outside_reads),
                "visible_skills": record.visible_skills,
                "cost_usd": record.cost_usd,
                "tokens": record.tokens,
                "trace_path": record.trace_path,
                "exit_code": exec_result.get("exit_code"),
                "duration_s": exec_result.get("duration_s"),
            }

    # Round 2 finding 5: reserve the slot BEFORE dispatch, under the lock, so
    # a tripped cap stops further calls from ever being submitted to the
    # pool -- not merely skipped once a thread already picked them up. Cost
    # and token caps can only be evaluated against calls that have already
    # finished, so submission is a bounded sliding window (never more than
    # `concurrency` calls in flight at once): submitting the whole plan
    # up front, as a flat list comprehension, would let every remaining
    # call's reservation race ahead of the first call's own result, and the
    # cap would never trip until every call had already been dispatched. The
    # window keeps the overshoot bound to calls already in flight when a cap
    # trips, never the rest of the plan.
    max_workers = max(1, concurrency)
    calls = list(enumerate(plan["calls"]))
    next_idx = 0
    in_flight: dict[concurrent.futures.Future, int] = {}

    def _submit_next(pool: concurrent.futures.ThreadPoolExecutor) -> None:
        nonlocal next_idx
        while next_idx < len(calls) and len(in_flight) < max_workers:
            i, call = calls[next_idx]
            next_idx += 1
            if not state.try_reserve():
                case_row = next(c for c in plan["cases"]
                                 if c["id"] == call["case_id"] and c["split"] == call["split"])
                _skip_row(i, call, case_row, f"skipped: {state.stop_reason}")
                continue
            in_flight[pool.submit(worker, i, call)] = i

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        _submit_next(pool)
        while in_flight:
            done, _pending = concurrent.futures.wait(
                in_flight, return_when=concurrent.futures.FIRST_COMPLETED)
            for f in done:
                f.result()
                del in_flight[f]
            _submit_next(pool)

    result_rows = list(rows)
    plan["_stopped_by_cap"] = state.stopped_by_cap
    plan["_stop_reason"] = state.stop_reason
    return result_rows


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def _rate_block(hits: int, n: int) -> dict:
    lo, hi = wilson_interval(hits, n)
    return {"hits": hits, "n": n, "rate": (hits / n if n else None), "wilson_lo": lo, "wilson_hi": hi}


def _valid(rows: Iterable[dict]) -> list[dict]:
    return [r for r in rows if not r.get("skipped_by_cap") and r.get("ok") and not r.get("contaminated")]


def _count_first_activated(rows: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in rows:
        fired = r.get("first_activated")
        if fired:
            out[fired] = out.get(fired, 0) + 1
    return out


def build_summary(plan: dict, records: list[dict]) -> dict:
    """Re-derive the whole summary from `plan` + `records` only. Never from
    memory: `report` calls this on data re-read from disk.

    Round 2 finding 3b: the holdout split is reported as an aggregate only
    (sensitivity / false-activation rate), never a per-case breakdown --
    `splits_out["holdout"]["cases"]` is always empty, so nothing downstream
    (`report`, `compare`, `feedback`) can recover a holdout case id from it.
    """
    shape = plan["shape"]
    by_vendor: dict[str, list[dict]] = {}
    for r in records:
        by_vendor.setdefault(r["vendor"], []).append(r)

    vendors_out = {}
    for vendor, model in plan["vendors"].items():
        vrows = by_vendor.get(vendor, [])
        scheduled = [r for r in vrows if not r.get("skipped_by_cap")]
        failed = [r for r in scheduled if not r.get("ok")]
        contaminated = [r for r in scheduled if r.get("contaminated")]
        failure_rate = (len(failed) / len(scheduled)) if scheduled else None

        foreign_counts: dict[str, int] = {}
        for r in scheduled:
            for name in r.get("foreign_skills") or []:
                foreign_counts[name] = foreign_counts.get(name, 0) + 1

        outside_reads_warn_count = sum(r.get("other_outside_reads_count") or 0 for r in scheduled)

        cost_usd_vals = [r["cost_usd"] for r in scheduled if r.get("cost_usd") is not None]
        token_rows = [r["tokens"] for r in scheduled if r.get("tokens")]
        tokens_sum = None
        if token_rows:
            tokens_sum = {}
            for row in token_rows:
                for k, v in row.items():
                    if v is None:
                        continue
                    tokens_sum[k] = tokens_sum.get(k, 0) + v

        splits_out = {}
        for split in ("train", "dev", "holdout"):
            srows = [r for r in vrows if r["split"] == split]
            valid = _valid(srows)

            per_case: dict[str, dict] = {}
            if split != "holdout":
                for case_id in sorted({r["case_id"] for r in srows}):
                    crows = [r for r in valid if r["case_id"] == case_id]
                    hits = sum(1 for r in crows if r["hit"])
                    block = {**_rate_block(hits, len(crows)),
                             "polarity": next((r["polarity"] for r in srows
                                                if r["case_id"] == case_id), None)}
                    if shape == "competitive":
                        block["first_activated_by"] = _count_first_activated(crows)
                    per_case[case_id] = block

            pos_valid = [r for r in valid if r["polarity"] == "positive"]
            neg_valid = [r for r in valid if r["polarity"] == "negative"]
            sensitivity = _rate_block(sum(1 for r in pos_valid if r["hit"]), len(pos_valid))
            false_activation = _rate_block(sum(1 for r in neg_valid if r["hit"]), len(neg_valid))

            orig_pos = [r for r in pos_valid if not any(t.startswith("paraphrase-of:") for t in r["tags"])]
            para_pos = [r for r in pos_valid if any(t.startswith("paraphrase-of:") for t in r["tags"])]
            paraphrase_gap = None
            if para_pos:
                orig_rate = _rate_block(sum(1 for r in orig_pos if r["hit"]), len(orig_pos))
                para_rate = _rate_block(sum(1 for r in para_pos if r["hit"]), len(para_pos))
                delta = (orig_rate["rate"] - para_rate["rate"]
                         if orig_rate["rate"] is not None and para_rate["rate"] is not None else None)
                paraphrase_gap = {"original": orig_rate, "paraphrase": para_rate, "delta": delta}

            stolen_by: dict[str, int] = {}
            if shape == "competitive":
                for r in pos_valid:
                    for s in r.get("stolen", []):
                        stolen_by[s] = stolen_by.get(s, 0) + 1

            # Round 2 finding 6: negatives never used to report which skill
            # fired -- a competitive negative that activates something is as
            # informative as a stolen positive, and was silently dropped.
            negative_fired_by: dict[str, int] = {}
            for r in neg_valid:
                if r["hit"]:
                    fired = r.get("first_activated")
                    if fired:
                        negative_fired_by[fired] = negative_fired_by.get(fired, 0) + 1

            splits_out[split] = {
                "calls": len(srows),
                "valid_calls": len(valid),
                "cases": per_case,
                "sensitivity": sensitivity,
                "false_activation_rate": false_activation,
                "paraphrase_gap": paraphrase_gap,
                "stolen_by": dict(sorted(stolen_by.items(), key=lambda kv: -kv[1])),
                "false_activation_fired_by": dict(sorted(negative_fired_by.items(), key=lambda kv: -kv[1])),
            }

        # Round 3 finding I3 (blocker): holdout failures are reported as
        # counts only, in every output -- never with a case id or error
        # text, which is exactly the identifying, potentially prompt-
        # bearing detail the aggregate-only rule (DESIGN.md sec 2 T-C item
        # 1c) exists to keep out of summary.json / summary.md.
        non_holdout_failed = [r for r in failed if r["split"] != "holdout"]
        holdout_failed_count = sum(1 for r in failed if r["split"] == "holdout")

        vendors_out[vendor] = {
            "model": model,
            "calls_scheduled": len(scheduled),
            "calls_failed": len(failed),
            "failure_rate": failure_rate,
            "failure_rate_warn": (failure_rate is not None and failure_rate > FAILURE_RATE_WARN),
            "errors": [{"case_id": r["case_id"], "split": r["split"], "repeat": r["repeat"],
                        "error": r.get("error", "")} for r in non_holdout_failed],
            "holdout_failed_count": holdout_failed_count,
            "contaminated_count": len(contaminated),
            "foreign_skills": dict(sorted(foreign_counts.items(), key=lambda kv: -kv[1])),
            "outside_reads_warn_count": outside_reads_warn_count,
            "cost_usd": (sum(cost_usd_vals) if cost_usd_vals else None),
            "tokens": tokens_sum,
            "splits": splits_out,
        }

    return {
        "run_id": plan.get("run_id"),
        "skill": plan["skill"],
        "shape": shape,
        "split": plan["split"],
        "repeats": plan["repeats"],
        "description_sha": plan.get("description_sha"),
        "workspace": plan.get("workspace"),
        "workspace_sha": plan.get("workspace_sha"),
        "caps": {
            "max_calls": plan.get("max_calls"),
            "max_cost_usd": plan.get("max_cost_usd"),
            "max_codex_tokens": plan.get("max_codex_tokens"),
            "stopped_by_cap": bool(plan.get("_stopped_by_cap")),
            "stop_reason": plan.get("_stop_reason", ""),
        },
        "vendors": vendors_out,
    }


def _fmt_rate(block: dict) -> str:
    if block["n"] == 0:
        return "n/a (n=0)"
    return f"{block['hits']}/{block['n']} = {block['rate']:.0%} (95% CI {block['wilson_lo']:.0%}-{block['wilson_hi']:.0%})"


def render_summary_md(summary: dict) -> str:
    lines = [f"# activation summary: {summary['skill']} ({summary['shape']})", ""]
    lines.append(f"split requested: {summary['split']}  repeats: {summary['repeats']}")
    if summary["description_sha"]:
        lines.append(f"description sha256: {summary['description_sha']}")
    if summary.get("workspace_sha"):
        lines.append(f"workspace: {summary.get('workspace')}  fixture sha256: {summary['workspace_sha']}")
    caps = summary["caps"]
    if caps["stopped_by_cap"]:
        lines.append(f"**run stopped by cap**: {caps['stop_reason']}")
    lines.append("")

    for vendor, v in summary["vendors"].items():
        lines.append(f"## {vendor} ({v['model']})")
        lines.append(f"- calls: {v['calls_scheduled']}, failed: {v['calls_failed']}"
                      + (f" (rate {v['failure_rate']:.0%})" if v['failure_rate'] is not None else ""))
        if v["failure_rate_warn"]:
            lines.append(f"  - **warning**: failure rate exceeds {FAILURE_RATE_WARN:.0%}")
        if v["contaminated_count"]:
            lines.append(f"- contaminated (excluded from rates): {v['contaminated_count']}")
        if v.get("foreign_skills"):
            lines.append("- foreign skills seen: "
                          + ", ".join(f"{k}={n}" for k, n in v["foreign_skills"].items()))
        if v.get("outside_reads_warn_count"):
            lines.append(f"- outside reads outside repo/home (warning only): {v['outside_reads_warn_count']}")
        if v["cost_usd"] is not None:
            lines.append(f"- cost: ${v['cost_usd']:.4f} USD")
        if v["tokens"] is not None:
            lines.append(f"- tokens: {v['tokens']}")
        for err in v["errors"][:10]:
            lines.append(f"  - error [{err['split']}/{err['case_id']}#{err['repeat']}]: {err['error'][:200]}")
        if v.get("holdout_failed_count"):
            # Aggregate only, by design: never a case id, never error text.
            lines.append(f"  - holdout failures (count only): {v['holdout_failed_count']}")

        for split, s in v["splits"].items():
            if s["calls"] == 0:
                continue
            lines.append(f"### {vendor} / {split}")
            lines.append(f"- sensitivity (positive activation rate): {_fmt_rate(s['sensitivity'])}")
            lines.append(f"- false-activation rate (negative activation rate): {_fmt_rate(s['false_activation_rate'])}")
            if s["paraphrase_gap"]:
                pg = s["paraphrase_gap"]
                lines.append(f"- paraphrase gap: original {_fmt_rate(pg['original'])} vs "
                              f"paraphrase {_fmt_rate(pg['paraphrase'])}")
            if s["stolen_by"]:
                lines.append("- stolen-by: " + ", ".join(f"{k}={n}" for k, n in s["stolen_by"].items()))
            if s.get("false_activation_fired_by"):
                lines.append("- negatives fired instead: "
                              + ", ".join(f"{k}={n}" for k, n in s["false_activation_fired_by"].items()))
            if split == "holdout":
                lines.append("- (holdout: aggregate only, no per-case ids or prompts)")
            else:
                lines.append("- per case:")
                for case_id, block in s["cases"].items():
                    lines.append(f"  - {case_id} [{block['polarity']}]: {_fmt_rate(block)}")
        lines.append("")

    return "\n".join(lines)


def _write_summary_files(run_dir: Path, plan: dict, records: list[dict]) -> dict:
    summary = build_summary(plan, records)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    md = render_summary_md(summary)
    (run_dir / "summary.md").write_text(md, encoding="utf-8")
    return summary


# ---------------------------------------------------------------------------
# CLI: run
# ---------------------------------------------------------------------------


def _count_uncached_baseline_probes(vendors_models: dict[str, str]) -> int:
    """Round 2 finding 6: the builtin-baseline probe call `run_activation`
    makes per uncached (vendor, model) pair was not counted in the plan, so
    `--dry-run` undercounted the real spend by one call per vendor the first
    time it ran. Filesystem-only: never calls `builtin_baseline` itself,
    which would spend a real call.

    Round 3 finding (minor): this used to guess the cache filename
    (`{vendor}-{model}.json`) instead of asking `vendors.baseline_cache_path`,
    which actually keys the file on vendor + model + CLI version
    (`{vendor}-{model}-{version}.json`, see `builtin_baseline`'s R2 fix) --
    the guessed name never matched a real cache file, so this always
    reported every vendor as uncached, even on a second run against a
    warm cache.
    """
    from . import vendors as vendors_mod

    count = 0
    for vendor, model in vendors_models.items():
        if not vendors_mod.baseline_cache_path(vendor, model).exists():
            count += 1
    return count


def _print_plan(plan: dict) -> None:
    print(json.dumps({
        "skill": plan["skill"], "shape": plan["shape"], "split": plan["split"],
        "vendors": plan["vendors"], "repeats": plan["repeats"],
        "installed_skills": plan["installed_skills"],
        "call_count_per_vendor": plan["call_count_per_vendor"],
        "call_count_total": plan["call_count_total"],
        "baseline_probe_calls": plan.get("baseline_probe_calls", 0),
        "call_count_total_with_baseline_probes":
            plan["call_count_total"] + plan.get("baseline_probe_calls", 0),
        "description_sha": plan.get("description_sha"),
        "max_calls": plan.get("max_calls"), "max_cost_usd": plan.get("max_cost_usd"),
        "max_codex_tokens": plan.get("max_codex_tokens"),
        "allow_holdout_reuse": plan.get("allow_holdout_reuse"),
    }, indent=2, sort_keys=True))


def _preflight_check(plan: dict, run_label: str, description_overrides: dict[str, str],
                      keep_homes: bool) -> list[Finding]:
    """One representative home per vendor, checked before any call spends
    anything. Every call still gets its own fresh home (see `_execute_one`);
    this exists purely so a systemic isolation problem (a stray CLAUDE.md
    above SCRATCH_ROOT, a leaked env var, a home-skills mismatch) is caught
    once, up front, rather than on call 1 of possibly many.

    Round 3 finding O1: this is also where `plan["workspace_sha"]` is filled
    in -- `vendors.prepare_workspace` runs here, once per run, before
    `verify_environment`, exactly like every other call's cwd (see
    `_execute_one`). The fixture is deterministic for a given kind (DESIGN.md
    sec 3: "a sha256 over the fixture's file list and contents"), so one
    representative preparation is enough to record the condition the whole
    run measured; `compare` reads it back from `plan.json` to warn when two
    runs used different fixtures.
    """
    from . import vendors as vendors_mod

    findings: list[Finding] = []
    expected = _known_skills_for(plan["installed_skills"])
    skills_map = {name: skill_dir(name) for name in plan["installed_skills"]}
    workspace_kind = plan.get("workspace") or DEFAULT_WORKSPACE
    for vendor in plan["vendors"]:
        home = SCRATCH_ROOT / "homes" / f"{run_label}-{vendor}-preflight"
        vendors_mod.build_home(vendor, home, skills_map, description_overrides=description_overrides)
        cwd = vendors_mod.neutral_cwd(f"preflight-{vendor}")
        workspace_sha = vendors_mod.prepare_workspace(cwd, kind=workspace_kind)
        if plan.get("workspace_sha") is None:
            plan["workspace_sha"] = workspace_sha
        findings.extend(vendors_mod.verify_environment(vendor, home, cwd, expected))
        if not keep_homes:
            vendors_mod.cleanup_home(home)
            shutil.rmtree(cwd, ignore_errors=True)
    return findings


def _corpus_gate(skill: str, allow_errors: bool) -> tuple[bool, dict]:
    """Lint `skill`'s visible corpus before spending anything. A file with
    lint errors (below the floor, template residue, unparsable cases) cannot
    give a valid measurement, so a run over it is refused unless the caller
    passes `--allow-corpus-errors`, which the plan records."""
    from . import cases as cases_mod
    findings = cases_mod.lint(skill)
    errors = [f for f in findings if f.severity == "error"]
    summary = {
        "errors": len(errors),
        "warnings": sum(1 for f in findings if f.severity == "warn"),
        "error_codes": sorted({f.code for f in errors}),
        "allowed_with_errors": bool(errors) and allow_errors,
    }
    if errors and not allow_errors:
        print(f"error: the trigger-case corpus for {skill!r} has {len(errors)} lint error(s) "
              f"({', '.join(summary['error_codes'])}); a run over it is not a valid measurement.\n"
              f"  see: python3 scripts/auditing/skill-eval.py cases lint --skill {skill}\n"
              "  pass --allow-corpus-errors to run anyway (recorded in the plan)",
              file=sys.stderr)
        return False, summary
    return True, summary


def _cmd_run(args: argparse.Namespace) -> int:
    vendor_names = [v.strip() for v in args.vendors.split(",") if v.strip()]
    overrides = _parse_kv_list(args.models or "")
    vendors_models = _resolve_models(vendor_names, overrides)

    neighbors = [n.strip() for n in args.neighbors.split(",") if n.strip()] if args.neighbors else []
    if args.shape == "isolated" and (neighbors or args.library):
        print("error: --neighbors/--library only apply to --shape competitive", file=sys.stderr)
        return 2
    if args.shape == "competitive" and not neighbors and not args.library:
        print("error: --shape competitive requires --neighbors or --library", file=sys.stderr)
        return 2

    installed = [args.skill] + (library_skills() if args.library else neighbors)
    installed = list(dict.fromkeys(installed))  # dedupe, keep order, target first

    description_file = Path(args.description_file) if args.description_file else None
    description_text = _description_text(args.skill, description_file)
    description_sha = sha256_text(description_text)
    description_overrides = {args.skill: description_text} if description_file else {}

    # The holdout is ONLY the sealed set (DESIGN.md sec 2 T-C, item 1): load
    # it through integrity.unseal and never mix it with visible train/dev
    # cases in the same run. Everything else (train, dev, visible) comes
    # from the plaintext trigger-cases/ corpus via common.split_cases, whose
    # "holdout" key is the visible dev set, renamed here to avoid confusing
    # it with the real (sealed) holdout.
    if args.split == "holdout":
        from . import integrity as integrity_mod

        sealed_file = integrity_mod.sealed_path(args.skill, "holdout")
        if not sealed_file.exists():
            print(
                f"error: no sealed holdout set for '{args.skill}'; seal one first with:\n"
                f"  python3 scripts/auditing/skill-eval.py integrity seal --skill {args.skill} "
                "--kind holdout --src <path-to-holdout.json>",
                file=sys.stderr,
            )
            return 2
        try:
            sealed = integrity_mod.unseal(sealed_file)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        holdout_cases = [
            Case(skill=args.skill, prompt=c["prompt"], expect=c["expect"],
                 tags=list(c.get("tags", [])), source="sealed")
            for c in sealed["payload"].get("cases", [])
        ]
        cases_by_split = {"train": [], "dev": [], "holdout": holdout_cases}
        all_cases_by_id = {c.id: c for c in holdout_cases}
    else:
        corpus_ok, corpus_lint = _corpus_gate(args.skill, args.allow_corpus_errors)
        if not corpus_ok:
            return 2
        all_cases = _load_all_cases(args.skill, Path(args.include_paraphrases) if args.include_paraphrases else None)
        if not all_cases:
            print(f"error: no trigger cases found for skill {args.skill!r}", file=sys.stderr)
            return 2
        visible_split = split_cases(all_cases)
        cases_by_split = {"train": visible_split["train"], "dev": visible_split["holdout"]}
        all_cases_by_id = {c.id: c for c in all_cases}

    plan = plan_run(
        skill=args.skill, shape=args.shape, installed_skills=installed,
        vendors_models=vendors_models, repeats=args.repeats, split=args.split,
        cases_by_split=cases_by_split, description_sha=description_sha,
        description_file=str(description_file) if description_file else None,
        case_ids=args.case or None, limit=args.limit, max_calls=args.max_calls,
        max_cost_usd=args.max_cost_usd, max_codex_tokens=args.max_codex_tokens,
        allow_holdout_reuse=args.allow_holdout_reuse,
        neighbors=neighbors, library=args.library, workspace=args.workspace,
    )
    plan["baseline_probe_calls"] = _count_uncached_baseline_probes(vendors_models)
    if args.split != "holdout":
        plan["corpus_lint"] = corpus_lint

    if args.dry_run:
        _print_plan(plan)
        return 0

    if plan["call_count_total"] == 0:
        print("error: plan has zero calls (empty split/case selection)", file=sys.stderr)
        return 2

    ledger_path = _resolve_holdout_ledger()
    holdout_decision = None
    if plan["split"] == "holdout":
        holdout_decision = check_holdout_budget(
            args.skill, description_sha, ledger=ledger_path, allow_reuse=args.allow_holdout_reuse,
        )
        if holdout_decision.warning:
            print(f"warning: {holdout_decision.warning}", file=sys.stderr)
        if not holdout_decision.proceed:
            print(f"refused: {holdout_decision.refusal}", file=sys.stderr)
            return 1

    the_run_id = run_id(f"activation-{args.skill}")
    plan["run_id"] = the_run_id
    run_dir = RUNS_DIR / the_run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    findings = _preflight_check(plan, the_run_id, description_overrides, args.keep_homes)
    errors = [f for f in findings if f.severity == "error"]
    if errors:
        for f in errors:
            print(f"error: {f.code}: {f.message}", file=sys.stderr)
        plan["aborted"] = True
        plan["preflight_findings"] = [dataclasses.asdict(f) for f in findings]
        (run_dir / "plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True, default=str),
                                            encoding="utf-8")
        return 1
    for f in findings:  # warnings only, by construction
        print(f"warning: {f.code}: {f.message}", file=sys.stderr)

    (run_dir / "plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True, default=str),
                                        encoding="utf-8")

    # Round 3 finding I7 (minor): the look was recorded AFTER the run
    # finished, so a run that spent one or more real holdout calls and then
    # crashed or was killed left the ledger showing no look at all -- a
    # second run on the same description would spend the holdout again for
    # free. Recorded here, before the first holdout call, as a reservation:
    # the look is charged against the budget as soon as this run commits to
    # spending it, not only once it happens to finish cleanly.
    if holdout_decision is not None:
        common.record_holdout_look(args.skill, description_sha, the_run_id, ledger=ledger_path)

    skills_map = {name: skill_dir(name) for name in plan["installed_skills"]}
    rows = run_activation(plan, run_dir=run_dir, skills_map=skills_map,
                           description_overrides=description_overrides, run_label=the_run_id,
                           all_cases_by_id=all_cases_by_id, concurrency=args.concurrency,
                           timeout=args.timeout, effort=args.effort, keep_homes=args.keep_homes,
                           workspace_kind=args.workspace)
    common.write_jsonl(run_dir / "records.jsonl", rows)

    # plan.json may have been updated in-place with cap-stop info by
    # run_activation(); rewrite it so `report` sees the same picture.
    (run_dir / "plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True, default=str),
                                        encoding="utf-8")

    summary = _write_summary_files(run_dir, plan, rows)
    for vendor, v in summary["vendors"].items():
        if v["failure_rate_warn"]:
            print(f"warning: vendor {vendor} failure rate {v['failure_rate']:.0%} exceeds "
                  f"{FAILURE_RATE_WARN:.0%}", file=sys.stderr)
    if plan.get("_stopped_by_cap"):
        print(f"note: run stopped by cap: {plan.get('_stop_reason')}", file=sys.stderr)

    print(str(run_dir))
    return 0


# ---------------------------------------------------------------------------
# CLI: report
# ---------------------------------------------------------------------------


def _resolve_run_dir(raw: str) -> Path:
    p = Path(raw)
    if p.exists():
        return p
    alt = RUNS_DIR / raw
    if alt.exists():
        return alt
    raise FileNotFoundError(f"no such run directory: {raw}")


def _cmd_report(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run_dir)
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    records = list(common.read_jsonl(run_dir / "records.jsonl"))
    summary = _write_summary_files(run_dir, plan, records)
    print(render_summary_md(summary))
    return 0


# ---------------------------------------------------------------------------
# CLI: compare
# ---------------------------------------------------------------------------


def _holdout_aggregate_rates(records: list[dict]) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    by_key: dict[tuple[str, str], list[dict]] = {}
    for r in records:
        by_key.setdefault((r["vendor"], r.get("polarity", "")), []).append(r)
    for key, rows in by_key.items():
        valid = _valid(rows)
        hits = sum(1 for r in valid if r["hit"])
        out[key] = _rate_block(hits, len(valid))
    return out


def compare_runs(plan_a: dict, records_a: list[dict], plan_b: dict, records_b: list[dict]) -> dict:
    """Per-case rate deltas on case ids common to both runs, per vendor, for
    the train/dev splits, plus a holdout aggregate comparison (never
    per-case, DESIGN.md sec 2 T-C item 3b -- see `_holdout_aggregate_rates`).

    Round 2 finding 6 fixes:
    - warns (never silently compares) when the two runs used different
      models for the same vendor -- rates across different models are not
      the same measurement;
    - the repeats-floor warning now uses the actually valid n for a compared
      case, never the planned `--repeats`: a run whose calls mostly failed
      or were contaminated has fewer usable trials than it was told to make,
      and LEARNINGS.md's floor is about trials that actually happened.

    Round 3 finding O1: also warns when the two runs' workspace fixture
    shas differ -- an A/B description comparison run against two different
    cwd fixtures is not comparing the description, it is comparing the
    fixtures.
    """
    warnings = []

    models_a = plan_a.get("vendors") or {}
    models_b = plan_b.get("vendors") or {}
    mismatched = sorted(v for v in (set(models_a) & set(models_b)) if models_a[v] != models_b[v])
    if mismatched:
        detail = ", ".join(f"{v} (A={models_a[v]!r} vs B={models_b[v]!r})" for v in mismatched)
        warnings.append(f"model mismatch: {detail}; rates are not comparable across different models")

    workspace_sha_a = plan_a.get("workspace_sha")
    workspace_sha_b = plan_b.get("workspace_sha")
    if workspace_sha_a and workspace_sha_b and workspace_sha_a != workspace_sha_b:
        warnings.append(
            f"workspace fixture mismatch: A={workspace_sha_a!r} vs B={workspace_sha_b!r}; "
            "rates are not comparable across different cwd fixtures"
        )

    def _rates(records: list[dict]) -> dict[tuple[str, str, str], dict]:
        out: dict[tuple[str, str, str], dict] = {}
        by_key: dict[tuple[str, str, str], list[dict]] = {}
        for r in records:
            if r["split"] == "holdout":
                continue
            key = (r["vendor"], r["split"], r["case_id"])
            by_key.setdefault(key, []).append(r)
        for key, rows in by_key.items():
            valid = _valid(rows)
            hits = sum(1 for r in valid if r["hit"])
            out[key] = _rate_block(hits, len(valid))
        return out

    rates_a = _rates(records_a)
    rates_b = _rates(records_b)
    common_keys = sorted(set(rates_a) & set(rates_b))

    deltas = []
    min_valid_n = None
    for vendor, split, case_id in common_keys:
        a = rates_a[(vendor, split, case_id)]
        b = rates_b[(vendor, split, case_id)]
        for block in (a, b):
            min_valid_n = block["n"] if min_valid_n is None else min(min_valid_n, block["n"])
        delta = (b["rate"] - a["rate"]) if (a["rate"] is not None and b["rate"] is not None) else None
        deltas.append({"vendor": vendor, "split": split, "case_id": case_id,
                        "rate_a": a["rate"], "rate_b": b["rate"], "delta": delta})

    if min_valid_n is not None and min_valid_n < MIN_REPEATS_FOR_COMPARE:
        warnings.append(f"valid n as low as {min_valid_n} for a compared case, below the floor of "
                         f"{MIN_REPEATS_FOR_COMPARE} for ranking close variants")

    holdout_a = _holdout_aggregate_rates([r for r in records_a if r["split"] == "holdout"])
    holdout_b = _holdout_aggregate_rates([r for r in records_b if r["split"] == "holdout"])
    holdout_out = []
    for key in sorted(set(holdout_a) | set(holdout_b)):
        vendor, polarity = key
        a = holdout_a.get(key, _rate_block(0, 0))
        b = holdout_b.get(key, _rate_block(0, 0))
        delta = (b["rate"] - a["rate"]) if (a["rate"] is not None and b["rate"] is not None) else None
        holdout_out.append({"vendor": vendor, "polarity": polarity,
                             "rate_a": a["rate"], "rate_b": b["rate"], "delta": delta})

    return {"warnings": warnings, "deltas": deltas, "holdout_aggregate": holdout_out}


def _cmd_compare(args: argparse.Namespace) -> int:
    dir_a = _resolve_run_dir(args.run_a)
    dir_b = _resolve_run_dir(args.run_b)
    plan_a = json.loads((dir_a / "plan.json").read_text(encoding="utf-8"))
    plan_b = json.loads((dir_b / "plan.json").read_text(encoding="utf-8"))
    records_a = list(common.read_jsonl(dir_a / "records.jsonl"))
    records_b = list(common.read_jsonl(dir_b / "records.jsonl"))
    result = compare_runs(plan_a, records_a, plan_b, records_b)
    for w in result["warnings"]:
        print(f"warning: {w}", file=sys.stderr)
    for d in result["deltas"]:
        delta_s = f"{d['delta']:+.0%}" if d["delta"] is not None else "n/a"
        print(f"{d['vendor']:8} {d['split']:8} {d['case_id']}  a={d['rate_a']}  b={d['rate_b']}  delta={delta_s}")
    for d in result["holdout_aggregate"]:
        delta_s = f"{d['delta']:+.0%}" if d["delta"] is not None else "n/a"
        print(f"{d['vendor']:8} holdout/{d['polarity']:8}  a={d['rate_a']}  b={d['rate_b']}  delta={delta_s}")
    return 0


# ---------------------------------------------------------------------------
# CLI: feedback (train split only; never leaks holdout, not even case ids)
# ---------------------------------------------------------------------------


def build_feedback(records: list[dict], *, verbatim: bool,
                    all_cases_by_id: dict[str, Case] | None = None) -> dict:
    """Train-only, class-level feedback (DESIGN.md sec 2 T-C, item 3).

    Dev and holdout never appear here as prompts or case ids, train or not:
    they surface only as an aggregate activation rate over their valid
    calls, so a caller can see the split is measured without learning
    anything about any individual case in it.
    """
    train = [r for r in records if r["split"] == "train"]
    dev_rows = [r for r in records if r["split"] == "dev"]
    holdout_rows = [r for r in records if r["split"] == "holdout"]
    valid_train = _valid(train)

    def _aggregate(rows: list[dict]) -> dict:
        valid = _valid(rows)
        return _rate_block(sum(1 for r in valid if r["hit"]), len(valid))

    missed_positive = [r for r in valid_train if r["polarity"] == "positive" and not r["hit"]]
    false_activation = [r for r in valid_train if r["polarity"] == "negative" and r["hit"]]

    def _group_by_tags(rows: list[dict]) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {}
        for r in rows:
            key = ",".join(sorted(r["tags"])) or "untagged"
            out.setdefault(key, []).append(r)
        return out

    near_miss = [r for r in false_activation if "near-miss" in r["tags"]]
    other_false = [r for r in false_activation if "near-miss" not in r["tags"]]

    stolen_by: dict[str, int] = {}
    for r in valid_train:
        if r["polarity"] == "positive":
            for s in r.get("stolen", []):
                stolen_by[s] = stolen_by.get(s, 0) + 1

    # Round 2 finding 6: negatives never reported what fired instead.
    false_activation_fired_by: dict[str, int] = {}
    for r in false_activation:
        fired = r.get("first_activated")
        if fired:
            false_activation_fired_by[fired] = false_activation_fired_by.get(fired, 0) + 1

    def _rows_out(rows: list[dict]) -> list[dict]:
        out = []
        for r in rows:
            row = {"case_id": r["case_id"], "vendor": r["vendor"], "tags": r["tags"],
                   "first_activated": r.get("first_activated")}
            if verbatim and all_cases_by_id is not None and r["case_id"] in all_cases_by_id:
                row["prompt"] = all_cases_by_id[r["case_id"]].prompt
            out.append(row)
        return out

    return {
        "missed_positive_by_tags": {k: _rows_out(v) for k, v in _group_by_tags(missed_positive).items()},
        "false_activation_near_miss": _rows_out(near_miss),
        "false_activation_other": _rows_out(other_false),
        "stolen_by": dict(sorted(stolen_by.items(), key=lambda kv: -kv[1])),
        "false_activation_fired_by": dict(sorted(false_activation_fired_by.items(), key=lambda kv: -kv[1])),
        "dev_aggregate": _aggregate(dev_rows),
        "holdout_aggregate": _aggregate(holdout_rows),
        "dev_calls_omitted": len(dev_rows),
        "holdout_calls_omitted": len(holdout_rows),
        "verbatim": verbatim,
    }


def _cmd_feedback(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run_dir)
    records = list(common.read_jsonl(run_dir / "records.jsonl"))

    all_cases_by_id = None
    if args.verbatim:
        plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
        from . import cases as cases_mod
        cases = cases_mod.load_cases(plan["skill"])
        all_cases_by_id = {c.id: c for c in cases}

    fb = build_feedback(records, verbatim=args.verbatim, all_cases_by_id=all_cases_by_id)
    print(f"train-only feedback ({fb['dev_calls_omitted']} dev calls, "
          f"{fb['holdout_calls_omitted']} holdout calls omitted from the case-level report below)")
    print(f"dev aggregate activation rate:     {_fmt_rate(fb['dev_aggregate'])}")
    print(f"holdout aggregate activation rate: {_fmt_rate(fb['holdout_aggregate'])}")
    print()
    print("missed positives, by tags:")
    for tags, rows in fb["missed_positive_by_tags"].items():
        print(f"  [{tags}] {len(rows)} case(s)")
        for r in rows:
            extra = f": {r['prompt']!r}" if "prompt" in r else ""
            print(f"    - {r['case_id']} ({r['vendor']}){extra}")
    print()
    print(f"false activations, near-miss negatives: {len(fb['false_activation_near_miss'])}")
    for r in fb["false_activation_near_miss"]:
        extra = f": {r['prompt']!r}" if "prompt" in r else ""
        print(f"  - {r['case_id']} ({r['vendor']}){extra} fired={r.get('first_activated')}")
    print(f"false activations, other negatives: {len(fb['false_activation_other'])}")
    for r in fb["false_activation_other"]:
        extra = f": {r['prompt']!r}" if "prompt" in r else ""
        print(f"  - {r['case_id']} ({r['vendor']}){extra} fired={r.get('first_activated')}")
    print()
    if fb["stolen_by"]:
        print("stolen-by: " + ", ".join(f"{k}={n}" for k, n in fb["stolen_by"].items()))
    if fb["false_activation_fired_by"]:
        print("negatives fired instead: "
              + ", ".join(f"{k}={n}" for k, n in fb["false_activation_fired_by"].items()))
    return 0


# ---------------------------------------------------------------------------
# CLI: selftest
# ---------------------------------------------------------------------------


#: Round 3 finding O1: a fixed, never-vary message for a failed positive
#: control. Naming the skill outright is the strongest possible activation
#: signal a prompt can give; when even that does not activate it, the most
#: likely explanation is the environment (a workspace fixture, a vendor CLI
#: change, a rate limit silently degrading responses), not that "detection"
#: -- the trace parser, the Skill-tool / SKILL.md-read signal -- is broken.
#: DESIGN.md's own wording: "that pattern means 'the environment does not
#: let the skill activate', not 'detection is broken'." The old message
#: ("Detection itself is broken") is the one thing this verdict must never
#: say again.
SELFTEST_INCONCLUSIVE_MESSAGE = "no signal: the environment does not let the skill activate"


def _selftest_rate(rows: list[dict]) -> float | None:
    valid = [r for r in rows if r.get("ok")]
    if not valid:
        return None
    return sum(1 for r in valid if r["hit"]) / len(valid)


def _no_valid_calls_reason(arm: str, rows: list[dict]) -> str:
    """Why an arm produced no valid call. A cap that skipped the calls and a
    vendor that failed them are different findings, and neither one says
    anything about the description, so the reason names which it was."""
    if not rows:
        return f"{arm}: no calls were planned"
    skipped = [r for r in rows if str(r.get("error", "")).startswith("skipped: ")]
    if len(skipped) == len(rows):
        return f"{arm}: every call was skipped ({skipped[0]['error'][len('skipped: '):]})"
    errors = sorted({str(r.get("error") or "no error text") for r in rows if not r.get("ok")})
    return f"{arm}: none of {len(rows)} calls returned a valid trace ({'; '.join(errors)[:300]})"


def evaluate_selftest(real_rows: list[dict], negative_rows: list[dict],
                       positive_control_rows: list[dict]) -> dict:
    """Pure scoring over already-executed call rows (dicts with 'hit'/'ok').

    Round 3 finding O1 (blocker): the positive control is judged first. When
    it is below threshold, the verdict is `"inconclusive"` -- explicit
    naming of the skill did not activate it, so nothing this run measured
    about the real description is trustworthy either; the negative control
    is not even scored (DESIGN.md: "the negative control is judged only
    once the positive control passes"). Only once the positive control
    passes does the negative control's drop decide `"pass"` vs `"fail"`.

    An arm with no valid call (every call capped, failed, or contaminated)
    is `"inconclusive"` with a reason naming the arm, never `"fail"`: a
    missing rate is not a measured lack of discrimination.

    `verdict` is one of `"pass" | "fail" | "inconclusive"`. `passed` is kept
    for backward compatibility (`True` iff `verdict == "pass"`); callers
    that need to tell a broken run apart from a genuinely bad description
    must read `verdict`, not `passed`.
    """
    positive_control_rate = _selftest_rate(positive_control_rows)
    positive_control_ok = (
        positive_control_rate is not None
        and positive_control_rate >= SELFTEST_POSITIVE_CONTROL_MIN_RATE
    )

    if not positive_control_ok:
        reason = (SELFTEST_INCONCLUSIVE_MESSAGE if positive_control_rate is not None
                  else _no_valid_calls_reason("positive control", positive_control_rows))
        return {
            "verdict": "inconclusive",
            "passed": False,
            "real_rate": None,
            "negative_control_rate": None,
            "positive_control_rate": positive_control_rate,
            "negative_control_ok": None,
            "positive_control_ok": False,
            "reasons": [reason],
        }

    real_rate = _selftest_rate(real_rows)
    negative_rate = _selftest_rate(negative_rows)
    missing = [_no_valid_calls_reason(arm, rows)
               for arm, rows, rate in (("real arm", real_rows, real_rate),
                                       ("negative arm", negative_rows, negative_rate))
               if rate is None]
    if missing:
        return {
            "verdict": "inconclusive",
            "passed": False,
            "real_rate": real_rate,
            "negative_control_rate": negative_rate,
            "positive_control_rate": positive_control_rate,
            "negative_control_ok": None,
            "positive_control_ok": True,
            "reasons": missing,
        }

    negative_control_ok = negative_rate <= real_rate - SELFTEST_MIN_DROP
    reasons = []
    if not negative_control_ok:
        reasons.append(
            f"negative control failed: real-description positive rate is {real_rate}, "
            f"unrelated-description rate is {negative_rate}; needed a drop of at least "
            f"{SELFTEST_MIN_DROP:.0%}. This description is no better than noise at this "
            "sample size."
        )

    return {
        "verdict": "pass" if negative_control_ok else "fail",
        "passed": negative_control_ok,
        "real_rate": real_rate,
        "negative_control_rate": negative_rate,
        "positive_control_rate": positive_control_rate,
        "negative_control_ok": negative_control_ok,
        "positive_control_ok": True,
        "reasons": reasons,
    }


def _build_negative_control_skill_dir(skill: str, dest_root: Path) -> Path:
    """Copy `skill`'s SKILL.md into `dest_root/<neutral name>/SKILL.md` with
    both the frontmatter `name:` and `description:` swapped to a neutral,
    unrelated unit-conversion control, keeping the body identical (round 2
    finding 4). The negative control used to keep the skill's own name, so
    an agent could activate it purely on name recognition -- a false pass or
    fail that has nothing to do with whether the description discriminates.
    With only the name and description different, a name match can no
    longer explain the result either way.
    """
    src_dir = skill_dir(skill)
    text = (src_dir / "SKILL.md").read_text(encoding="utf-8")
    text = common.replace_description(text, SELFTEST_UNRELATED_DESCRIPTION)
    text, n = re.subn(r"(?m)^name:\s*.*$", f"name: {SELFTEST_NEGATIVE_CONTROL_NAME}", text, count=1)
    if n == 0:
        raise ValueError(f"{src_dir / 'SKILL.md'}: no top-level 'name:' frontmatter line found")

    dest_dir = dest_root / SELFTEST_NEGATIVE_CONTROL_NAME
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)
    (dest_dir / "SKILL.md").write_text(text, encoding="utf-8")
    for item in src_dir.iterdir():
        if item.name == "SKILL.md":
            continue
        target = dest_dir / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    return dest_dir


def _run_arm(*, skill: str, vendor: str, model: str, skills_map: dict[str, Path],
             prompt_specs: list[tuple[str, int, str]], run_dir: Path, arm_label: str,
             known_skills: set[str], timeout: int, effort: str, run_label: str,
             keep_homes: bool, workspace_kind: str = DEFAULT_WORKSPACE,
             state: "_RunState | None" = None, reserved: bool = False) -> list[dict]:
    """Run one selftest arm. `prompt_specs` is `[(case_id, repeat, prompt), ...]`
    so each call's home and trace are named for the case id and repeat index
    (round 2 finding 6: the old naming used `hash((arm_label, vendor, i))`,
    which can collide; case id + repeat index cannot, by construction of
    `common.case_id`). Each call gets its own fresh home, verified and torn
    down like every other call in this module (round 2 finding 1).

    Round 3 finding I7: `state`, when given, is the same `_RunState` cap
    machinery `run_activation` uses -- a spec is skipped (never dispatched)
    once a cap trips, exactly like a capped call in `run`. `reserved` means
    the caller already reserved these calls on `state`; costs still accrue.
    """
    rows = []
    for case_id, repeat, prompt in prompt_specs:
        if state is not None and not reserved and not state.try_reserve():
            rows.append({"vendor": vendor, "ok": False, "hit": False,
                         "error": f"skipped: {state.stop_reason}", "_record": TraceRecord(vendor=vendor, ok=False)})
            continue
        label = f"{arm_label}-{case_id}-r{repeat}"
        record, exec_result, _findings = _execute_one(
            vendor=vendor, model=model, skills_map=skills_map, description_overrides=None,
            run_label=run_label, label=label, prompt=prompt, run_dir=run_dir,
            known_skills=known_skills, timeout=timeout, effort=effort, keep_home=keep_homes,
            workspace_kind=workspace_kind,
        )
        if state is not None:
            state.add_cost(record.cost_usd)
            state.add_codex_tokens(record.tokens)
        rows.append({"vendor": vendor, "ok": record.ok, "hit": skill in record.activated,
                      "error": record.error, "_record": record})
    return rows


class SelftestBudgetError(ValueError):
    """`--max-calls` cannot fund one complete comparison per vendor."""


def _selftest_plan(skill: str, vendors_models: dict[str, str], repeats: int,
                    n_train_positives: int, max_calls: int | None = None) -> dict:
    """Round 3 finding I7: `--dry-run` for selftest, sharing the same shape
    `run --dry-run` prints. Per vendor: positive control `repeats` calls
    (one case, repeated), then real and negative `cases * repeats` calls
    each. This is the UPPER bound -- a live invocation spends less per
    vendor when the positive control fails and the real/negative arms are
    skipped (DESIGN.md/finding O1: the negative control is judged, and also
    RUN, only once the positive control passes).

    `max_calls` sizes the plan instead of truncating it. A cap that tripped
    mid-run used to starve the arms dispatched last -- the negative arm,
    and every arm of the second vendor -- so a capped run reported a
    missing rate as a failed control. Now the cap is split evenly across
    vendors and the number of train positives shrinks until every vendor
    can afford a complete positive control plus paired real and negative
    arms. A cap too small for one case per vendor raises
    `SelftestBudgetError` before any call is made."""
    n_cases = n_train_positives
    per_vendor_budget = None
    if max_calls is not None:
        per_vendor_budget = max_calls // max(1, len(vendors_models))
        affordable = (per_vendor_budget - repeats) // (2 * repeats) if repeats > 0 else 0
        if affordable < 1:
            minimum = 3 * repeats * len(vendors_models)
            raise SelftestBudgetError(
                f"--max-calls {max_calls} cannot fund one complete selftest: each vendor needs "
                f"{3 * repeats} calls at --repeats {repeats} (positive control, real, negative), "
                f"so {len(vendors_models)} vendor(s) need at least {minimum}. "
                "Raise --max-calls or lower --repeats."
            )
        n_cases = min(n_train_positives, affordable)
    per_vendor = {v: (2 * n_cases * repeats) + repeats for v in vendors_models}
    return {
        "skill": skill, "vendors": dict(vendors_models), "repeats": repeats,
        "train_positive_cases": n_train_positives,
        "cases_used": n_cases,
        "max_calls": max_calls,
        "call_budget_per_vendor": per_vendor_budget,
        "call_count_per_vendor": per_vendor,
        "call_count_total": sum(per_vendor.values()),
    }


#: Round 3 finding O1: exit code per overall verdict. `fail` outranks
#: `inconclusive` (a vendor that actively fails must not be hidden behind
#: another vendor's inconclusive run), which outranks `pass`.
SELFTEST_EXIT_CODES = {"pass": 0, "fail": 1, "inconclusive": 3}


def _overall_selftest_verdict(per_vendor: dict[str, dict]) -> str:
    verdicts = [v.get("verdict", "fail") for v in per_vendor.values()]
    if any(v == "fail" for v in verdicts):
        return "fail"
    if any(v == "inconclusive" for v in verdicts):
        return "inconclusive"
    return "pass"


def _cmd_selftest(args: argparse.Namespace) -> int:
    from . import vendors as vendors_mod
    from . import cases as cases_mod

    vendor_names = [v.strip() for v in args.vendors.split(",") if v.strip()]
    overrides = _parse_kv_list(args.models or "")
    vendors_models = _resolve_models(vendor_names, overrides)

    corpus_ok, corpus_lint = _corpus_gate(args.skill, args.allow_corpus_errors)
    if not corpus_ok:
        return 2
    cases = cases_mod.load_cases(args.skill)
    train_positives = [c for c in split_cases(cases)["train"] if c.expect]
    if not train_positives:
        print(f"error: {args.skill!r} has no train-split positive cases; selftest needs at least one",
              file=sys.stderr)
        return 2

    try:
        plan = _selftest_plan(args.skill, vendors_models, args.repeats, len(train_positives),
                              max_calls=args.max_calls)
    except SelftestBudgetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.dry_run:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0
    train_positives = train_positives[:plan["cases_used"]]
    plan["corpus_lint"] = corpus_lint

    the_run_id = run_id(f"selftest-{args.skill}")
    run_dir = RUNS_DIR / the_run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    vendors_mod.harden_scratch_root()
    neg_control_root = SCRATCH_ROOT / "selftest-negctrl" / the_run_id
    neg_skill_dir = _build_negative_control_skill_dir(args.skill, neg_control_root)

    real_skills_map = {args.skill: skill_dir(args.skill)}
    neg_skills_map = {SELFTEST_NEGATIVE_CONTROL_NAME: neg_skill_dir}

    repeat_specs = [(c.id, r, c.prompt) for c in train_positives for r in range(args.repeats)]
    explicit_prompt = f"Use the {args.skill} skill to help with this: {train_positives[0].prompt}"
    pc_specs = [(train_positives[0].id, r, explicit_prompt) for r in range(args.repeats)]

    # Each vendor gets its own call budget, sized by `_selftest_plan`, so the
    # first vendor can never spend the second vendor's calls. Cost and token
    # caps are per vendor already: only claude reports dollars and only codex
    # reports tokens.
    vendor_budget = plan["call_budget_per_vendor"]

    def _write_result(per_vendor: dict[str, dict]) -> dict:
        overall = _overall_selftest_verdict(per_vendor) if per_vendor else "inconclusive"
        result = {
            "verdict": overall,
            "passed": overall == "pass",
            "skill": args.skill,
            "negative_control_skill_name": SELFTEST_NEGATIVE_CONTROL_NAME,
            "plan": plan,
            "vendors": per_vendor,
        }
        (run_dir / "selftest.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return result

    def _vendor_selftest(vendor: str, model: str) -> dict:
        state = _RunState(vendor_budget, args.max_cost_usd, args.max_codex_tokens)
        preflight_findings: list[Finding] = []
        for label, skills_map in (("real", real_skills_map), ("negative", neg_skills_map)):
            pf_home = SCRATCH_ROOT / "homes" / f"{the_run_id}-{vendor}-{label}-preflight"
            vendors_mod.build_home(vendor, pf_home, skills_map)
            cwd = vendors_mod.neutral_cwd(f"selftest-preflight-{vendor}-{label}")
            vendors_mod.prepare_workspace(cwd, kind=args.workspace)
            preflight_findings.extend(vendors_mod.verify_environment(vendor, pf_home, cwd, set(skills_map)))
            if not args.keep_homes:
                vendors_mod.cleanup_home(pf_home)
                shutil.rmtree(cwd, ignore_errors=True)
        pf_errors = [f for f in preflight_findings if f.severity == "error"]
        if pf_errors:
            return {
                "verdict": "fail", "passed": False,
                "preflight_errors": [dataclasses.asdict(f) for f in pf_errors],
                "reasons": [f"preflight isolation check failed for {vendor}: "
                            + "; ".join(f"{f.code}={f.message}" for f in pf_errors)],
            }

        builtin = vendors_mod.builtin_baseline(vendor, model)

        def _score(rows: list[dict], expected: set[str]) -> list[dict]:
            # A contaminated call is an invalid call: it keeps its row, with
            # ok=False and the reason as its error, so a fully contaminated
            # arm reports why it has no rate instead of looking unplanned.
            for row in rows:
                record = row.pop("_record")
                reasons, _foreign, _other = _check_contamination(record, vendor, expected, builtin)
                row["contaminated"] = bool(reasons)
                row["contamination_reasons"] = reasons
                if reasons and row.get("ok"):
                    row["ok"] = False
                    row["error"] = "contaminated: " + "; ".join(reasons)
            return rows

        def _arm(arm_label: str, specs: list[tuple[str, int, str]], negative: bool,
                 reserved: bool = False) -> list[dict]:
            name = SELFTEST_NEGATIVE_CONTROL_NAME if negative else args.skill
            return _score(_run_arm(
                skill=name, vendor=vendor, model=model,
                skills_map=neg_skills_map if negative else real_skills_map,
                prompt_specs=specs, run_dir=run_dir, arm_label=arm_label,
                known_skills={name}, timeout=args.timeout, effort=args.effort,
                run_label=the_run_id, keep_homes=args.keep_homes, workspace_kind=args.workspace,
                state=state, reserved=reserved,
            ), {name})

        # Round 3 finding O1: the positive control runs, and is judged,
        # FIRST. When it is below threshold the run stops for this vendor
        # right there -- the real and negative arms are never dispatched,
        # which both saves the spend and matches "the negative control is
        # judged only once the positive control passes" as an execution
        # order, not merely a scoring order.
        positive_control_rows = _arm("positive-control", pc_specs, negative=False)
        real_rows: list[dict] = []
        negative_rows: list[dict] = []
        pc_only = evaluate_selftest([], [], positive_control_rows)
        if pc_only["positive_control_ok"]:
            # Real and negative calls run as reserved pairs, so a cost or
            # token cap that trips mid-run leaves both arms with the same
            # number of calls instead of starving whichever arm ran last.
            for spec in repeat_specs:
                if not state.try_reserve(2):
                    skipped = {"vendor": vendor, "ok": False, "hit": False,
                               "error": f"skipped: {state.stop_reason}", "contaminated": False,
                               "contamination_reasons": []}
                    real_rows.append(dict(skipped))
                    negative_rows.append(dict(skipped))
                    continue
                real_rows.extend(_arm("real", [spec], negative=False, reserved=True))
                negative_rows.extend(_arm("negative", [spec], negative=True, reserved=True))
            vendor_result = evaluate_selftest(real_rows, negative_rows, positive_control_rows)
        else:
            vendor_result = pc_only

        all_rows = positive_control_rows + real_rows + negative_rows
        vendor_result["calls"] = {
            "planned": plan["call_count_per_vendor"][vendor],
            "dispatched": state.calls_issued,
            "valid": sum(1 for r in all_rows if r.get("ok")),
        }
        if state.stopped_by_cap:
            vendor_result["stopped_by_cap"] = state.stop_reason
        vendor_result["contaminated_counts"] = {
            "real": sum(1 for r in real_rows if r["contaminated"]),
            "negative": sum(1 for r in negative_rows if r["contaminated"]),
            "positive_control": sum(1 for r in positive_control_rows if r["contaminated"]),
        }
        return vendor_result

    # Round 2 finding 4: evaluate per vendor, never pooled -- one broken
    # vendor must fail the selftest for that vendor specifically, and the
    # report lists each vendor's own verdict rather than averaging a healthy
    # vendor's signal over a broken one's noise. Each vendor's result is
    # written as soon as it exists, and an exception in one vendor becomes
    # that vendor's inconclusive result, so an interrupted or crashing run
    # still leaves a selftest.json naming what it measured.
    per_vendor: dict[str, dict] = {}
    try:
        for vendor, model in vendors_models.items():
            try:
                vendor_result = _vendor_selftest(vendor, model)
            except Exception as exc:  # noqa: BLE001 - recorded, never swallowed
                vendor_result = {
                    "verdict": "inconclusive", "passed": False,
                    "reasons": [f"selftest raised {type(exc).__name__}: {exc}"],
                }
            vendor_result["vendor"] = vendor
            per_vendor[vendor] = vendor_result
            _write_result(per_vendor)
    finally:
        if not args.keep_homes:
            shutil.rmtree(neg_control_root, ignore_errors=True)

    result = _write_result(per_vendor)
    overall_verdict = result["verdict"]
    print(json.dumps(result, indent=2, sort_keys=True))
    print(str(run_dir))
    return SELFTEST_EXIT_CODES[overall_verdict]


# ---------------------------------------------------------------------------
# CLI: selftest-all -- one selftest per skill, run as parallel child processes
# ---------------------------------------------------------------------------


def _selftest_child_argv(skill: str, args: argparse.Namespace) -> list[str]:
    argv = [sys.executable, str(common.AUDITING_DIR / "skill-eval.py"), "activation", "selftest",
            "--skill", skill, "--vendors", args.vendors, "--repeats", str(args.repeats),
            "--timeout", str(args.timeout), "--effort", args.effort, "--workspace", args.workspace]
    for flag, value in (("--models", args.models), ("--max-calls", args.max_calls),
                        ("--max-cost-usd", args.max_cost_usd),
                        ("--max-codex-tokens", args.max_codex_tokens)):
        if value is not None:
            argv += [flag, str(value)]
    return argv


def summarize_sweep(results: dict[str, dict]) -> dict:
    """Counts per overall verdict and per vendor verdict; `results` maps a
    skill to its selftest.json content, or to `{"verdict": "error", ...}`
    when the child produced none."""
    overall: dict[str, int] = {}
    per_vendor: dict[str, dict[str, int]] = {}
    for res in results.values():
        overall[res.get("verdict", "error")] = overall.get(res.get("verdict", "error"), 0) + 1
        for vendor, vres in (res.get("vendors") or {}).items():
            bucket = per_vendor.setdefault(vendor, {})
            bucket[vres.get("verdict", "error")] = bucket.get(vres.get("verdict", "error"), 0) + 1
    return {"skills": len(results), "overall": overall, "per_vendor": per_vendor}


def render_sweep_md(results: dict[str, dict], summary: dict) -> str:
    def _r(x):
        return "-" if x is None else f"{x:.2f}"
    vendors = sorted({v for r in results.values() for v in (r.get("vendors") or {})})
    lines = ["# selftest sweep", "",
             f"skills: {summary['skills']}  overall: "
             + ", ".join(f"{k}={v}" for k, v in sorted(summary["overall"].items())), ""]
    for v in vendors:
        lines.append(f"- {v}: " + ", ".join(f"{k}={n}" for k, n in sorted(summary["per_vendor"].get(v, {}).items())))
    lines += ["", "| skill | overall | " + " | ".join(f"{v} verdict | {v} pc/real/neg | {v} valid/planned | {v} reason" for v in vendors) + " |",
              "|---|---|" + "---|---|---|---|" * len(vendors)]
    for skill in sorted(results):
        res = results[skill]
        cells = [skill, res.get("verdict", "error")]
        for v in vendors:
            vr = (res.get("vendors") or {}).get(v, {})
            calls = vr.get("calls") or {}
            reason = "; ".join(vr.get("reasons", []))[:120].replace("|", "/")
            cells += [vr.get("verdict", "-"),
                      f"{_r(vr.get('positive_control_rate'))}/{_r(vr.get('real_rate'))}/{_r(vr.get('negative_control_rate'))}",
                      f"{calls.get('valid', '-')}/{calls.get('planned', '-')}", reason]
        if res.get("verdict") == "error":
            cells[-1] = (res.get("error") or "")[:120].replace("|", "/")
        lines.append("| " + " | ".join(str(c) for c in cells) + " |")
    return "\n".join(lines) + "\n"


def _cmd_selftest_all(args: argparse.Namespace) -> int:
    import subprocess

    skills = [s.strip() for s in args.skills.split(",") if s.strip()] if args.skills else library_skills()
    if args.dry_run:
        total = 0
        for skill in skills:
            out = subprocess.run(_selftest_child_argv(skill, args) + ["--dry-run"],
                                 capture_output=True, text=True)
            if out.returncode != 0:
                print(f"{skill}: refused: {out.stderr.strip()[:200]}")
                continue
            total += json.loads(out.stdout)["call_count_total"]
        print(json.dumps({"skills": len(skills), "call_count_total_upper_bound": total}, indent=2))
        return 0

    sweep_dir = RUNS_DIR / run_id("selftest-sweep")
    sweep_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict] = {}
    lock = threading.Lock()

    def _one(skill: str) -> None:
        out = subprocess.run(_selftest_child_argv(skill, args), capture_output=True, text=True)
        lines = [l for l in out.stdout.strip().splitlines() if l.strip()]
        run_dir = Path(lines[-1]) if lines else None
        if run_dir is not None and (run_dir / "selftest.json").exists():
            res = json.loads((run_dir / "selftest.json").read_text(encoding="utf-8"))
            res["run_dir"] = str(run_dir)
        else:
            res = {"verdict": "error", "exit_code": out.returncode,
                   "error": (out.stderr.strip().splitlines() or ["no selftest.json and no stderr"])[-1]}
        with lock:
            results[skill] = res
            summary = summarize_sweep(results)
            (sweep_dir / "sweep.json").write_text(
                json.dumps({"summary": summary, "skills": results}, indent=2, sort_keys=True), encoding="utf-8")
            (sweep_dir / "sweep.md").write_text(render_sweep_md(results, summary), encoding="utf-8")
            print(f"[{len(results)}/{len(skills)}] {skill}: {res.get('verdict')}", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.parallel)) as pool:
        list(pool.map(_one, skills))
    summary = summarize_sweep(results)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(str(sweep_dir))
    if summary["overall"].get("fail") or summary["overall"].get("error"):
        return 1
    return 0 if summary["overall"].get("pass", 0) == len(skills) else 3


# ---------------------------------------------------------------------------
# argparse wiring
# ---------------------------------------------------------------------------


def add_subparser(subparsers) -> None:
    parser = subparsers.add_parser(
        "activation", help="measure whether a skill's description makes it load"
    )
    sub = parser.add_subparsers(dest="activation_command", required=True)

    p_run = sub.add_parser("run", help="run an activation measurement")
    p_run.add_argument("--skill", required=True)
    p_run.add_argument("--shape", choices=SHAPES, default="isolated")
    p_run.add_argument("--neighbors", default=None, help="comma-separated skill names (competitive)")
    p_run.add_argument("--library", action="store_true", help="install the whole library (competitive)")
    p_run.add_argument("--vendors", default="claude,codex")
    p_run.add_argument("--models", default=None, help="vendor=model,vendor2=model2")
    p_run.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    p_run.add_argument("--split", choices=SPLITS, default="train")
    p_run.add_argument("--include-paraphrases", default=None, type=str)
    p_run.add_argument("--description-file", default=None, type=str)
    p_run.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    p_run.add_argument("--max-cost-usd", type=float, default=None)
    p_run.add_argument("--max-codex-tokens", type=int, default=None,
                        help="cap on summed input+output codex tokens across records "
                             "(--max-cost-usd never applies to codex)")
    p_run.add_argument("--max-calls", type=int, default=None)
    p_run.add_argument("--limit", type=int, default=None)
    p_run.add_argument("--case", action="append", default=[])
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument("--keep-homes", action="store_true",
                        help="skip cleanup of arm homes after each call (they hold credentials)")
    p_run.add_argument("--allow-holdout-reuse", action="store_true")
    p_run.add_argument("--allow-corpus-errors", action="store_true",
                       help="run even when `cases lint` reports errors for this skill (recorded)")
    p_run.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    p_run.add_argument("--effort", default="medium")
    p_run.add_argument("--workspace", default=DEFAULT_WORKSPACE,
                        help="empty|git|<fixture dir>: how each fresh cwd is prepared "
                             "before verify_environment runs (default: git)")
    p_run.set_defaults(func=_cmd_run)

    p_report = sub.add_parser("report", help="re-render a run's summary from records.jsonl")
    p_report.add_argument("run_dir")
    p_report.set_defaults(func=_cmd_report)

    p_compare = sub.add_parser("compare", help="per-case rate deltas between two runs")
    p_compare.add_argument("run_a")
    p_compare.add_argument("run_b")
    p_compare.set_defaults(func=_cmd_compare)

    p_feedback = sub.add_parser("feedback", help="train-only, class-level failure feedback")
    p_feedback.add_argument("run_dir")
    p_feedback.add_argument("--verbatim", action="store_true")
    p_feedback.set_defaults(func=_cmd_feedback)

    p_selftest = sub.add_parser("selftest", help="negative + positive control on the same home layout")
    p_selftest.add_argument("--skill", required=True)
    p_selftest.add_argument("--vendors", default="claude,codex")
    p_selftest.add_argument("--models", default=None)
    p_selftest.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    p_selftest.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    p_selftest.add_argument("--effort", default="medium")
    p_selftest.add_argument("--keep-homes", action="store_true",
                             help="skip cleanup of arm homes after each call (they hold credentials)")
    p_selftest.add_argument("--workspace", default=DEFAULT_WORKSPACE,
                             help="empty|git|<fixture dir>: how each fresh cwd is prepared "
                                  "before verify_environment runs (default: git)")
    p_selftest.add_argument("--dry-run", action="store_true",
                             help="print the call plan and exit; no home is built, nothing is spent")
    p_selftest.add_argument("--max-calls", type=int, default=None)
    p_selftest.add_argument("--max-cost-usd", type=float, default=None)
    p_selftest.add_argument("--max-codex-tokens", type=int, default=None)
    p_selftest.add_argument("--allow-corpus-errors", action="store_true",
                            help="run even when `cases lint` reports errors for this skill (recorded)")
    p_selftest.set_defaults(func=_cmd_selftest)

    p_sweep = sub.add_parser("selftest-all", help="selftest every skill (or --skills) in parallel; one summary table")
    p_sweep.add_argument("--skills", default=None, help="comma-separated subset; default is the whole library")
    p_sweep.add_argument("--parallel", type=int, default=6, help="skills run at once (each is one child process)")
    p_sweep.add_argument("--vendors", default="claude,codex")
    p_sweep.add_argument("--models", default=None)
    p_sweep.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    p_sweep.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    p_sweep.add_argument("--effort", default="medium")
    p_sweep.add_argument("--workspace", default=DEFAULT_WORKSPACE)
    p_sweep.add_argument("--max-calls", type=int, default=None, help="per skill, as in selftest")
    p_sweep.add_argument("--max-cost-usd", type=float, default=None, help="per skill, as in selftest")
    p_sweep.add_argument("--max-codex-tokens", type=int, default=None, help="per skill, as in selftest")
    p_sweep.add_argument("--dry-run", action="store_true")
    p_sweep.set_defaults(func=_cmd_selftest_all)
