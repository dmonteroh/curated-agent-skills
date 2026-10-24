"""Compare task quality with and without a skill on both vendors."""
from __future__ import annotations

import argparse
import dataclasses
import fnmatch
import json
import math
import os
import random
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path, PurePosixPath

from . import __version__, activation, common, judge, vendors

# Chosen defaults bound evidence size and scorer runtime.
MAX_EVIDENCE_BYTES = 2 * 1024 * 1024
SCORER_TIMEOUT = 60
DEFAULT_REPEATS = 4  # Recovered writing-style campaign's floor for close variants.


class BudgetExceeded(RuntimeError):
    """Stop before the next call when a spending guard is reached."""


@dataclasses.dataclass
class Budget:
    max_calls: int | None = None
    max_cost_usd: float | None = None
    max_codex_tokens: int | None = None
    calls: int = 0
    cost_usd: float = 0.0
    codex_tokens: int = 0

    def reserve(self):
        if self.max_calls is not None and self.calls >= self.max_calls:
            raise BudgetExceeded("Call budget reached.")
        if self.max_cost_usd is not None and self.cost_usd >= self.max_cost_usd:
            raise BudgetExceeded("Claude dollar budget reached.")
        if self.max_codex_tokens is not None and self.codex_tokens >= self.max_codex_tokens:
            raise BudgetExceeded("Codex token budget reached.")
        self.calls += 1

    def record(self, trace):
        if trace.cost_usd is not None:
            self.cost_usd += trace.cost_usd
        if trace.tokens:
            self.codex_tokens += sum((trace.tokens.get(k) or trace.tokens.get(k + "_tokens") or 0)
                                     for k in ("input", "output"))


def _relative_path(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Artifact paths must be relative POSIX paths.")
    path = PurePosixPath(value)
    if path.is_absolute() or str(path) != value or any(p in (".", "..") for p in value.split("/")):
        raise ValueError(f"Unsafe artifact path: {value}")
    return value


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must contain text.")
    return value


_ID_RE = re.compile(r"[a-zA-Z0-9_-]+")
TASK_KINDS = ("deliverable", "harm", "stand-down")
_V1_TASK_FIELDS = {"id", "prompt", "workspace", "artifacts", "checks", "assertions", "control_markers"}
_V2_TASK_FIELDS = _V1_TASK_FIELDS | {"kind", "claims", "planted"}


def load_suite(path: Path) -> list[dict]:
    """Validate task data before any agent calls. Returns the task list."""
    return load_card(path)["tasks"]


def load_card(path: Path) -> dict:
    """Validate a suite (version 1) or an eval card (version 2).

    Version 2 adds `claims` (what the skill promises, each probed by tagged
    checks or assertions), task `kind` and `claims`, `planted` good and bad
    outputs for `validate`, and an `invalidation` map from skill paths to
    the claims a change there invalidates (read by `plan`)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] not in (1, 2):
        raise ValueError("Suite version must be 1 or 2.")
    version = data["version"]
    allowed = {"version", "tasks"} | ({"claims", "invalidation"} if version == 2 else set())
    if set(data) - allowed:
        raise ValueError("Unknown suite fields.")
    claim_ids: list[str] = []
    if version == 2:
        claims = data.get("claims")
        if not isinstance(claims, list) or not claims:
            raise ValueError("A version 2 card needs a nonempty claims list.")
        for claim in claims:
            if not isinstance(claim, dict) or set(claim) - {"id", "statement", "rests_on"}:
                raise ValueError("Claims take id, statement, and rests_on.")
            cid = _text(claim.get("id"), "Claim id")
            if not _ID_RE.fullmatch(cid) or cid in claim_ids:
                raise ValueError(f"Duplicate or unsafe claim id: {cid}")
            claim_ids.append(cid)
            _text(claim.get("statement"), "Claim statement")
            rests_on = claim.setdefault("rests_on", [])
            if not isinstance(rests_on, list) or any(not isinstance(r, str) or not r.strip() for r in rests_on):
                raise ValueError("Claim rests_on must be a list of skill paths or sections.")
        invalidation = data.setdefault("invalidation", {})
        if not isinstance(invalidation, dict):
            raise ValueError("Invalidation must map skill paths to claim lists.")
        for key, value in invalidation.items():
            _text(key, "Invalidation path")
            if value != "all" and (not isinstance(value, list) or not value
                                   or any(v not in claim_ids for v in value)):
                raise ValueError(f"Invalidation for {key} must be \"all\" or a list of known claim ids.")
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Suite tasks must be a nonempty list.")
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or set(task) - (_V2_TASK_FIELDS if version == 2 else _V1_TASK_FIELDS):
            raise ValueError("Unknown task fields.")
        tid = _text(task.get("id"), "Task id")
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", tid) or tid in seen:
            raise ValueError(f"Duplicate or unsafe task id: {tid}")
        seen.add(tid)
        _text(task.get("prompt"), "Prompt")
        workspace = _text(task.get("workspace", "empty"), "Workspace")
        if workspace not in ("empty", "git"):
            src = (path.parent / workspace).resolve()
            vendors._refuse_instruction_or_config_source(src)
            if any(p.is_symlink() for p in src.rglob("*")):
                raise ValueError("Workspace fixtures cannot contain symlinks.")
            workspace = str(src)
        task["workspace"] = workspace
        artifacts = task.setdefault("artifacts", [])
        if not isinstance(artifacts, list):
            raise ValueError("Artifacts must be a list.")
        for artifact in artifacts:
            _relative_path(artifact)
        if len(set(artifacts)) != len(artifacts):
            raise ValueError("Duplicate artifact paths.")
        assertions = task.setdefault("assertions", [])
        if not isinstance(assertions, list):
            raise ValueError("Assertions must be a list.")
        assertion_ids = set()
        for i, assertion in enumerate(assertions):
            if isinstance(assertion, str):
                assertions[i] = {"id": f"assertion-{i + 1}", "text": _text(assertion, "Assertion")}
            elif isinstance(assertion, dict) and {"id", "text"} <= set(assertion) <= (
                    {"id", "text", "claim"} if version == 2 else {"id", "text"}):
                _text(assertion["id"], "Assertion id")
                _text(assertion["text"], "Assertion text")
            else:
                raise ValueError("Assertions need text or an id/text object.")
            if assertions[i]["id"] in assertion_ids:
                raise ValueError("Duplicate assertion ids.")
            assertion_ids.add(assertions[i]["id"])
        checks = task.setdefault("checks", [])
        if not isinstance(checks, list):
            raise ValueError("Checks must be a list.")
        check_ids = set()
        for check in checks:
            if not isinstance(check, dict) or set(check) - ({"id", "kind", "target", "value", "argv", "metrics"}
                                                            | ({"claim"} if version == 2 else set())):
                raise ValueError("Unknown check fields.")
            cid = _text(check.get("id"), "Check id")
            if cid in check_ids:
                raise ValueError("Duplicate check ids.")
            check_ids.add(cid)
            kind = check.get("kind")
            if kind not in ("contains", "not_contains", "regex", "file_exists", "command"):
                raise ValueError(f"Unknown check kind: {kind}")
            target = check.get("target", "output")
            if target != "output" and target not in artifacts:
                raise ValueError("Check targets must be output or a declared artifact.")
            if kind == "file_exists" and target == "output":
                raise ValueError("file_exists needs an artifact target.")
            if kind == "command":
                argv = check.get("argv")
                if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a for a in argv):
                    raise ValueError("Command checks need a nonempty argv list.")
                metrics = check.get("metrics", {})
                if not isinstance(metrics, dict):
                    raise ValueError("Command metrics must map names to path/direction objects.")
                for name, spec in metrics.items():
                    _text(name, "Metric name")
                    if not isinstance(spec, dict) or set(spec) != {"path", "direction"}:
                        raise ValueError("Metrics need a path and direction.")
                    _text(spec["path"], "Metric path")
                    if spec["direction"] not in ("lower", "higher"):
                        raise ValueError("Metric direction must be lower or higher.")
            elif "metrics" in check:
                raise ValueError("Numeric metrics require a command check.")
            if kind not in ("command", "file_exists"):
                _text(check.get("value"), "Check value")
                if kind == "regex":
                    re.compile(check["value"])
        markers = task.setdefault("control_markers", [])
        if not isinstance(markers, list):
            raise ValueError("Control markers must be a list.")
        for marker in markers:
            re.compile(_text(marker, "Control marker"))
        if not checks and not assertions:
            raise ValueError("Every task needs checks or assertions.")
        if version == 2:
            _validate_card_task(task, claim_ids, path)
    if version == 2:
        probed = {item["claim"] for t in tasks for item in t["checks"] + t["assertions"]}
        missing = [c for c in claim_ids if c not in probed]
        if missing:
            raise ValueError(f"Claims with no check or assertion: {', '.join(missing)}")
        if not any(t["kind"] in ("harm", "stand-down") for t in tasks):
            raise ValueError("A card needs at least one harm or stand-down task.")
    return {"version": version, "claims": data.get("claims", []),
            "invalidation": data.get("invalidation", {}), "tasks": tasks}


def _validate_card_task(task: dict, claim_ids: list[str], path: Path) -> None:
    """Version 2 task rules: a kind, the claims it probes, every check and
    assertion tagged with one of those claims, and planted outputs on disk."""
    kind = task.setdefault("kind", "deliverable")
    if kind not in TASK_KINDS:
        raise ValueError(f"Task kind must be one of {', '.join(TASK_KINDS)}.")
    claims = task.get("claims")
    if not isinstance(claims, list) or not claims or any(c not in claim_ids for c in claims) \
            or len(set(claims)) != len(claims):
        raise ValueError(f"Task {task['id']} must list known claims, without duplicates.")
    for item in task["checks"] + task["assertions"]:
        if item.get("claim") not in claims:
            raise ValueError(f"Task {task['id']}: {item['id']} must name one of the task's claims.")
    planted = task.setdefault("planted", [])
    if not isinstance(planted, list):
        raise ValueError("Planted outputs must be a list.")
    for sample in planted:
        if not isinstance(sample, dict) or set(sample) != {"path", "expect"} or sample["expect"] not in ("good", "bad"):
            raise ValueError("A planted output needs a path and expect: good or bad.")
        src = (path.parent / _text(sample["path"], "Planted path")).resolve()
        if not (src / "output.txt").is_file():
            raise ValueError(f"Planted output {sample['path']} needs an output.txt.")
        if any(p.is_symlink() for p in src.rglob("*")):
            raise ValueError("Planted outputs cannot contain symlinks.")
        sample["path"] = str(src)


def collect_evidence(cwd: Path, text: str, task: dict, destination: Path) -> dict:
    """Capture declared artifacts before the temporary workspace is removed."""
    destination.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    used = len(text.encode("utf-8"))
    if used > MAX_EVIDENCE_BYTES:
        raise ValueError("Final output exceeds the evidence limit.")
    for rel in task["artifacts"]:
        path = cwd / rel
        if any(p.is_symlink() for p in (path, *path.parents) if p != cwd.parent):
            raise ValueError(f"Artifact contains a symlink: {rel}")
        if not path.exists():
            artifacts[rel] = None
            continue
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError(f"Artifact must be a regular file: {rel}")
        used += path.stat().st_size
        if used > MAX_EVIDENCE_BYTES:
            raise ValueError("Declared artifacts exceed the evidence limit.")
        content = path.read_text(encoding="utf-8")
        artifacts[rel] = content
        target = destination / "artifacts" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    (destination / "output.txt").write_text(text, encoding="utf-8")
    (destination / "artifacts").mkdir(exist_ok=True)
    return {"artifacts": artifacts}


def objective_checks(text: str, artifacts: dict, checks: list[dict], destination: Path) -> list[dict]:
    results = []
    for check in checks:
        kind = check["kind"]
        target = check.get("target", "output")
        content = text if target == "output" else artifacts.get(target)
        row = {"id": check["id"], "verdict": "unsupported"}
        if check.get("claim"):
            row["claim"] = check["claim"]
        if kind == "command":
            # The operator supplies argv. No shell or arm labels reach the scorer.
            argv = [arg.replace("{output}", str(destination / "output.txt"))
                    .replace("{workspace}", str(destination / "artifacts")) for arg in check["argv"]]
            try:
                proc = subprocess.run(argv, cwd=destination / "artifacts", input=None,
                                      capture_output=True, text=True, timeout=SCORER_TIMEOUT,
                                      env={k: v for k, v in os.environ.items()
                                           if k in {"PATH", "LANG", "LC_ALL", "TMPDIR"}})
                row.update(exit_code=proc.returncode, stdout=proc.stdout[:MAX_EVIDENCE_BYTES],
                           stderr=proc.stderr[:MAX_EVIDENCE_BYTES])
                row["verdict"] = {0: "pass", 1: "fail"}.get(proc.returncode, "unsupported")
                if check.get("metrics"):
                    try:
                        payload = json.loads(proc.stdout)
                        values = {}
                        for name, spec in check["metrics"].items():
                            value = payload
                            for key in spec["path"].split("."):
                                value = value[int(key)] if isinstance(value, list) else value[key]
                            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                                raise ValueError(f"Metric {name} must be a finite number.")
                            values[name] = {"value": value, "direction": spec["direction"]}
                        row["metrics"] = values
                    except (ValueError, KeyError, TypeError, IndexError) as exc:
                        row["verdict"] = "unsupported"
                        row["metric_error"] = str(exc)
            except (OSError, subprocess.TimeoutExpired) as exc:
                row["error"] = str(exc)
        else:
            if kind == "file_exists":
                passed = content is not None
            elif content is None:
                passed = False
            elif kind == "contains":
                passed = check["value"] in content
            elif kind == "not_contains":
                passed = check["value"] not in content
            else:
                passed = bool(re.search(check["value"], content))
            row["verdict"] = "pass" if passed else "fail"
        results.append(row)
    return results


def _judge_text(record: dict) -> str:
    text = record["trace"]["text"]
    for path, content in sorted(record.get("artifacts", {}).items()):
        text += f"\n\nArtifact {path}:\n{content if content is not None else '[missing file]'}"
    return text


GRADING_MODES = ("batched", "separate")


def judge_calls_per_pair(task: dict, grading: str) -> int:
    """`batched`: one call per presentation order grades every assertion for
    both outputs and gives the preference. `separate`: one call per assertion
    per output, plus two pairwise calls."""
    return 2 if grading == "batched" else 2 + 2 * len(task["assertions"])


def plan_run(tasks, models, repeats, judge_vendor, mode, grading="batched"):
    if grading not in GRADING_MODES:
        raise ValueError(f"Grading must be one of {', '.join(GRADING_MODES)}.")
    pairs = len(tasks) * len(models) * repeats
    grading_calls = sum(judge_calls_per_pair(t, grading) for t in tasks) * len(models) * repeats
    return {"vendors": models, "repeats": repeats, "mode": mode, "judge_vendor": judge_vendor,
            "grading": grading, "tasks": tasks, "baseline_calls": len(models), "arm_calls": pairs * 2,
            "judge_calls": grading_calls if judge_vendor != "none" else 0,
            "call_count_total": len(models) + pairs * 2 + (grading_calls if judge_vendor != "none" else 0)}


# Chosen default: a claim the no-skill arm already meets at this rate or
# above is BASELINE, so the skill earns nothing for it (claims.md rule from
# the writing-style campaign: "a claim present in the without arms is baseline").
BASELINE_RATE = 0.8


def claim_outcome(pair: dict, arm: str, claim: str, task: dict) -> bool | None:
    """Whether one arm met one claim: every check and assertion the task tags
    with the claim passed. None when any of them is missing from the record
    (a judge that never ran) or unsupported, so partial evidence never
    decides a claim."""
    expected = [("checks", c["id"]) for c in task["checks"] if c.get("claim") == claim] + \
               [("grades", a["id"]) for a in task["assertions"] if a.get("claim") == claim]
    if not expected:
        return None
    verdicts = []
    for kind, item_id in expected:
        row = next((r for r in pair["arms"][arm].get(kind, []) if r["id"] == item_id), None)
        if row is None or row["verdict"] == "unsupported":
            return None
        verdicts.append(row["verdict"] == "pass")
    return all(verdicts)


def claim_verdict(with_met: int, without_met: int, n: int) -> dict:
    """STRONG or HARM when the two arms' 95% Wilson intervals do not overlap,
    BASELINE when the no-skill arm already meets the claim, WEAK otherwise
    (no separation at this n: more pairs may still separate it), UNMEASURED
    with no supported pair. Disjoint intervals are a conservative chosen
    test. A paired test would separate sooner."""
    if n == 0:
        return {"verdict": "UNMEASURED", "n": 0}
    w_lo, w_hi = common.wilson_interval(with_met, n)
    o_lo, o_hi = common.wilson_interval(without_met, n)
    if w_lo > o_hi:
        verdict = "STRONG"
    elif o_lo > w_hi:
        verdict = "HARM"
    elif without_met / n >= BASELINE_RATE:
        verdict = "BASELINE"
    else:
        verdict = "WEAK"
    return {"verdict": verdict, "n": n, "with": with_met / n, "without": without_met / n,
            "with_interval": [w_lo, w_hi], "without_interval": [o_lo, o_hi]}


def claim_summary(plan: dict, pairs: list[dict]) -> dict:
    """Per claim: a verdict per vendor and pooled, plus whether the vendors
    moved the same way. A claim counts once per pair, over every task that
    probes it."""
    out = {}
    for claim in plan.get("claims", []):
        cid = claim["id"]
        tasks = {t["id"]: t for t in plan["tasks"] if cid in t.get("claims", [])}
        per_vendor, pooled = {}, [0, 0, 0]
        for vendor in plan["vendors"]:
            counts = [0, 0, 0]
            for pair in pairs:
                if pair["vendor"] != vendor or pair["task_id"] not in tasks or not pair["valid"]:
                    continue
                task = tasks[pair["task_id"]]
                w, o = claim_outcome(pair, "with", cid, task), claim_outcome(pair, "without", cid, task)
                if w is None or o is None:
                    continue
                counts[0] += w
                counts[1] += o
                counts[2] += 1
            per_vendor[vendor] = claim_verdict(*counts)
            pooled = [a + b for a, b in zip(pooled, counts)]
        directions = {v: r["with"] - r["without"] for v, r in per_vendor.items() if r["n"]}
        agree = None
        if len(directions) == len(plan["vendors"]) and len(directions) > 1:
            signs = {(d > 0) - (d < 0) for d in directions.values()}
            agree = len(signs) == 1 and 0 not in signs
        out[cid] = {"statement": claim["statement"], "vendors": per_vendor,
                    "pooled": claim_verdict(*pooled), "vendors_agree": agree}
    return out


def _codex_token_parts(tokens: dict) -> dict:
    """Codex reports cached input inside input; it is billed at a discount,
    so the parts stay separate. Older traces used *_tokens keys."""
    get = lambda k: tokens.get(k) or tokens.get(k + "_tokens") or 0
    cached = get("cached_input")
    return {"uncached_input": get("input") - cached, "cached_input": cached, "output": get("output")}


def _arm_cost(pairs: list[dict], vendor: str) -> dict:
    """Mean cost per arm in the vendor's own unit, never converted. Codex
    gives input plus output (the budget's unit) and its parts."""
    out = {"unit": "usd" if vendor == "claude" else "tokens"}
    for arm in ("without", "with"):
        values, parts = [], []
        for pair in pairs:
            if pair["vendor"] != vendor or not pair["valid"]:
                continue
            trace = pair["arms"][arm]["trace"]
            if vendor == "claude" and trace.get("cost_usd") is not None:
                values.append(trace["cost_usd"])
            elif vendor == "codex" and trace.get("tokens"):
                part = _codex_token_parts(trace["tokens"])
                parts.append(part)
                values.append(part["uncached_input"] + part["cached_input"] + part["output"])
        out[arm] = sum(values) / len(values) if values else None
        if parts:
            out.setdefault("parts", {})[arm] = {k: sum(p[k] for p in parts) / len(parts) for k in parts[0]}
    return out


def _script_runs(pairs: list[dict], vendor: str, name: str) -> dict:
    """Valid arms that executed one of the evaluated skill's own scripts.
    Records parsed before traces carried `script_runs` are left out, so an
    old run reports 0 of 0 rather than a false "never ran"."""
    out = {}
    prefix = f"skills/{name}/scripts/"
    for arm in ("without", "with"):
        rows = [p["arms"][arm]["trace"] for p in pairs if p["vendor"] == vendor and p["valid"]
                and "script_runs" in p["arms"][arm]["trace"]]
        out[arm] = {"ran": sum(any(r.startswith(prefix) for r in t.get("script_runs", [])) for t in rows),
                    "of": len(rows)}
    return out


def judge_pair(pair: dict, task: dict, *, grading: str, judge_kwargs: dict, run_dir: Path,
               label: str, rng: random.Random) -> None:
    """Grade both arms of a valid pair and compare them, in place. Grades
    carry the claim their assertion names, so claim verdicts can read them."""
    claim_of = {a["id"]: a.get("claim") for a in task["assertions"]}
    without, with_ = _judge_text(pair["arms"]["without"]), _judge_text(pair["arms"]["with"])
    if grading == "batched":
        result = judge.compare_and_grade(task["prompt"], without, with_, task["assertions"],
                                         run_dir=run_dir / "judgements" / label,
                                         seed=rng.randrange(2**32), **judge_kwargs)
        pair["arms"]["without"]["grades"] = result["grades"]["a"]
        pair["arms"]["with"]["grades"] = result["grades"]["b"]
        pair["comparison"] = result["comparison"]
    else:
        order = ["without", "with"]
        rng.shuffle(order)
        for arm in order:
            pair["arms"][arm]["grades"] = judge.grade(task["prompt"], _judge_text(pair["arms"][arm]),
                                                      task["assertions"], **judge_kwargs)
        pair["comparison"] = judge.pairwise(task["prompt"], without, with_, repeats=2,
                                            run_dir=run_dir / "judgements" / label,
                                            seed=rng.randrange(2**32), **judge_kwargs)
    for arm in ("without", "with"):
        for row in pair["arms"][arm]["grades"]:
            if claim_of.get(row["id"]):
                row["claim"] = claim_of[row["id"]]


def _decided_claims(plan: dict, pairs: list[dict], vendor: str) -> set[str]:
    """Claims already STRONG or HARM for this vendor: more pairs cannot
    change the direction, so adaptive rounds stop spending on them."""
    summary = claim_summary(plan, pairs)
    return {cid for cid, c in summary.items() if c["vendors"].get(vendor, {}).get("verdict") in ("STRONG", "HARM")}


def _score(rows):
    if not rows or any(r["verdict"] == "unsupported" for r in rows):
        return None
    return sum(r["verdict"] == "pass" for r in rows) / len(rows)


def summarize(plan, pairs, budget):
    rows = []
    for vendor in plan["vendors"]:
        for task in plan["tasks"]:
            selected = [p for p in pairs if p["vendor"] == vendor and p["task_id"] == task["id"]]
            valid = [p for p in selected if p["valid"]]
            skipped = sum(1 for v, t, _ in plan.get("adaptive_skipped", []) if v == vendor and t == task["id"])
            row = {"vendor": vendor, "task_id": task["id"], "pairs": len(selected),
                   "expected_pairs": plan["repeats"] - skipped,
                   "valid_pairs": len(valid), "invalid_pairs": len(selected) - len(valid),
                   "activation_count": sum((plan.get("installed_name") or plan["skill"]) in p["arms"]["with"]["trace"]["activated"]
                                           for p in selected),
                   "pairwise": dict(Counter({"a": "without", "b": "with"}.get(
                       p.get("comparison", {}).get("verdict"), p.get("comparison", {}).get("verdict", "void"))
                       for p in valid))}
            decisive = row["pairwise"].get("with", 0) + row["pairwise"].get("without", 0)
            row["skill_win_interval"] = list(common.wilson_interval(row["pairwise"].get("with", 0), decisive))
            for metric in ("checks", "grades"):
                deltas = []
                without_scores, with_scores = [], []
                for pair in valid:
                    scores = [_score(pair["arms"][a].get(metric, [])) for a in ("without", "with")]
                    if all(s is not None for s in scores):
                        without_scores.append(scores[0])
                        with_scores.append(scores[1])
                        deltas.append(scores[1] - scores[0])
                row[metric] = {"supported_pairs": len(deltas),
                               "without": sum(without_scores) / len(deltas) if deltas else None,
                               "with": sum(with_scores) / len(deltas) if deltas else None,
                               "delta": sum(deltas) / len(deltas) if deltas else None}
            metric_samples = {}
            for pair in valid:
                left = {check["id"]: check for check in pair["arms"]["without"].get("checks", [])}
                for check in pair["arms"]["with"].get("checks", []):
                    other = left.get(check["id"], {})
                    if check["verdict"] == "unsupported" or other.get("verdict") == "unsupported":
                        continue
                    for name, item in check.get("metrics", {}).items():
                        previous = other.get("metrics", {}).get(name)
                        if previous and previous["direction"] == item["direction"]:
                            samples = metric_samples.setdefault(f"{check['id']}/{name}", {"direction": item["direction"], "values": []})
                            samples["values"].append((previous["value"], item["value"]))
            row["metrics"] = {}
            for name, samples in metric_samples.items():
                values = samples["values"]
                without = sum(a for a, _ in values) / len(values)
                with_skill = sum(b for _, b in values) / len(values)
                delta = with_skill - without
                row["metrics"][name] = {"supported_pairs": len(values), "without": without,
                                        "with": with_skill, "delta": delta, "direction": samples["direction"],
                                        "improvement": -delta if samples["direction"] == "lower" else delta}
            rows.append(row)
    installed_name = plan.get("installed_name") or plan["skill"]
    return {"skill": plan["skill"], "mode": plan["mode"], "rows": rows,
            "claims": claim_summary(plan, pairs),
            "arm_cost": {v: _arm_cost(pairs, v) for v in plan["vendors"]},
            "script_runs": {v: _script_runs(pairs, v, installed_name) for v in plan["vendors"]},
            "adaptive_skipped": len(plan.get("adaptive_skipped", [])),
            "calls": budget.calls, "claude_cost_usd": budget.cost_usd,
            "codex_tokens": budget.codex_tokens,
            "incomplete": any(r["pairs"] != r["expected_pairs"] or r["invalid_pairs"] for r in rows)
                          or any(p.get("grading_error") for p in pairs)
                          or any(p.get("comparison", {}).get("verdict") == "void" for p in pairs)
                          or any(r["verdict"] == "unsupported" for p in pairs for a in p["arms"].values()
                                 for r in a.get("checks", []) + a.get("grades", []))}


def write_summary(run_dir: Path, summary: dict):
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [f"# Task quality: {summary['skill']}", "", f"Mode: {summary['mode']}. Incomplete: {summary['incomplete']}.", "",
             "| Vendor | Task | Valid pairs | Skill loaded | Check delta | Assertion delta | Preference |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in summary["rows"]:
        def delta(metric):
            value = row[metric]["delta"]
            return f"{value:+.3f}" if value is not None else "unavailable"
        lines.append(f"| {row['vendor']} | {row['task_id']} | {row['valid_pairs']}/{row['pairs']} | "
                     f"{row['activation_count']}/{row['pairs']} | {delta('checks')} | {delta('grades')} | {row['pairwise']} |")
    if any(row["metrics"] for row in summary["rows"]):
        lines += ["", "| Vendor | Task | Metric | Without | With | Improvement | Pairs |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        for row in summary["rows"]:
            for name, metric in sorted(row["metrics"].items()):
                lines.append(f"| {row['vendor']} | {row['task_id']} | {name} | {metric['without']:.3f} | "
                             f"{metric['with']:.3f} | {metric['improvement']:+.3f} | {metric['supported_pairs']} |")
    if summary.get("claims"):
        vendor_names = sorted({v for c in summary["claims"].values() for v in c["vendors"]})
        lines += ["", "| Claim | " + " | ".join(vendor_names) + " | Pooled | Vendors agree |",
                  "| --- | " + " | ".join("---" for _ in vendor_names) + " | --- | --- |"]

        def cell(result):
            if not result["n"]:
                return "UNMEASURED"
            return f"{result['verdict']} {result['with']:.2f} vs {result['without']:.2f}, n={result['n']}"
        for cid, claim in summary["claims"].items():
            agree = {True: "yes", False: "no", None: "-"}[claim["vendors_agree"]]
            lines.append(f"| {cid} | " + " | ".join(cell(claim["vendors"][v]) for v in vendor_names)
                         + f" | {cell(claim['pooled'])} | {agree} |")
        lines += ["", "A claim verdict compares the with-skill rate to the without rate. STRONG and HARM need "
                  "non-overlapping 95% intervals. BASELINE means the without arm already meets the claim. "
                  "WEAK means no separation at this n."]
    if summary.get("arm_cost"):
        lines += ["", "| Vendor | Unit | Mean per arm without | Mean per arm with | Skill scripts run (with) |",
                  "| --- | --- | --- | --- | --- |"]
        part_lines = []
        for vendor, cost in summary["arm_cost"].items():
            fmt = (lambda x: "-" if x is None else f"{x:.4f}") if cost["unit"] == "usd" else \
                  (lambda x: "-" if x is None else f"{x:.0f}")
            runs = summary.get("script_runs", {}).get(vendor, {}).get("with", {"ran": 0, "of": 0})
            ran = f"{runs['ran']}/{runs['of']}" if runs["of"] else "not recorded"
            lines.append(f"| {vendor} | {cost['unit']} | {fmt(cost['without'])} | {fmt(cost['with'])} | {ran} |")
            for arm, part in sorted(cost.get("parts", {}).items()):
                part_lines.append(f"| {vendor} | {arm} | {part['uncached_input']:.0f} | {part['cached_input']:.0f} | "
                                  f"{part['output']:.0f} |")
        if part_lines:
            lines += ["", "Codex input includes cached input, which is billed at a discount.", "",
                      "| Vendor | Arm | Uncached input | Cached input | Output |", "| --- | --- | --- | --- | --- |"]
            lines += part_lines
    if summary.get("adaptive_skipped"):
        lines += ["", f"Adaptive rounds skipped {summary['adaptive_skipped']} pairs whose claims were already decided."]
    lines += ["", f"Calls: {summary['calls']}. Claude dollars: {summary['claude_cost_usd']:.4f}. Codex tokens: {summary['codex_tokens']}.", "",
              "Scores use valid pairs with supported evidence. Positive check deltas, assertion deltas, and metric improvements favour the skill.",
              "An installed skill may remain inactive in natural mode. Explicit mode requires observed activation."]
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(plan: dict, *, budget: Budget, timeout: int, effort: str, seed: int) -> Path:
    if any(activation._is_within(common.RUNS_DIR, root) for root in (common.REPO_ROOT, common.SCRATCH_ROOT)):
        raise ValueError("Run records must stay outside the repository and scratch root.")
    rid = common.run_id(f"performance-{plan['skill']}")
    run_dir = common.RUNS_DIR / rid
    run_dir.mkdir(parents=True, mode=0o700)
    plan = dict(plan, run_id=rid, evaluator_version=__version__, seed=seed, effort=effort, timeout=timeout,
                budget_limits=dataclasses.asdict(budget), cli_versions={v: vendors.cli_version(v) for v in plan["vendors"]})
    plan["tasks"] = json.loads(json.dumps(plan["tasks"]))
    skill_snapshot = run_dir / "inputs" / "skill"
    shutil.copytree(common.skill_dir(plan["skill"]), skill_snapshot)
    if vendors._fixture_fingerprint(skill_snapshot) != plan["skill_sha"]:
        raise ValueError("Skill changed after planning. Start a fresh run.")
    # `installed_name` is the name the arms see. It differs from the skill
    # only with --install-as, used when the skill's name collides with a
    # vendor built-in (claude ships `code-review`): the frontmatter name is
    # rewritten in the snapshot so the installed skill answers to the alias.
    installed_name = plan.get("installed_name") or plan["skill"]
    if installed_name != plan["skill"]:
        skill_md = skill_snapshot / "SKILL.md"
        text, n = re.subn(r"(?m)^name:\s*.*$", f"name: {installed_name}", skill_md.read_text(encoding="utf-8"), count=1)
        if n != 1:
            raise ValueError("Cannot rename the skill snapshot: no frontmatter name line.")
        skill_md.write_text(text, encoding="utf-8")
    for task in plan["tasks"]:
        if task["workspace"] not in ("empty", "git"):
            snapshot = run_dir / "inputs" / "fixtures" / task["id"]
            shutil.copytree(task["workspace"], snapshot)
            task["workspace"] = str(snapshot)
            task["workspace_sha"] = vendors._fixture_fingerprint(snapshot)
    (run_dir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    known = set(common.library_skills()) | {installed_name}
    names = sorted(known | set(judge._default_skill_names()))
    pairs = []
    builtins, baseline_errors = {}, {}

    def execute(vendor, model, prompt, installed, label, task=None):
        budget.reserve()
        destination = run_dir / "evidence" / common.run_id("sample")
        def collect(cwd, text):
            try:
                return collect_evidence(cwd, text, task, destination)
            except (OSError, ValueError, UnicodeError) as exc:
                return {"error": str(exc)}
        rec, info, findings = activation._execute_one(
            vendor=vendor, model=model, skills_map=installed, description_overrides=None,
            run_label=rid, label=label, prompt=prompt, run_dir=run_dir,
            known_skills=known, timeout=timeout, effort=effort, keep_home=False,
            workspace_kind=task["workspace"] if task else "empty", collect=collect if task else None,
            tools="task" if task else "activation")
        budget.record(rec)
        rec.model = model
        if task is None and rec.visible_skills is not None:
            builtins[vendor] = [s for s in rec.visible_skills if ":" not in s]
        reasons, foreign, other = activation._check_contamination(
            rec, vendor, set(installed), builtins.get(vendor, []), tool_role="task" if task else "activation")
        capture_error = info.get("evidence", {}).get("error")
        if capture_error:
            reasons.append(capture_error)
        if not installed and installed_name in rec.activated:
            reasons.append("Control loaded the evaluated skill.")
        row = {"trace": dataclasses.asdict(rec), "valid": rec.ok and not reasons,
               "invalid_reasons": reasons + ([rec.error] if not rec.ok else []),
               "workspace_sha": info.get("workspace_sha"), "foreign_skills": foreign,
               "outside_reads": other, "findings": [dataclasses.asdict(f) for f in findings],
               "artifacts": info.get("evidence", {}).get("artifacts", {})}
        if task:
            row["evidence_dir"] = str(destination.relative_to(run_dir))
            output = _judge_text(row)
            if not installed and any(re.search(m, output) for m in task["control_markers"]):
                row["valid"] = False
                row["invalid_reasons"].append("Control fingerprint found.")
            if installed and plan["mode"] == "explicit" and installed_name not in rec.activated:
                row["valid"] = False
                row["invalid_reasons"].append("Explicit treatment did not load the skill.")
            if row["valid"]:
                row["checks"] = objective_checks(rec.text, row["artifacts"], task["checks"], destination)
        return row

    def complete(vendor, prompt, **kwargs):
        budget.reserve()
        kwargs["timeout"] = timeout
        text, rec = vendors.complete(vendor, prompt, **kwargs)
        budget.record(rec)
        return text, rec

    try:
        for vendor, model in plan["vendors"].items():
            try:
                row = execute(vendor, model, "Say OK and do nothing else.", {}, f"baseline-{vendor}")
                rec = row["trace"]
                builtins[vendor] = rec["visible_skills"] or list(vendors.KNOWN_BUILTINS[vendor])
                if installed_name in builtins[vendor]:
                    baseline_errors[vendor] = ("Evaluated skill collides with a vendor built-in; "
                                               "rerun with --install-as <other-name>.")
                if not row["valid"] or vendor == "claude" and rec["visible_skills"] is None:
                    baseline_errors[vendor] = "Built-in baseline failed or was contaminated."
                common.append_jsonl(run_dir / "baselines.jsonl", {"vendor": vendor, **row})
            except BudgetExceeded:
                raise
            except Exception as exc:
                baseline_errors[vendor] = str(exc)
                common.append_jsonl(run_dir / "baselines.jsonl", {"vendor": vendor, "error": str(exc)})
        rng = random.Random(seed)
        plan.setdefault("adaptive_skipped", [])

        def jobs():
            # One round per repeat. Adaptive runs drop, after the first round,
            # the tasks whose every claim is already decided for that vendor.
            for repeat in range(plan["repeats"]):
                decided = {v: _decided_claims(plan, pairs, v) for v in plan["vendors"]} \
                    if plan.get("adaptive") and repeat else {}
                round_jobs = []
                for vendor in plan["vendors"]:
                    for task in plan["tasks"]:
                        if task.get("claims") and set(task["claims"]) <= decided.get(vendor, set()):
                            plan["adaptive_skipped"].append([vendor, task["id"], repeat])
                        else:
                            round_jobs.append((vendor, task, repeat))
                rng.shuffle(round_jobs)
                yield from round_jobs

        for vendor, task, repeat in jobs():
            pair = {"vendor": vendor, "task_id": task["id"], "repeat": repeat,
                    "valid": False, "arms": {}, "judge_vendor": None}
            arms = ["without", "with"]
            rng.shuffle(arms)
            pair["execution_order"] = arms
            for arm in arms:
                try:
                    if vendor in baseline_errors:
                        raise RuntimeError(baseline_errors[vendor])
                    installed = {installed_name: skill_snapshot} if arm == "with" else {}
                    prompt = task["prompt"]
                    if arm == "with" and plan["mode"] == "explicit":
                        prompt = f"Use the {installed_name} skill for this task.\n\n{prompt}"
                    pair["arms"][arm] = execute(vendor, plan["vendors"][vendor], prompt, installed,
                                                f"{task['id']}-{repeat}-{arm}-{vendor}", task)
                except Exception as exc:
                    pair["arms"][arm] = {"valid": False, "invalid_reasons": [str(exc)],
                                           "trace": dataclasses.asdict(common.TraceRecord(vendor=vendor, ok=False, error=str(exc)))}
            pair["valid"] = all(row["valid"] for row in pair["arms"].values())
            hashes = {row.get("workspace_sha") for row in pair["arms"].values()}
            if pair["valid"] and (len(hashes) != 1 or None in hashes):
                pair["valid"] = False
                pair["error"] = "Workspace fixtures differed between arms."
            if pair["valid"] and plan["judge_vendor"] != "none":
                jv = ("codex" if vendor == "claude" else "claude") if plan["judge_vendor"] == "cross" else plan["judge_vendor"]
                pair["judge_vendor"] = jv
                try:
                    kwargs = dict(judge_vendor=jv, judge_model=plan["judge_models"][jv],
                                  skill_names=names, complete=complete, effort=effort)
                    judge_pair(pair, task, grading=plan.get("grading", "separate"), judge_kwargs=kwargs,
                               run_dir=run_dir, label=f"{task['id']}-{vendor}-{repeat}", rng=rng)
                except BudgetExceeded:
                    raise
                except Exception as exc:
                    pair["grading_error"] = str(exc)
            pairs.append(pair)
            common.append_jsonl(run_dir / "pairs.jsonl", pair)
            print(f"{vendor}/{task['id']}/{repeat + 1}: {'valid' if pair['valid'] else 'invalid'}", file=sys.stderr)
    except BudgetExceeded as exc:
        plan["stop_reason"] = str(exc)
        (run_dir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    except KeyboardInterrupt:
        print(f"Interrupted run records: {run_dir}", file=sys.stderr)
        raise
    finally:
        (run_dir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
        (run_dir / "budget.json").write_text(json.dumps(dataclasses.asdict(budget), indent=2), encoding="utf-8")
        write_summary(run_dir, summarize(plan, pairs, budget))
    return run_dir


def _positive_int(raw):
    value = int(raw)
    if value < 1:
        raise argparse.ArgumentTypeError("Value must be a positive integer.")
    return value


def _positive_float(raw):
    value = float(raw)
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError("Value must be a finite positive number.")
    return value


def _models(raw):
    models = dict(vendors.DEFAULT_MODELS)
    if raw:
        for entry in raw.split(","):
            vendor, sep, model = entry.partition("=")
            if not sep or vendor not in common.VENDORS or not model.strip():
                raise ValueError("Models use claude=MODEL,codex=MODEL.")
            models[vendor] = model.strip()
    return models


def _cmd_run(args):
    try:
        card = load_card(args.suite.resolve())
        tasks = card["tasks"]
        selected_claims = None
        if args.claims:
            if card["version"] != 2:
                raise ValueError("--claims needs a version 2 card.")
            selected_claims = args.claims.split(",")
            unknown = set(selected_claims) - {c["id"] for c in card["claims"]}
            if unknown:
                raise ValueError(f"Unknown claims: {', '.join(sorted(unknown))}")
            tasks = [t for t in tasks if set(t["claims"]) & set(selected_claims)]
        if args.adaptive and card["version"] != 2:
            raise ValueError("--adaptive needs a version 2 card: rounds stop on decided claims.")
        if not (common.skill_dir(args.skill) / "SKILL.md").is_file() or args.skill not in common.library_skills():
            raise ValueError("Select an existing library skill.")
        source_models, judge_models = _models(args.models), _models(args.judge_models or args.models)
        selected = args.vendors.split(",")
        if not selected or len(set(selected)) != len(selected) or any(v not in common.VENDORS for v in selected):
            raise ValueError("Vendors must be claude,codex or one vendor.")
        if args.judge_vendor == "none" and any(not t["checks"] for t in tasks):
            raise ValueError("Every task needs objective checks when judging is disabled.")
        for vendor in set(selected) | (set(common.VENDORS) if args.judge_vendor == "cross" else
                                       {args.judge_vendor} if args.judge_vendor != "none" else set()):
            valid_efforts = vendors.CLAUDE_EFFORT_VALUES if vendor == "claude" else vendors.CODEX_EFFORT_VALUES
            if args.effort not in valid_efforts:
                raise ValueError(f"Unsupported effort for {vendor}: {args.effort}")
        plan = plan_run(tasks, {v: source_models[v] for v in selected}, args.repeats, args.judge_vendor, args.mode,
                        args.grading)
        plan.update(card_version=card["version"], claims=card["claims"], claims_selected=selected_claims,
                    adaptive=args.adaptive)
        if args.install_as and (not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.install_as)
                                or args.install_as in common.library_skills()):
            raise ValueError("--install-as needs a lowercase hyphenated name that no library skill uses.")
        plan.update(skill=args.skill, installed_name=args.install_as or args.skill,
                    suite_sha=common.sha256_file(args.suite),
                    skill_sha=vendors._fixture_fingerprint(common.skill_dir(args.skill)),
                    judge_models=judge_models)
        if args.max_calls is not None and plan["call_count_total"] > args.max_calls:
            raise ValueError(f"Plan needs at most {plan['call_count_total']} calls. Increase --max-calls or reduce the suite.")
        if args.dry_run:
            print(json.dumps(plan, indent=2))
            return 0
        if len(selected) == 1:
            print(f"warning: evaluation deliberately narrowed to {selected[0]}.", file=sys.stderr)
        if args.judge_vendor in selected:
            print("warning: some outputs share their vendor with the judge.", file=sys.stderr)
        path = run(plan, budget=Budget(args.max_calls, args.max_cost_usd, args.max_codex_tokens),
                   timeout=args.timeout, effort=args.effort, seed=args.seed)
        print(path)
        return 3 if json.loads((path / "summary.json").read_text())["incomplete"] else 0
    except (ValueError, OSError, BudgetExceeded) as exc:
        print(f"performance: {exc}", file=sys.stderr)
        return 2 if isinstance(exc, (ValueError, OSError)) else 3


def _cmd_report(args):
    try:
        plan = json.loads((args.run_dir / "plan.json").read_text())
        pairs = list(common.read_jsonl(args.run_dir / "pairs.jsonl"))
        budget = Budget(**json.loads((args.run_dir / "budget.json").read_text()))
        summary = summarize(plan, pairs, budget)
        write_summary(args.run_dir, summary)
        print(json.dumps(summary, indent=2) if args.json else (args.run_dir / "summary.md").read_text())
        return 3 if summary["incomplete"] else 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f"performance report: {exc}", file=sys.stderr)
        return 2


def _needs_rejudge(pair: dict) -> bool:
    """A valid pair whose judging produced nothing usable: a grading error,
    every pairwise repeat void, or every grade unsupported in an arm."""
    if not pair.get("valid"):
        return False
    if pair.get("grading_error"):
        return True
    repeats = pair.get("comparison", {}).get("repeats") or []
    if not repeats or all(r.get("void") for r in repeats):
        return True
    for arm in pair["arms"].values():
        grades = arm.get("grades") or []
        if grades and all(g.get("verdict") == "unsupported" for g in grades):
            return True
    return False


def rejudge(run_dir: Path, *, budget: Budget, effort: str, timeout: int, all_pairs: bool = False) -> dict:
    """Re-run only the judges of a finished run: assertion grades and the
    pairwise comparison, for valid pairs whose judging failed (or every
    valid pair with `all_pairs`). Arm outputs are reused as recorded, so a
    judge outage costs judge calls, not a rerun. The previous pairs.jsonl
    is kept beside the new one."""
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    pairs = list(common.read_jsonl(run_dir / "pairs.jsonl"))
    # The caps given here bound this rejudge's own calls; budget.json keeps
    # the run's running total.
    prior = json.loads((run_dir / "budget.json").read_text(encoding="utf-8"))
    tasks = {t["id"]: t for t in plan["tasks"]}
    installed_name = plan.get("installed_name") or plan["skill"]
    names = sorted(set(common.library_skills()) | {installed_name} | set(judge._default_skill_names()))
    rng = random.Random(f"{plan.get('seed', 0)}-rejudge-{common.utc_now()}")

    def complete(vendor, prompt, **kwargs):
        budget.reserve()
        kwargs["timeout"] = timeout
        text, rec = vendors.complete(vendor, prompt, **kwargs)
        budget.record(rec)
        return text, rec

    done = 0
    try:
        for pair in pairs:
            if not pair.get("valid") or not (all_pairs or _needs_rejudge(pair)):
                continue
            task = tasks[pair["task_id"]]
            vendor = pair["vendor"]
            jv = pair.get("judge_vendor") or (("codex" if vendor == "claude" else "claude")
                                              if plan["judge_vendor"] == "cross" else plan["judge_vendor"])
            kwargs = dict(judge_vendor=jv, judge_model=plan["judge_models"][jv],
                          skill_names=names, complete=complete, effort=effort)
            pair.pop("grading_error", None)
            try:
                # Plans written before batched grading existed graded separately.
                judge_pair(pair, task, grading=plan.get("grading", "separate"), judge_kwargs=kwargs,
                           run_dir=run_dir, label=f"{task['id']}-{vendor}-{pair['repeat']}-rejudge", rng=rng)
            except BudgetExceeded:
                raise
            except Exception as exc:
                pair["grading_error"] = str(exc)
            pair["rejudged_at"] = common.utc_now()
            done += 1
    finally:
        backup = run_dir / f"pairs.before-rejudge-{common.run_id('bak')}.jsonl"
        shutil.copy2(run_dir / "pairs.jsonl", backup)
        (run_dir / "pairs.jsonl").write_text("".join(json.dumps(p) + "\n" for p in pairs), encoding="utf-8")
        total = Budget(prior.get("max_calls"), prior.get("max_cost_usd"), prior.get("max_codex_tokens"),
                       prior.get("calls", 0) + budget.calls, prior.get("cost_usd", 0.0) + budget.cost_usd,
                       prior.get("codex_tokens", 0) + budget.codex_tokens)
        (run_dir / "budget.json").write_text(json.dumps(dataclasses.asdict(total), indent=2), encoding="utf-8")
        write_summary(run_dir, summarize(plan, pairs, total))
    return {"rejudged": done, "judge_calls": budget.calls, "backup": str(backup)}


def _cmd_rejudge(args):
    try:
        result = rejudge(args.run_dir, budget=Budget(args.max_calls, args.max_cost_usd, args.max_codex_tokens),
                         effort=args.effort, timeout=args.timeout, all_pairs=args.all)
        print(json.dumps(result, indent=2))
        print((args.run_dir / "summary.md").read_text())
        return 3 if json.loads((args.run_dir / "summary.json").read_text())["incomplete"] else 0
    except (ValueError, OSError, KeyError, BudgetExceeded) as exc:
        print(f"performance rejudge: {exc}", file=sys.stderr)
        return 2


def _planted_evidence(sample: dict, task: dict, root: Path) -> tuple[str, dict, Path]:
    """Copy a planted output into a scratch evidence directory shaped like a
    run's, so command checks see the same layout they see in a run."""
    destination = root / common.run_id("planted")
    shutil.copytree(sample["path"], destination)
    (destination / "artifacts").mkdir(exist_ok=True)
    artifacts = {}
    for rel in task["artifacts"]:
        path = destination / "artifacts" / rel
        artifacts[rel] = path.read_text(encoding="utf-8") if path.is_file() else None
    return (destination / "output.txt").read_text(encoding="utf-8"), artifacts, destination


def validate_card(path: Path) -> list[dict]:
    """Free checks of a card against its own planted outputs. Every check
    must pass every planted good output and fail at least one planted bad
    one: a check that cannot fail certifies nothing. Returns findings with
    severity error or info."""
    card = load_card(path)
    findings = []
    if card["version"] != 2:
        return [{"severity": "error", "task": None,
                 "message": "Version 1 suites carry no planted outputs or claims. Convert to version 2."}]
    with tempfile.TemporaryDirectory() as tmp:
        for task in card["tasks"]:
            if not task["checks"]:
                continue
            goods = [p for p in task["planted"] if p["expect"] == "good"]
            bads = [p for p in task["planted"] if p["expect"] == "bad"]
            if not goods or not bads:
                findings.append({"severity": "error", "task": task["id"],
                                 "message": "Checks need at least one planted good and one planted bad output."})
                continue
            results = {}
            for sample in goods + bads:
                text, artifacts, destination = _planted_evidence(sample, task, Path(tmp))
                rows = objective_checks(text, artifacts, task["checks"], destination)
                results[sample["path"]] = {r["id"]: r["verdict"] for r in rows}
            for check in task["checks"]:
                cid = check["id"]
                for sample in goods:
                    verdict = results[sample["path"]][cid]
                    if verdict != "pass":
                        findings.append({"severity": "error", "task": task["id"],
                                         "message": f"Check {cid} gives {verdict} on planted good {Path(sample['path']).name}."})
                bad_verdicts = [results[b["path"]][cid] for b in bads]
                if "unsupported" in bad_verdicts:
                    findings.append({"severity": "error", "task": task["id"],
                                     "message": f"Check {cid} is unsupported on a planted bad output: the scorer failed."})
                if "fail" not in bad_verdicts:
                    findings.append({"severity": "error", "task": task["id"],
                                     "message": f"Check {cid} cannot fail: it passes every planted bad output."})
    checked = {c.get("claim") for t in card["tasks"] for c in t["checks"]}
    for claim in card["claims"]:
        if claim["id"] not in checked:
            findings.append({"severity": "info", "task": None,
                             "message": f"Claim {claim['id']} rests on judged assertions only."})
    return findings


def _cmd_validate(args):
    try:
        findings = validate_card(args.suite.resolve())
    except (ValueError, OSError, re.error) as exc:
        print(f"performance validate: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            print(f"{f['severity']}\t{f['task'] or '-'}\t{f['message']}")
        errors = sum(f["severity"] == "error" for f in findings)
        print(f"{errors} errors, {len(findings) - errors} info.")
    return 1 if any(f["severity"] == "error" for f in findings) else 0


def rescore(run_dir: Path, suite: Path | None = None) -> dict:
    """Rerun objective checks and scorers over a finished run's stored
    outputs. No agent or judge calls. With `suite`, its checks and claim
    tags replace the plan's for tasks with the same id. Changed assertions
    are reported, since their grades need `rejudge --all`."""
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    pairs = list(common.read_jsonl(run_dir / "pairs.jsonl"))
    tasks = {t["id"]: t for t in plan["tasks"]}
    assertions_changed = []
    if suite is not None:
        card = load_card(suite)
        fresh = {t["id"]: t for t in card["tasks"]}
        missing = set(tasks) - set(fresh)
        if missing:
            raise ValueError(f"The suite lacks tasks this run used: {', '.join(sorted(missing))}")
        for tid, task in tasks.items():
            new = fresh[tid]
            if [(a["id"], a["text"]) for a in new["assertions"]] != [(a["id"], a["text"]) for a in task["assertions"]]:
                assertions_changed.append(tid)
            task["checks"] = new["checks"]
            if tid not in assertions_changed:
                # Same requirements: only their claim tags can have moved.
                task["assertions"] = new["assertions"]
            if "claims" in new:
                task["claims"] = new["claims"]
                task["kind"] = new["kind"]
        if card["version"] == 2:
            plan["claims"] = card["claims"]
        plan.setdefault("rescored", []).append({"at": common.utc_now(), "suite_sha": common.sha256_file(suite),
                                                "assertions_changed": assertions_changed})
    rescored = 0
    with tempfile.TemporaryDirectory() as tmp:
        for pair in pairs:
            if not pair.get("valid"):
                continue
            task = tasks[pair["task_id"]]
            claim_of = {a["id"]: a.get("claim") for a in task["assertions"]}
            for arm in pair["arms"].values():
                stored = run_dir / arm["evidence_dir"] if arm.get("evidence_dir") else None
                if stored is not None and stored.is_dir():
                    destination = stored
                else:
                    # Runs recorded before evidence_dir: rebuild from the pair record.
                    destination = Path(tmp) / common.run_id("evidence")
                    collected = {k: v for k, v in (arm.get("artifacts") or {}).items()}
                    (destination / "artifacts").mkdir(parents=True)
                    (destination / "output.txt").write_text(arm["trace"]["text"], encoding="utf-8")
                    for rel, content in collected.items():
                        if content is not None:
                            target = destination / "artifacts" / rel
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_text(content, encoding="utf-8")
                arm["checks"] = objective_checks(arm["trace"]["text"], arm.get("artifacts") or {},
                                                 task["checks"], destination)
                for row in arm.get("grades", []):
                    row.pop("claim", None)
                    if claim_of.get(row["id"]):
                        row["claim"] = claim_of[row["id"]]
            rescored += 1
    backup = run_dir / f"pairs.before-rescore-{common.run_id('bak')}.jsonl"
    shutil.copy2(run_dir / "pairs.jsonl", backup)
    (run_dir / "pairs.jsonl").write_text("".join(json.dumps(p) + "\n" for p in pairs), encoding="utf-8")
    (run_dir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    budget = Budget(**json.loads((run_dir / "budget.json").read_text(encoding="utf-8")))
    write_summary(run_dir, summarize(plan, pairs, budget))
    return {"rescored_pairs": rescored, "assertions_changed": assertions_changed, "backup": str(backup)}


def _cmd_rescore(args):
    try:
        result = rescore(args.run_dir, args.suite.resolve() if args.suite else None)
    except (ValueError, OSError, KeyError, re.error) as exc:
        print(f"performance rescore: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    if result["assertions_changed"]:
        print("warning: assertions changed for " + ", ".join(result["assertions_changed"])
              + "; their grades are stale until `performance rejudge --all`.", file=sys.stderr)
    print((args.run_dir / "summary.md").read_text())
    return 3 if json.loads((args.run_dir / "summary.json").read_text())["incomplete"] else 0


def _git(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *argv], cwd=common.REPO_ROOT, capture_output=True, text=True)


def _split_skill_md(text: str | None) -> tuple[str | None, str | None]:
    if text is None:
        return None, None
    m = common._FM_RE.match(text)
    return (m.group(1), text[m.end():]) if m else ("", text)


def plan_changes(skill: str, card: dict, since: str) -> dict:
    """Which measurements a change to a skill invalidates.

    Reads the changes under `skills/<skill>/` between `since` and the
    working tree, untracked files included. A frontmatter change in
    SKILL.md invalidates activation. A SKILL.md body change and every other
    changed path map through the card's `invalidation` globs (relative to
    the skill directory) to claims. A path no glob matches invalidates every
    claim: an unmapped change is never assumed harmless."""
    rel_root = f"skills/{skill}"
    diff = _git("diff", "--name-only", since, "--", rel_root)
    if diff.returncode != 0:
        raise ValueError(f"git diff failed: {diff.stderr.strip()}")
    untracked = _git("ls-files", "--others", "--exclude-standard", "--", rel_root)
    changed = sorted({line[len(rel_root) + 1:] for line in (diff.stdout + untracked.stdout).splitlines()
                      if line.startswith(rel_root + "/")})
    activation = False
    paths = []
    for rel in changed:
        if rel != "SKILL.md":
            paths.append(rel)
            continue
        old = _git("show", f"{since}:{rel_root}/SKILL.md")
        new_path = common.skill_dir(skill) / "SKILL.md"
        old_fm, old_body = _split_skill_md(old.stdout if old.returncode == 0 else None)
        new_fm, new_body = _split_skill_md(new_path.read_text(encoding="utf-8") if new_path.is_file() else None)
        activation = old_fm != new_fm
        if old_body != new_body:
            paths.append(rel)
    all_claims = [c["id"] for c in card["claims"]]
    per_path, selected = {}, set()
    for rel in paths:
        keys = [k for k in card["invalidation"] if fnmatch.fnmatch(rel, k)]
        if not keys:
            claims, reason = all_claims, "unmapped: every claim"
        elif any(card["invalidation"][k] == "all" for k in keys):
            claims, reason = all_claims, "mapped to all"
        else:
            claims = sorted({c for k in keys for c in card["invalidation"][k]}, key=all_claims.index)
            reason = "mapped by " + ", ".join(keys)
        per_path[rel] = {"claims": claims, "reason": reason}
        selected.update(claims)
    claims = [c for c in all_claims if c in selected]
    tasks = [t for t in card["tasks"] if set(t["claims"]) & selected]
    return {"skill": skill, "since": since, "changed": changed, "activation": activation,
            "paths": per_path, "claims": claims, "tasks": [t["id"] for t in tasks]}


def _cmd_plan(args):
    try:
        card = load_card(args.suite.resolve())
        if card["version"] != 2:
            raise ValueError("plan needs a version 2 card with claims and an invalidation map.")
        if args.skill not in common.library_skills():
            raise ValueError("Select an existing library skill.")
        result = plan_changes(args.skill, card, args.since)
        selected = [v for v in args.vendors.split(",") if v]
        tasks = [t for t in card["tasks"] if t["id"] in result["tasks"]]
        result["estimated_calls"] = plan_run(tasks, {v: "" for v in selected}, args.repeats, "cross", "explicit",
                                             args.grading)["call_count_total"] if tasks else 0
        commands = []
        if result["activation"]:
            commands.append(f"python3 scripts/auditing/skill-eval.py activation run --skill {args.skill} --split train")
        if result["claims"]:
            commands.append(f"python3 scripts/auditing/skill-eval.py performance run --skill {args.skill} "
                            f"--suite {args.suite} --claims {','.join(result['claims'])} --repeats {args.repeats} --adaptive")
        result["commands"] = commands
    except (ValueError, OSError, re.error) as exc:
        print(f"performance plan: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Changed under skills/{args.skill} since {args.since}: {', '.join(result['changed']) or 'nothing'}")
        print(f"Activation invalidated: {'yes' if result['activation'] else 'no'}")
        for rel, item in result["paths"].items():
            print(f"  {rel}: {', '.join(item['claims'])} ({item['reason']})")
        print(f"Claims to rerun: {', '.join(result['claims']) or 'none'}")
        print(f"Tasks: {', '.join(result['tasks']) or 'none'}. Estimated calls at most: {result['estimated_calls']}")
        for command in result["commands"]:
            print(command)
    return 0


def add_subparser(subparsers):
    parser = subparsers.add_parser("performance", help=__doc__)
    sub = parser.add_subparsers(dest="subcommand", required=True)
    cmd = sub.add_parser("run", help="Compare the same tasks with and without a skill.")
    cmd.add_argument("--skill", required=True)
    cmd.add_argument("--suite", type=Path, required=True)
    cmd.add_argument("--vendors", default="claude,codex")
    cmd.add_argument("--models")
    cmd.add_argument("--judge-models")
    cmd.add_argument("--judge-vendor", choices=("cross", "claude", "codex", "none"), default="cross")
    cmd.add_argument("--mode", choices=("explicit", "natural"), default="explicit")
    cmd.add_argument("--repeats", type=_positive_int, default=DEFAULT_REPEATS)
    cmd.add_argument("--timeout", type=_positive_int, default=600)
    cmd.add_argument("--effort", default="medium")
    cmd.add_argument("--seed", type=int, default=0)
    cmd.add_argument("--max-calls", type=_positive_int)
    cmd.add_argument("--max-cost-usd", type=_positive_float)
    cmd.add_argument("--max-codex-tokens", type=_positive_int)
    cmd.add_argument("--install-as", default=None,
                     help="install the skill under this name (for a name that collides with a vendor built-in)")
    cmd.add_argument("--grading", choices=GRADING_MODES, default="batched",
                     help="batched: two judge calls per pair; separate: one per assertion per output plus two")
    cmd.add_argument("--claims", help="version 2 cards: run only the tasks probing these claims (comma-separated)")
    cmd.add_argument("--adaptive", action="store_true",
                     help="version 2 cards: after the first round, skip tasks whose claims are already decided")
    cmd.add_argument("--dry-run", action="store_true")
    cmd.set_defaults(func=_cmd_run)
    cmd = sub.add_parser("validate", help="Check a card's checks against its planted good and bad outputs. Free.")
    cmd.add_argument("--suite", type=Path, required=True)
    cmd.add_argument("--json", action="store_true")
    cmd.set_defaults(func=_cmd_validate)
    cmd = sub.add_parser("rescore", help="Rerun objective checks over a finished run's outputs. Free.")
    cmd.add_argument("run_dir", type=Path)
    cmd.add_argument("--suite", type=Path, help="take checks and claim tags from this suite")
    cmd.set_defaults(func=_cmd_rescore)
    cmd = sub.add_parser("plan", help="List the claims and runs a change to a skill invalidates. Free.")
    cmd.add_argument("--skill", required=True)
    cmd.add_argument("--suite", type=Path, required=True)
    cmd.add_argument("--since", default="HEAD", help="git ref to compare the working tree against (default HEAD)")
    cmd.add_argument("--repeats", type=_positive_int, default=DEFAULT_REPEATS)
    cmd.add_argument("--vendors", default="claude,codex")
    cmd.add_argument("--grading", choices=GRADING_MODES, default="batched")
    cmd.add_argument("--json", action="store_true")
    cmd.set_defaults(func=_cmd_plan)
    cmd = sub.add_parser("report", help="Rebuild quality metrics from saved pairs.")
    cmd.add_argument("run_dir", type=Path)
    cmd.add_argument("--json", action="store_true")
    cmd.set_defaults(func=_cmd_report)
    rj = sub.add_parser("rejudge", help="Re-run only the judges of a finished run, for pairs whose judging failed.")
    rj.add_argument("run_dir", type=Path)
    rj.add_argument("--all", action="store_true", help="re-judge every valid pair, not only failed ones")
    rj.add_argument("--effort", default="medium")
    rj.add_argument("--timeout", type=_positive_int, default=600)
    rj.add_argument("--max-calls", type=_positive_int)
    rj.add_argument("--max-cost-usd", type=_positive_float)
    rj.add_argument("--max-codex-tokens", type=_positive_int)
    rj.set_defaults(func=_cmd_rejudge)
