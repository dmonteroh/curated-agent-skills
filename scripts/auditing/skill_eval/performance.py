"""Compare task quality with and without a skill on both vendors."""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import os
import random
import re
import shutil
import stat
import subprocess
import sys
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


def load_suite(path: Path) -> list[dict]:
    """Validate task data before any agent calls."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != 1:
        raise ValueError("Suite version must be 1.")
    if set(data) - {"version", "tasks"}:
        raise ValueError("Unknown suite fields.")
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Suite tasks must be a nonempty list.")
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or set(task) - {
            "id", "prompt", "workspace", "artifacts", "checks", "assertions", "control_markers"
        }:
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
            elif isinstance(assertion, dict) and set(assertion) == {"id", "text"}:
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
            if not isinstance(check, dict) or set(check) - {"id", "kind", "target", "value", "argv", "metrics"}:
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
    return tasks


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


def plan_run(tasks, models, repeats, judge_vendor, mode):
    pairs = len(tasks) * len(models) * repeats
    grading = sum(2 + 2 * len(t["assertions"]) for t in tasks) * len(models) * repeats
    return {"vendors": models, "repeats": repeats, "mode": mode, "judge_vendor": judge_vendor,
            "tasks": tasks, "baseline_calls": len(models), "arm_calls": pairs * 2,
            "judge_calls": grading if judge_vendor != "none" else 0,
            "call_count_total": len(models) + pairs * 2 + (grading if judge_vendor != "none" else 0)}


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
            row = {"vendor": vendor, "task_id": task["id"], "pairs": len(selected),
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
    return {"skill": plan["skill"], "mode": plan["mode"], "rows": rows,
            "calls": budget.calls, "claude_cost_usd": budget.cost_usd,
            "codex_tokens": budget.codex_tokens,
            "incomplete": any(r["pairs"] != plan["repeats"] or r["invalid_pairs"] for r in rows)
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
        jobs = [(vendor, task, repeat) for vendor in plan["vendors"] for task in plan["tasks"]
                for repeat in range(plan["repeats"])]
        rng.shuffle(jobs)
        for vendor, task, repeat in jobs:
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
                    order = ["without", "with"]
                    rng.shuffle(order)
                    for arm in order:
                        pair["arms"][arm]["grades"] = judge.grade(task["prompt"], _judge_text(pair["arms"][arm]), task["assertions"], **kwargs)
                    pair["comparison"] = judge.pairwise(task["prompt"], _judge_text(pair["arms"]["without"]),
                                                        _judge_text(pair["arms"]["with"]), repeats=2,
                                                        run_dir=run_dir / "judgements" / f"{task['id']}-{vendor}-{repeat}",
                                                        seed=rng.randrange(2**32), **kwargs)
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
        tasks = load_suite(args.suite.resolve())
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
        plan = plan_run(tasks, {v: source_models[v] for v in selected}, args.repeats, args.judge_vendor, args.mode)
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
                order = ["without", "with"]
                rng.shuffle(order)
                for arm in order:
                    pair["arms"][arm]["grades"] = judge.grade(task["prompt"], _judge_text(pair["arms"][arm]),
                                                              task["assertions"], **kwargs)
                pair["comparison"] = judge.pairwise(task["prompt"], _judge_text(pair["arms"]["without"]),
                                                    _judge_text(pair["arms"]["with"]), repeats=2,
                                                    run_dir=run_dir / "judgements" / f"{task['id']}-{vendor}-{pair['repeat']}-rejudge",
                                                    seed=rng.randrange(2**32), **kwargs)
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
    cmd.add_argument("--dry-run", action="store_true")
    cmd.set_defaults(func=_cmd_run)
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
