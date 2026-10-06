"""Regression coverage for paired task evaluation without live calls."""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "auditing"))
from skill_eval import activation, common, performance as perf, vendors


def task(**overrides):
    return dict(id="task", prompt="Write a useful note.", workspace="empty", artifacts=[],
                checks=[{"id": "fact", "kind": "contains", "value": "stable"}],
                assertions=[{"id": "useful", "text": "The note is useful."}], control_markers=[], **overrides)


class SuiteTests(unittest.TestCase):
    def load(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "suite.json"
            path.write_text(json.dumps(data))
            return perf.load_suite(path)

    def test_minimal_suite_normalizes_assertions_and_defaults(self):
        result = self.load({"version": 1, "tasks": [{"id": "one", "prompt": "Do work.", "assertions": ["Preserves facts."]}]})
        self.assertEqual(result[0]["assertions"], [{"id": "assertion-1", "text": "Preserves facts."}])
        self.assertEqual(result[0]["workspace"], "empty")

    def test_invalid_suites_fail_before_calls(self):
        cases = [
            [], {"version": True, "tasks": [task()]}, {"version": 2, "tasks": [task()]}, {"version": 1, "tasks": []},
            {"version": 1, "tasks": [task()], "typo": True},
            {"version": 1, "tasks": [task(), task()]},
        ]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.load(data)

    def test_task_validation_rejects_unsafe_or_ambiguous_data(self):
        overrides = [
            {"id": "../escape"}, {"prompt": ""}, {"checks": [], "assertions": []},
            {"artifacts": ["/absolute"]}, {"artifacts": ["../outside"]},
            {"artifacts": ["a/../b"]}, {"artifacts": ["a//b"]}, {"artifacts": ["a", "a"]},
            {"checks": [{"id": "r", "kind": "regex", "value": "["}]},
            {"checks": [{"id": "f", "kind": "file_exists"}]},
            {"checks": [{"id": "f", "kind": "contains", "target": "missing", "value": "a"}]},
            {"checks": [{"id": "c", "kind": "command", "argv": "echo pass"}]},
            {"assertions": [{"id": "a", "text": "x"}, {"id": "a", "text": "y"}]},
            {"control_markers": ["["]}, {"typo": 1},
            {"checks": [{"id": "m", "kind": "command", "argv": ["test"], "metrics": {"a": {"path": "a", "direction": "wrong"}}}]},
            {"checks": [{"id": "m", "kind": "contains", "value": "a", "metrics": {}}]},
        ]
        for override in overrides:
            with self.subTest(override=override), self.assertRaises((ValueError, perf.re.error)):
                self.load({"version": 1, "tasks": [{**task(), **override}]})

    def test_fixture_is_relative_to_suite_and_instruction_files_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "fixture").mkdir()
            (root / "fixture" / "data.txt").write_text("input")
            path = root / "suite.json"
            path.write_text(json.dumps({"version": 1, "tasks": [{**task(), "workspace": "fixture"}]}))
            self.assertEqual(perf.load_suite(path)[0]["workspace"], str(root / "fixture"))
            (root / "fixture" / "CLAUDE.md").write_text("contamination")
            with self.assertRaises(ValueError):
                perf.load_suite(path)

    def test_fixture_symlinks_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "fixture").mkdir()
            (root / "outside").write_text("data")
            (root / "fixture" / "link").symlink_to(root / "outside")
            path = root / "suite.json"
            path.write_text(json.dumps({"version": 1, "tasks": [{**task(), "workspace": "fixture"}]}))
            with self.assertRaises(ValueError):
                perf.load_suite(path)


class ScoringTests(unittest.TestCase):
    def test_objective_checks_can_pass_and_fail(self):
        checks = [{"id": "yes", "kind": "contains", "value": "stable"},
                  {"id": "no", "kind": "not_contains", "value": "promise"},
                  {"id": "regex", "kind": "regex", "value": r"\b3\b"},
                  {"id": "file", "kind": "file_exists", "target": "note.txt"}]
        clean = perf.objective_checks("stable 3", {"note.txt": ""}, checks, Path("/unused"))
        bad = perf.objective_checks("promise 4", {"note.txt": None}, checks, Path("/unused"))
        self.assertEqual([r["verdict"] for r in clean], ["pass"] * 4)
        self.assertEqual([r["verdict"] for r in bad], ["fail"] * 4)

    def test_missing_artifact_fails_even_a_negative_check(self):
        checks = [{"id": "missing", "kind": "not_contains", "target": "file", "value": "bad"}]
        result = perf.objective_checks("fine", {"file": None}, checks, Path("/unused"))
        self.assertEqual(result[0]["verdict"], "fail")

    def test_artifacts_are_captured_without_following_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cwd, dest = root / "cwd", root / "dest"
            cwd.mkdir()
            (cwd / "note.txt").write_text("stable")
            t = {**task(), "artifacts": ["note.txt", "absent"]}
            result = perf.collect_evidence(cwd, "final", t, dest)
            self.assertEqual(result["artifacts"], {"note.txt": "stable", "absent": None})
            self.assertEqual((dest / "output.txt").read_text(), "final")
            (cwd / "note.txt").unlink()
            (cwd / "note.txt").symlink_to(dest / "output.txt")
            with self.assertRaises(ValueError):
                perf.collect_evidence(cwd, "final", t, dest)

    def test_oversize_evidence_is_invalid(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(perf, "MAX_EVIDENCE_BYTES", 3):
            with self.assertRaises(ValueError):
                perf.collect_evidence(Path(directory), "four", task(), Path(directory) / "dest")

    def test_command_adapter_receives_neutral_paths_and_no_parent_secrets(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(os.environ, {"PARENT_SECRET": "hidden"}):
            dest = Path(directory)
            (dest / "artifacts").mkdir()
            (dest / "output.txt").write_text("stable")
            code = "import os,pathlib,sys; assert 'PARENT_SECRET' not in os.environ; sys.exit(0 if pathlib.Path(sys.argv[1]).read_text()=='stable' else 1)"
            check = {"id": "adapter", "kind": "command", "argv": [sys.executable, "-c", code, "{output}"]}
            self.assertEqual(perf.objective_checks("", {}, [check], dest)[0]["verdict"], "pass")
            (dest / "output.txt").write_text("wrong")
            self.assertEqual(perf.objective_checks("", {}, [check], dest)[0]["verdict"], "fail")
            check["argv"] = [sys.executable, "-c", "raise SystemExit(2)"]
            self.assertEqual(perf.objective_checks("", {}, [check], dest)[0]["verdict"], "unsupported")

    def test_command_metrics_reject_missing_and_non_numeric_values(self):
        check = {"id": "score", "kind": "command", "argv": ["fixture"],
                 "metrics": {"violations": {"path": "summary.violations", "direction": "lower"}}}
        for value in ["bad", True, float("nan")]:
            proc = subprocess.CompletedProcess([], 0, json.dumps({"summary": {"violations": value}}), "")
            with mock.patch.object(perf.subprocess, "run", return_value=proc):
                result = perf.objective_checks("", {}, [check], Path("/unused"))
                self.assertEqual(result[0]["verdict"], "unsupported")
        proc = subprocess.CompletedProcess([], 1, '{"summary":{"violations":2.5}}', "")
        with mock.patch.object(perf.subprocess, "run", return_value=proc):
            result = perf.objective_checks("", {}, [check], Path("/unused"))
            self.assertEqual(result[0]["verdict"], "fail")
            self.assertEqual(result[0]["metrics"]["violations"]["value"], 2.5)

    def test_command_timeout_is_unsupported(self):
        with mock.patch.object(perf.subprocess, "run", side_effect=perf.subprocess.TimeoutExpired("test", 60)):
            result = perf.objective_checks("", {}, [{"id": "c", "kind": "command", "argv": ["test"]}], Path("/unused"))
            self.assertEqual(result[0]["verdict"], "unsupported")


class BudgetPlanTests(unittest.TestCase):
    def test_default_two_vendor_plan_includes_every_paid_call(self):
        plan = perf.plan_run([task()], {"claude": "haiku", "codex": "luna"}, 4, "cross", "explicit")
        self.assertEqual(plan["baseline_calls"], 2)
        self.assertEqual(plan["arm_calls"], 16)
        self.assertEqual(plan["judge_calls"], 32)
        self.assertEqual(plan["call_count_total"], 50)

    def test_objective_only_plan_omits_judging(self):
        plan = perf.plan_run([task()], {"claude": "haiku", "codex": "luna"}, 1, "none", "natural")
        self.assertEqual(plan["call_count_total"], 6)

    def test_cost_units_are_separate_and_guards_stop_next_call(self):
        budget = perf.Budget(max_calls=3, max_cost_usd=0.1, max_codex_tokens=20)
        budget.reserve()
        budget.record(common.TraceRecord(vendor="claude", cost_usd=0.1))
        self.assertEqual(budget.codex_tokens, 0)
        with self.assertRaises(perf.BudgetExceeded):
            budget.reserve()
        budget = perf.Budget(max_codex_tokens=20)
        budget.record(common.TraceRecord(vendor="codex", tokens={"input": 15, "cached_input": 10, "output": 5}))
        self.assertEqual(budget.codex_tokens, 20)
        self.assertEqual(budget.cost_usd, 0)
        with self.assertRaises(perf.BudgetExceeded):
            budget.reserve()
        budget = perf.Budget(max_calls=1)
        budget.reserve()
        with self.assertRaises(perf.BudgetExceeded):
            budget.reserve()

    def test_budget_accepts_legacy_token_keys_and_missing_usage(self):
        budget = perf.Budget()
        budget.record(common.TraceRecord(vendor="codex", tokens={"input_tokens": 3, "output_tokens": 2}))
        budget.record(common.TraceRecord(vendor="codex", tokens={"input": None, "output": None}))
        self.assertEqual(budget.codex_tokens, 5)

    def test_cli_rejects_invalid_numbers(self):
        parser = argparse.ArgumentParser()
        perf.add_subparser(parser.add_subparsers())
        for flag, value in [("--repeats", "0"), ("--repeats", "3.7"), ("--max-cost-usd", "nan"), ("--max-cost-usd", "-1")]:
            with self.subTest(flag=flag, value=value), self.assertRaises(SystemExit):
                parser.parse_args(["performance", "run", "--skill", "demo", "--suite", "unused", flag, value])


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skills = self.root / "skills"
        (self.skills / "demo").mkdir(parents=True)
        (self.skills / "demo" / "SKILL.md").write_text('---\nname: demo\ndescription: "Write notes."\n---\nUse facts.\n')
        for obj, name, value in [(common, "RUNS_DIR", self.root / "runs"), (common, "SKILLS_DIR", self.skills)]:
            patch = mock.patch.object(obj, name, value)
            patch.start()
            self.addCleanup(patch.stop)
        self.calls = []
        self.activate = True
        self.bad_control = False
        self.baseline_ok = True
        self.new_builtin = False
        self.judge_failure = False
        self.collect_error = False
        self.mismatch = False
        self.complete_calls = []
        for patch in [mock.patch.object(activation, "_execute_one", side_effect=self.execute),
                      mock.patch.object(vendors, "cli_version", return_value="fixture"),
                      mock.patch.object(vendors, "complete", side_effect=self.complete),
                      mock.patch.object(perf.judge, "_default_skill_names", return_value=("demo",))]:
            patch.start()
            self.addCleanup(patch.stop)

    def plan(self, mode="explicit", jv="cross", tasks=None):
        tasks = tasks or [task()]
        plan = perf.plan_run(tasks, {"claude": "haiku", "codex": "luna"}, 1, jv, mode)
        return dict(plan, skill="demo", skill_sha=vendors._fixture_fingerprint(self.skills / "demo"),
                    judge_models={"claude": "haiku", "codex": "luna"})

    def execute(self, **kwargs):
        self.calls.append(kwargs)
        installed = bool(kwargs["skills_map"])
        baseline = kwargs["label"].startswith("baseline")
        visible = (["new-builtin"] if self.new_builtin else []) + (["demo"] if installed else [])
        rec = common.TraceRecord(vendor=kwargs["vendor"], ok=self.baseline_ok if baseline else True,
                                 activated=["demo"] if installed and self.activate else [],
                                 visible_skills=visible if kwargs["vendor"] == "claude" else None,
                                 visible_tools=(vendors.CLAUDE_ARM_TOOLS if baseline else vendors.CLAUDE_TASK_TOOLS).split(",")
                                               if kwargs["vendor"] == "claude" else None,
                                 text="stable helpful note" if installed else "ordinary note",
                                 cost_usd=0.01 if kwargs["vendor"] == "claude" else None,
                                 tokens={"input_tokens": 10, "output_tokens": 2} if kwargs["vendor"] == "codex" else None)
        if self.bad_control and not installed and not baseline:
            rec.outside_reads = [str(common.REPO_ROOT / "skills/demo/SKILL.md")]
        info = {"workspace_sha": "fixture-with" if self.mismatch and installed else "fixture"}
        if kwargs["collect"]:
            cwd = self.root / common.run_id("workspace")
            cwd.mkdir()
            if self.collect_error:
                (cwd / "answer.txt").symlink_to(self.skills / "demo/SKILL.md")
            else:
                (cwd / "answer.txt").write_text("stable artifact")
            info["evidence"] = kwargs["collect"](cwd, rec.text)
        return rec, info, []

    def complete(self, vendor, prompt, **kwargs):
        self.complete_calls.append((vendor, prompt, kwargs))
        if self.judge_failure:
            raise RuntimeError("judge failed")
        if "Requirement:" in prompt:
            text = json.dumps({"verdict": "pass", "quote": "stable helpful note", "reason": "Useful."})
            if "ordinary note" in prompt:
                text = json.dumps({"verdict": "fail", "quote": "NO RELEVANT CONTENT", "reason": "Missing."})
        else:
            first = prompt.find("stable helpful note") < prompt.find("ordinary note")
            text = json.dumps({"winner": "1" if first else "2", "reason": "More useful."})
        return text, common.TraceRecord(vendor=vendor, cost_usd=0.01 if vendor == "claude" else None,
                                       tokens={"input_tokens": 3, "output_tokens": 2} if vendor == "codex" else None)

    def run_plan(self, plan=None, budget=None):
        return perf.run(plan or self.plan(), budget=budget or perf.Budget(), timeout=10, effort="medium", seed=7)

    def summary(self, directory):
        return json.loads((directory / "summary.json").read_text())

    def test_run_is_paired_cross_vendor_and_blind(self):
        directory = self.run_plan()
        result = self.summary(directory)
        self.assertFalse(result["incomplete"])
        self.assertEqual(result["calls"], 14)
        self.assertEqual(len(self.calls), 6)
        self.assertEqual(len(self.complete_calls), 8)
        for row in result["rows"]:
            self.assertEqual(row["checks"]["delta"], 1)
            self.assertEqual(row["grades"]["delta"], 1)
            self.assertEqual(row["pairwise"], {"with": 1})
        pairs = list(common.read_jsonl(directory / "pairs.jsonl"))
        self.assertEqual({(p["vendor"], p["judge_vendor"]) for p in pairs}, {("claude", "codex"), ("codex", "claude")})
        for _, prompt, _ in self.complete_calls:
            self.assertNotIn("demo", prompt)
            self.assertNotIn("with-skill", prompt)
        sources = [call["skills_map"]["demo"] for call in self.calls if call["skills_map"]]
        self.assertEqual(len(set(sources)), 1)
        self.assertNotEqual(sources[0], self.skills / "demo")

    def test_control_contamination_excludes_entire_pair(self):
        self.bad_control = True
        directory = self.run_plan()
        self.assertTrue(self.summary(directory)["incomplete"])
        self.assertEqual(self.complete_calls, [])
        for row in self.summary(directory)["rows"]:
            self.assertEqual(row["valid_pairs"], 0)
            self.assertIsNone(row["checks"]["delta"])

    def test_explicit_inactive_treatment_is_invalid_but_natural_is_measured(self):
        self.activate = False
        directory = self.run_plan()
        self.assertTrue(self.summary(directory)["incomplete"])
        directory = self.run_plan(self.plan(mode="natural"))
        self.assertFalse(self.summary(directory)["incomplete"])
        for row in self.summary(directory)["rows"]:
            self.assertEqual(row["activation_count"], 0)
        natural_calls = self.calls[-6:]
        self.assertEqual({call["prompt"] for call in natural_calls if not call["label"].startswith("baseline")}, {task()["prompt"]})

    def test_failed_baselines_keep_both_vendors_and_skip_quality(self):
        self.baseline_ok = False
        directory = self.run_plan()
        result = self.summary(directory)
        self.assertEqual({r["vendor"] for r in result["rows"]}, {"claude", "codex"})
        self.assertTrue(result["incomplete"])
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.complete_calls, [])

    def test_new_non_namespaced_builtin_is_measured_before_arm_validation(self):
        self.new_builtin = True
        directory = self.run_plan()
        self.assertFalse(self.summary(directory)["incomplete"])

    def test_artifact_collection_failure_keeps_cost_and_invalidates_pair(self):
        self.collect_error = True
        t = {**task(), "artifacts": ["answer.txt"]}
        directory = self.run_plan(self.plan(tasks=[t]))
        result = self.summary(directory)
        self.assertTrue(result["incomplete"])
        self.assertAlmostEqual(result["claude_cost_usd"], 0.03)
        self.assertEqual(result["calls"], 6)
        self.assertEqual(self.complete_calls, [])

    def test_mismatched_fixtures_are_not_compared(self):
        self.mismatch = True
        directory = self.run_plan()
        self.assertTrue(self.summary(directory)["incomplete"])
        self.assertEqual(self.complete_calls, [])

    def test_judge_failure_is_incomplete_and_never_becomes_a_tie(self):
        self.judge_failure = True
        directory = self.run_plan()
        result = self.summary(directory)
        self.assertTrue(result["incomplete"])
        for row in result["rows"]:
            self.assertEqual(row["pairwise"], {"void": 1})
            self.assertIsNone(row["grades"]["delta"])

    def test_baseline_budget_stop_returns_saved_incomplete_report(self):
        directory = self.run_plan(budget=perf.Budget(max_cost_usd=0.001))
        result = self.summary(directory)
        self.assertTrue(result["incomplete"])
        self.assertEqual(result["calls"], 1)
        self.assertIn("stop_reason", json.loads((directory / "plan.json").read_text()))
        self.assertEqual({row["vendor"] for row in result["rows"]}, {"claude", "codex"})

    def test_runtime_budget_keeps_unrun_pairs_visible(self):
        directory = self.run_plan(budget=perf.Budget(max_calls=3))
        result = self.summary(directory)
        self.assertEqual(result["calls"], 3)
        self.assertTrue(result["incomplete"])
        self.assertEqual(len(self.complete_calls), 0)
        self.assertEqual(len(list(common.read_jsonl(directory / "pairs.jsonl"))), 2)

    def test_numeric_metrics_report_direction_and_paired_improvement(self):
        code = "import json,pathlib,sys; text=pathlib.Path(sys.argv[1]).read_text(); print(json.dumps({'summary':{'violations':0 if 'stable' in text else 2}}))"
        check = {"id": "lint", "kind": "command", "argv": [sys.executable, "-c", code, "{output}"],
                 "metrics": {"violations": {"path": "summary.violations", "direction": "lower"}}}
        t = {**task(), "checks": [check]}
        directory = self.run_plan(self.plan(tasks=[t]))
        result = self.summary(directory)
        for row in result["rows"]:
            metric = row["metrics"]["lint/violations"]
            self.assertEqual(metric["delta"], -2)
            self.assertEqual(metric["improvement"], 2)
            self.assertEqual(metric["supported_pairs"], 1)
        self.assertIn("lint/violations", (directory / "summary.md").read_text())

    def test_report_recomputes_metrics_from_records(self):
        directory = self.run_plan()
        before = self.summary(directory)
        (directory / "summary.json").write_text("{}")
        with mock.patch("sys.stdout"):
            status = perf._cmd_report(argparse.Namespace(run_dir=directory, json=True))
        self.assertEqual(status, 0)
        self.assertEqual(self.summary(directory), before)

    def test_dry_run_and_insufficient_call_cap_make_no_calls(self):
        suite = self.root / "suite.json"
        suite.write_text(json.dumps({"version": 1, "tasks": [task()]}))
        parser = argparse.ArgumentParser()
        perf.add_subparser(parser.add_subparsers())
        args = parser.parse_args(["performance", "run", "--skill", "demo", "--suite", str(suite), "--repeats", "1", "--dry-run"])
        with mock.patch("sys.stdout"):
            self.assertEqual(args.func(args), 0)
        args.max_calls = 1
        with mock.patch("sys.stderr"):
            self.assertEqual(args.func(args), 2)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.complete_calls, [])

    def test_no_judge_requires_objective_checks(self):
        suite = self.root / "suite.json"
        suite.write_text(json.dumps({"version": 1, "tasks": [{**task(), "checks": []}]}))
        parser = argparse.ArgumentParser()
        perf.add_subparser(parser.add_subparsers())
        args = parser.parse_args(["performance", "run", "--skill", "demo", "--suite", str(suite), "--judge-vendor", "none", "--dry-run"])
        with mock.patch("sys.stderr"):
            self.assertEqual(args.func(args), 2)
        self.assertEqual(self.calls, [])


class CliIntegrationTests(unittest.TestCase):
    def test_real_entry_and_vendor_layer_with_fixture_clients(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bindir = root / "bin"
            bindir.mkdir()
            auditing = Path(__file__).resolve().parent.parent / "auditing"
            stub = auditing / "skill_eval/fixtures/performance/agent_stub.py"
            for name in ("claude", "codex"):
                client = bindir / name
                shutil.copy2(stub, client)
                client.chmod(0o755)
            suite = root / "suite.json"
            suite.write_text(json.dumps({"version": 1, "tasks": [task()]}))
            neutral_home = root / "home"
            neutral_home.mkdir()
            env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ["PATH"],
                       HOME=str(neutral_home), SKILL_EVAL_SCRATCH=str(root / "scratch"),
                       SKILL_EVAL_RUNS_DIR=str(root / "runs"), PARENT_SECRET="must-not-reach-client",
                       CLAUDE_CODE_MESSAGING_TOKEN="must-not-reach-client")
            proc = subprocess.run([sys.executable, str(auditing / "skill-eval.py"), "performance", "run",
                                   "--skill", "writing-style", "--suite", str(suite), "--repeats", "1",
                                   "--max-calls", "14"], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            result_dir = Path(proc.stdout.strip())
            summary = json.loads((result_dir / "summary.json").read_text())
            self.assertEqual(summary["calls"], 14)
            self.assertEqual(summary["codex_tokens"], 84)
            self.assertAlmostEqual(summary["claude_cost_usd"], 0.07)
            for row in summary["rows"]:
                self.assertEqual(row["activation_count"], 1)
                self.assertEqual(row["pairwise"], {"with": 1})
                self.assertEqual(row["checks"]["delta"], 1)
                self.assertEqual(row["grades"]["delta"], 1)
            scratch = root / "scratch"
            # The containers are traverse-only; restore read access to check
            # that every per-call home and cwd is gone.
            for name in ("homes", "cwd"):
                self.assertEqual((scratch / name).stat().st_mode & 0o777, 0o300)
                os.chmod(scratch / name, 0o700)
            self.assertEqual(list((scratch / "homes").iterdir()), [])
            self.assertEqual(list((scratch / "cwd").iterdir()), [])


    def test_install_as_runs_the_skill_under_an_alias(self):
        """--install-as: the arms see only the alias, the explicit prompt
        names it, and activation of the alias counts as the skill loading."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bindir = root / "bin"
            bindir.mkdir()
            auditing = Path(__file__).resolve().parent.parent / "auditing"
            for name in ("claude", "codex"):
                shutil.copy2(auditing / "skill_eval/fixtures/performance/agent_stub.py", bindir / name)
                (bindir / name).chmod(0o755)
            suite = root / "suite.json"
            suite.write_text(json.dumps({"version": 1, "tasks": [task()]}))
            (root / "home").mkdir()
            env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ["PATH"], HOME=str(root / "home"),
                       SKILL_EVAL_SCRATCH=str(root / "scratch"), SKILL_EVAL_RUNS_DIR=str(root / "runs"))
            proc = subprocess.run([sys.executable, str(auditing / "skill-eval.py"), "performance", "run",
                                   "--skill", "writing-style", "--install-as", "ws-under-test", "--suite", str(suite),
                                   "--repeats", "1", "--max-calls", "14"], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            result_dir = Path(proc.stdout.strip())
            for row in json.loads((result_dir / "summary.json").read_text())["rows"]:
                self.assertEqual(row["activation_count"], 1)
            snapshot = (result_dir / "inputs" / "skill" / "SKILL.md").read_text()
            self.assertIn("name: ws-under-test", snapshot)
            for line in (result_dir / "pairs.jsonl").read_text().splitlines():
                self.assertEqual(json.loads(line)["arms"]["with"]["trace"]["activated"], ["ws-under-test"])

    def test_install_as_refuses_a_library_name(self):
        auditing = Path(__file__).resolve().parent.parent / "auditing"
        proc = subprocess.run([sys.executable, str(auditing / "skill-eval.py"), "performance", "run",
                               "--skill", "writing-style", "--install-as", "code-review",
                               "--suite", str(auditing / "skill_eval/examples/text-task.json"), "--dry-run"],
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--install-as", proc.stderr)


    def test_rejudge_repairs_only_failed_judging_and_keeps_a_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bindir = root / "bin"
            bindir.mkdir()
            auditing = Path(__file__).resolve().parent.parent / "auditing"
            for name in ("claude", "codex"):
                shutil.copy2(auditing / "skill_eval/fixtures/performance/agent_stub.py", bindir / name)
                (bindir / name).chmod(0o755)
            suite = root / "suite.json"
            suite.write_text(json.dumps({"version": 1, "tasks": [task()]}))
            (root / "home").mkdir()
            env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ["PATH"], HOME=str(root / "home"),
                       SKILL_EVAL_SCRATCH=str(root / "scratch"), SKILL_EVAL_RUNS_DIR=str(root / "runs"))
            entry = [sys.executable, str(auditing / "skill-eval.py"), "performance"]
            proc = subprocess.run(entry + ["run", "--skill", "writing-style", "--suite", str(suite), "--repeats", "1",
                                           "--max-calls", "14"], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            run_dir = Path(proc.stdout.strip())
            pairs = [json.loads(l) for l in (run_dir / "pairs.jsonl").read_text().splitlines()]
            # Simulate a judge outage on the first pair only.
            broken = pairs[0]
            broken["comparison"]["repeats"] = [{"void": True}, {"void": True}]
            broken["comparison"]["verdict"] = "void"
            for arm in broken["arms"].values():
                for g in arm["grades"]:
                    g["verdict"] = "unsupported"
            (run_dir / "pairs.jsonl").write_text("".join(json.dumps(p) + "\n" for p in pairs))
            proc = subprocess.run(entry + ["rejudge", str(run_dir)], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            after = [json.loads(l) for l in (run_dir / "pairs.jsonl").read_text().splitlines()]
            self.assertIn("rejudged_at", after[0])
            self.assertNotIn("rejudged_at", after[1])
            self.assertEqual(after[0]["comparison"]["verdict"], "b")
            self.assertEqual(len(list(run_dir.glob("pairs.before-rejudge-*.jsonl"))), 1)
            budget = json.loads((run_dir / "budget.json").read_text())
            self.assertGreater(budget["calls"], 14)


class CollectorHookTests(unittest.TestCase):
    def test_task_role_enables_editing_without_messaging_or_network_tools(self):
        argv, env = vendors._build_argv("claude", Path("/tmp/home"), Path("/tmp/cwd"), "haiku", "medium", "task", None)
        tools = argv[argv.index("--tools") + 1].split(",")
        self.assertTrue({"Edit", "Write", "NotebookEdit"}.issubset(tools))
        self.assertFalse({"SendMessage", "ListAgents", "WebFetch", "WebSearch"}.intersection(tools))
        record = common.TraceRecord(vendor="claude", visible_tools=tools)
        self.assertEqual(activation._check_contamination(record, "claude", set(), [], tool_role="task")[0], [])
        self.assertTrue(activation._check_contamination(record, "claude", set(), [])[0])

    def test_shared_executor_collects_before_workspace_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home_root = root / "scratch"
            cwd = home_root / "cwd"
            cwd.mkdir(parents=True)
            (cwd / "artifact").write_text("evidence")
            rec = common.TraceRecord(vendor="codex", text="done")
            with mock.patch.object(activation, "SCRATCH_ROOT", home_root), \
                 mock.patch.object(vendors, "neutral_cwd", return_value=cwd), \
                 mock.patch.object(vendors, "build_home"), \
                 mock.patch.object(vendors, "prepare_workspace", return_value="fixture"), \
                 mock.patch.object(vendors, "verify_environment", return_value=[]), \
                 mock.patch.object(vendors, "exec_agent", return_value={"trace_path": str(root / "trace"), "exit_code": 0}), \
                 mock.patch("skill_eval.trace.parse_trace", return_value=rec), \
                 mock.patch.object(vendors, "cleanup_home"):
                _, info, _ = activation._execute_one(
                    vendor="codex", model="fixture", skills_map={}, description_overrides=None,
                    run_label="test", label="arm", prompt="task", run_dir=root / "runs", known_skills=set(),
                    timeout=10, effort="medium", keep_home=False,
                    collect=lambda path, text: (path / "artifact").read_text())
            self.assertEqual(info["evidence"], "evidence")
            self.assertFalse(cwd.exists())


if __name__ == "__main__":
    unittest.main()
