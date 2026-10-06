from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_AUDITING_DIR = Path(__file__).resolve().parent.parent / "auditing"
if str(_AUDITING_DIR) not in sys.path:
    sys.path.insert(0, str(_AUDITING_DIR))

from skill_eval import activation, vendors  # noqa: E402
from skill_eval import common  # noqa: E402
from skill_eval import trace as trace_module  # noqa: E402
from skill_eval.common import Case, Finding, TraceRecord, split_cases, split_of  # noqa: E402

_TRACE_FIXTURES = _AUDITING_DIR / "skill_eval" / "fixtures" / "trace"
_ACTIVATION_FIXTURES = _AUDITING_DIR / "skill_eval" / "fixtures" / "activation"

# trace.parse_trace is landing `roots=` concurrently in another module (see
# the task brief: "code against these names; in tests, stub them"). This
# shim lets activation.py be written against the final contract -- it
# always passes exit_code= and roots= -- while these tests still run against
# whatever trace.py currently supports. Once trace.py lands `roots`, this
# shim's try branch is what actually executes; nothing here needs to change.
_REAL_PARSE_TRACE = trace_module.parse_trace


def _compat_parse_trace(path, vendor, known_skills, *, exit_code=None, roots=None):
    try:
        return _REAL_PARSE_TRACE(path, vendor, known_skills, exit_code=exit_code, roots=roots)
    except TypeError:
        return _REAL_PARSE_TRACE(path, vendor, known_skills, exit_code=exit_code)


def _cases(skill="pr-description", n_pos=3, n_neg=3, extra_tags=None):
    cases = []
    for i in range(n_pos):
        cases.append(Case(skill=skill, prompt=f"positive prompt number {i}", expect=True,
                           tags=list((extra_tags or {}).get(f"pos{i}", []))))
    for i in range(n_neg):
        cases.append(Case(skill=skill, prompt=f"negative prompt number {i}", expect=False,
                           tags=list((extra_tags or {}).get(f"neg{i}", []))))
    return cases


class PlanRunTests(unittest.TestCase):
    """plan_run is pure: no filesystem, no network, no subprocess."""

    def test_call_count_is_cases_times_vendors_times_repeats(self):
        cases = _cases(n_pos=2, n_neg=2)
        splits = split_cases(cases)
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku", "codex": "gpt-5.6-luna"}, repeats=3,
            split="train", cases_by_split=splits,
        )
        n_train_cases = len(splits["train"])
        self.assertEqual(plan["call_count_total"], n_train_cases * 2 * 3)
        self.assertEqual(plan["call_count_per_vendor"]["claude"], n_train_cases * 3)
        self.assertEqual(plan["call_count_per_vendor"]["codex"], n_train_cases * 3)
        self.assertEqual(len(plan["calls"]), plan["call_count_total"])

    def test_visible_split_pools_train_and_dev_by_membership_not_count(self):
        """`split_cases()`'s "holdout" key is the visible dev set (renamed to
        "dev" by the caller, per DESIGN.md sec 2 T-C item 1); "visible" pools
        train and dev, and every case's split must match what
        `common.split_of()` says for it -- never a hard-coded count, which
        the salted per-case hash makes hash-luck-dependent (this is the test
        that broke under the new hash split; see item 7)."""
        cases = _cases(n_pos=6, n_neg=6)
        visible = split_cases(cases)  # {"train": [...], "holdout": [...]}; "holdout" == dev here
        cases_by_split = {"train": visible["train"], "dev": visible["holdout"]}
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="visible",
            cases_by_split=cases_by_split,
        )
        seen_splits = {c["split"] for c in plan["cases"]}
        self.assertLessEqual(seen_splits, {"train", "dev"})
        self.assertEqual(len(plan["cases"]), len(cases))
        by_id = {row["id"]: row for row in plan["cases"]}
        for c in cases:
            expected_split = "train" if split_of(c) == "train" else "dev"
            self.assertEqual(by_id[c.id]["split"], expected_split)

    def test_holdout_split_uses_only_the_holdout_group_never_visible(self):
        """The real holdout is only the sealed set: even when train/dev
        cases are present in `cases_by_split`, `--split holdout` must pull
        exclusively from the "holdout" key (DESIGN.md sec 2 T-C: "the
        holdout is never mixed with visible cases in one run")."""
        cases = _cases(n_pos=3, n_neg=3)
        visible = split_cases(cases)
        sealed_case = Case(skill="pr-description", prompt="a sealed holdout prompt",
                            expect=True, source="sealed")
        cases_by_split = {"train": visible["train"], "dev": visible["holdout"],
                           "holdout": [sealed_case]}
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="holdout",
            cases_by_split=cases_by_split,
        )
        self.assertEqual({c["split"] for c in plan["cases"]}, {"holdout"})
        self.assertEqual({c["id"] for c in plan["cases"]}, {sealed_case.id})

    def test_limit_takes_first_n_per_polarity(self):
        cases = _cases(n_pos=5, n_neg=5)
        splits = split_cases(cases)
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="train", cases_by_split=splits,
            limit=1,
        )
        positives = [c for c in plan["cases"] if c["polarity"] == "positive"]
        negatives = [c for c in plan["cases"] if c["polarity"] == "negative"]
        self.assertLessEqual(len(positives), 1)
        self.assertLessEqual(len(negatives), 1)

    def test_case_id_filter_selects_only_named_cases(self):
        cases = _cases(n_pos=3, n_neg=3)
        splits = split_cases(cases)
        one_id = splits["train"][0].id
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=2, split="train", cases_by_split=splits,
            case_ids=[one_id],
        )
        self.assertEqual({c["id"] for c in plan["cases"]}, {one_id})
        self.assertEqual(plan["call_count_total"], 2)

    def test_unknown_shape_or_split_raises(self):
        splits = split_cases(_cases())
        with self.assertRaises(ValueError):
            activation.plan_run(skill="x", shape="bogus", installed_skills=["x"],
                                vendors_models={"claude": "haiku"}, repeats=1, split="train",
                                cases_by_split=splits)
        with self.assertRaises(ValueError):
            activation.plan_run(skill="x", shape="isolated", installed_skills=["x"],
                                vendors_models={"claude": "haiku"}, repeats=1, split="bogus",
                                cases_by_split=splits)


class ParaphraseSplitInheritanceTests(unittest.TestCase):
    """DESIGN.md sec 2 T-C item 4: a paraphrase's split follows its parent's
    through `common.split_of`'s `paraphrase-of:<id>` tag, never its own
    wording. `activation._load_all_cases` + `common.split_cases` is exactly
    the pipeline `activation run --include-paraphrases` drives, so this
    exercises the same mechanism the runner depends on."""

    def test_paraphrase_of_a_dev_case_lands_in_dev(self):
        parent = None
        for i in range(300):
            candidate = Case(skill="pr-description", prompt=f"probe wording variant {i}", expect=True)
            # common.split_cases's "holdout" key is the visible dev set.
            if split_of(candidate) == "holdout":
                parent = candidate
                break
        self.assertIsNotNone(parent, "expected at least one dev-split probe within 300 tries")

        paraphrase = Case(skill="pr-description", prompt="a completely differently worded probe",
                           expect=True, tags=[f"paraphrase-of:{parent.id}"])
        splits = split_cases([parent, paraphrase])
        self.assertIn(parent, splits["holdout"])
        self.assertIn(paraphrase, splits["holdout"])
        self.assertNotIn(paraphrase, splits["train"])


class DryRunCliTests(unittest.TestCase):
    """`activation run --dry-run` prints the plan and never touches vendors."""

    def setUp(self):
        # These tests stub load_cases; the corpus gate lints the real file,
        # so it is stubbed clean here and exercised in CorpusGateTests.
        p = mock.patch("skill_eval.cases.lint", return_value=[])
        p.start()
        self.addCleanup(p.stop)

    def test_dry_run_never_calls_exec_agent(self):
        cases = _cases(n_pos=2, n_neg=2)

        with mock.patch("skill_eval.cases.load_cases", return_value=cases), \
             mock.patch.object(vendors, "exec_agent") as fake_exec, \
             mock.patch.object(vendors, "build_home") as fake_build:
            parser = _build_parser()
            args = parser.parse_args([
                "activation", "run", "--skill", "pr-description", "--shape", "isolated",
                "--vendors", "claude,codex", "--models", "claude=haiku,codex=gpt-5.6-luna",
                "--repeats", "1", "--limit", "2", "--split", "train", "--dry-run",
            ])
            rc = args.func(args)
        self.assertEqual(rc, 0)
        fake_exec.assert_not_called()
        fake_build.assert_not_called()

    def test_dry_run_counts_uncached_baseline_probe_calls(self):
        """Round 2 finding 6: the builtin-baseline probe call was not
        counted in the plan, so --dry-run undercounted the real spend.
        Guards: reverting `_count_uncached_baseline_probes` (or not calling
        it from `_cmd_run`) drops `baseline_probe_calls` back to 0/absent
        even though nothing is cached, which this test catches directly."""
        cases = _cases(n_pos=1, n_neg=1)
        with mock.patch("skill_eval.cases.load_cases", return_value=cases), \
             mock.patch.object(vendors, "exec_agent") as fake_exec, \
             mock.patch.object(vendors, "baseline_cache_path",
                                return_value=Path("/nonexistent-skill-eval-baseline-cache.json"),
                                create=True), \
             mock.patch.object(activation, "RUNS_DIR", Path("/nonexistent-skill-eval-runs-dir")):
            parser = _build_parser()
            args = parser.parse_args([
                "activation", "run", "--skill", "pr-description", "--shape", "isolated",
                "--vendors", "claude,codex", "--models", "claude=haiku,codex=gpt-5.6-luna",
                "--repeats", "1", "--limit", "1", "--split", "train", "--dry-run",
            ])
            rc = args.func(args)
        self.assertEqual(rc, 0)
        fake_exec.assert_not_called()

    def test_dry_run_baseline_probe_count_uses_real_cache_filename_lookup(self):
        """Round 3 finding (minor): `_count_uncached_baseline_probes` used
        to guess the cache filename instead of calling
        `vendors.baseline_cache_path` (which keys on vendor + model + CLI
        version), so it always reported every vendor as uncached, even
        against a warm cache. With `baseline_cache_path` stubbed to report
        one vendor cached and one not, exactly one must be counted."""
        cases = _cases(n_pos=1, n_neg=1)

        def fake_cache_path(vendor, model=None):
            return Path(f"/nonexistent-skill-eval-baseline-{vendor}.json")

        with mock.patch("skill_eval.cases.load_cases", return_value=cases), \
             mock.patch.object(vendors, "exec_agent"), \
             mock.patch.object(vendors, "baseline_cache_path", side_effect=fake_cache_path, create=True), \
             mock.patch("builtins.print") as fake_print:
            parser = _build_parser()
            args = parser.parse_args([
                "activation", "run", "--skill", "pr-description", "--shape", "isolated",
                "--vendors", "claude", "--models", "claude=haiku",
                "--repeats", "1", "--limit", "1", "--split", "train", "--dry-run",
            ])
            rc = args.func(args)
        self.assertEqual(rc, 0)
        printed = json.loads(fake_print.call_args[0][0])
        self.assertEqual(printed["baseline_probe_calls"], 1)


def _build_parser():
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    activation.add_subparser(sub)
    return parser


class RunActivationExecutionTests(unittest.TestCase):
    """Exercises run_activation() directly: a hand-built plan, a stubbed
    exec_agent that writes canned trace fixtures, and a stubbed
    builtin_baseline. No subprocess, no live network call. build_home /
    verify_environment / cleanup_home run for real (pure filesystem) against
    a patched SCRATCH_ROOT, since round 2 finding 1 moved home construction
    inside run_activation's own per-call executor."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        self.run_dir = self.tmp_path / "run"
        self.run_dir.mkdir()
        scratch = self.tmp_path / "scratch"
        self._scratch_patches = [
            mock.patch.object(vendors, "SCRATCH_ROOT", scratch),
            mock.patch.object(activation, "SCRATCH_ROOT", scratch),
        ]
        for p in self._scratch_patches:
            p.start()
            self.addCleanup(p.stop)
        self._builtin_patch = mock.patch.object(vendors, "builtin_baseline", return_value=[])
        self._builtin_patch.start()
        self.addCleanup(self._builtin_patch.stop)
        # A cached (existing) baseline path, so run_activation's baseline-
        # probe reservation (round 3 finding, minor) never fires here and
        # `vendors.baseline_cache_path` (which shells out to `<vendor>
        # --version` in the real implementation) is never called for real.
        cached_marker = self.tmp_path / "cached-baseline.json"
        cached_marker.write_text("{}", encoding="utf-8")
        self._baseline_cache_patch = mock.patch.object(
            vendors, "baseline_cache_path", return_value=cached_marker, create=True)
        self._baseline_cache_patch.start()
        self.addCleanup(self._baseline_cache_patch.stop)
        # Round 3 finding O1: every call now runs vendors.prepare_workspace
        # before verify_environment. kind="git" shells out to git in the
        # real implementation; DESIGN.md sec 5 forbids a subprocess in unit
        # tests, so it is stubbed here like every other vendor call.
        self._workspace_patch = mock.patch.object(vendors, "prepare_workspace",
                                                    return_value="fixturesha", create=True)
        self._workspace_patch.start()
        self.addCleanup(self._workspace_patch.stop)
        self._trace_patch = mock.patch.object(trace_module, "parse_trace", side_effect=_compat_parse_trace)
        self._trace_patch.start()
        self.addCleanup(self._trace_patch.stop)
        self.skills_map = {"pr-description": Path("/workspace/skills/pr-description"),
                            "code-review": Path("/workspace/skills/code-review")}

    def _plan(self, cases, split="train", repeats=1, vendors_models=None, shape="isolated"):
        splits = split_cases(cases)
        return activation.plan_run(
            skill="pr-description", shape=shape, installed_skills=["pr-description"],
            vendors_models=vendors_models or {"claude": "haiku"}, repeats=repeats,
            split=split, cases_by_split=splits,
        ), splits

    def _run(self, plan, all_by_id, concurrency=1):
        return activation.run_activation(
            plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
            run_label="testrun", all_cases_by_id=all_by_id, concurrency=concurrency,
        )

    def test_activation_from_real_fixture_is_scored_a_hit(self):
        cases = [Case(skill="pr-description", prompt="trigger it", expect=True)]
        plan, _ = self._plan(cases)
        all_by_id = {c.id: c for c in cases}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = self._run(plan, all_by_id)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["ok"])
        self.assertTrue(rows[0]["hit"])
        self.assertIn("pr-description", rows[0]["activated"])

    def test_failed_calls_are_excluded_from_denominators(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True),
                 Case(skill="pr-description", prompt="p2", expect=True)]
        plan, splits = self._plan(cases, repeats=2)
        all_by_id = {c.id: c for c in cases}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            if prompt == "p1":
                Path(trace_out).write_bytes(
                    (_TRACE_FIXTURES / "claude-auth-error.synthetic.jsonl").read_bytes())
            else:
                Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = self._run(plan, all_by_id)
        failed = [r for r in rows if not r["ok"]]
        self.assertTrue(failed, "expected at least one failed call from the auth-error fixture")
        summary = activation.build_summary(plan, rows)
        p1_id = cases[0].id
        found_zero = False
        for split_summary in summary["vendors"]["claude"]["splits"].values():
            if p1_id in split_summary["cases"]:
                found_zero = True
                self.assertEqual(split_summary["cases"][p1_id]["n"], 0)
        self.assertTrue(found_zero)
        self.assertEqual(summary["vendors"]["claude"]["calls_failed"], 2)

    def test_contamination_extra_skill_is_excluded_and_flagged(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan, _ = self._plan(cases)
        all_by_id = {c.id: c for c in cases}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes(
                (_ACTIVATION_FIXTURES / "claude-contaminated-extra-skill.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = self._run(plan, all_by_id)
        self.assertTrue(rows[0]["contaminated"])
        summary = activation.build_summary(plan, rows)
        self.assertEqual(summary["vendors"]["claude"]["contaminated_count"], 1)
        for split_summary in summary["vendors"]["claude"]["splits"].values():
            for block in split_summary["cases"].values():
                self.assertEqual(block["n"], 0)

    def test_contamination_missing_expected_skill_is_flagged(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan, _ = self._plan(cases)
        all_by_id = {c.id: c for c in cases}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes(
                (_ACTIVATION_FIXTURES / "claude-contaminated-missing-skill.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = self._run(plan, all_by_id)
        self.assertTrue(rows[0]["contaminated"])

    def test_train_and_dev_are_reported_separately(self):
        """"visible" pools train and dev cases into one run, but they must
        still be reported as distinct splits, never pooled into one rate
        (DESIGN.md sec 2 T-C item 1)."""
        cases = _cases(n_pos=6, n_neg=6)
        visible = split_cases(cases)
        self.assertTrue(visible["holdout"], "fixture corpus must actually produce a dev slice")
        cases_by_split = {"train": visible["train"], "dev": visible["holdout"]}
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="visible",
            cases_by_split=cases_by_split,
        )
        all_by_id = {c.id: c for c in cases}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-no-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = self._run(plan, all_by_id, concurrency=2)
        summary = activation.build_summary(plan, rows)
        train_ids = set(summary["vendors"]["claude"]["splits"]["train"]["cases"])
        dev_ids = set(summary["vendors"]["claude"]["splits"]["dev"]["cases"])
        self.assertTrue(train_ids)
        self.assertTrue(dev_ids)
        self.assertEqual(train_ids & dev_ids, set())
        expected_train_ids = {c.id for c in visible["train"]}
        expected_dev_ids = {c.id for c in visible["holdout"]}
        self.assertEqual(train_ids, expected_train_ids)
        self.assertEqual(dev_ids, expected_dev_ids)

    def test_stolen_by_table_only_counts_non_target_activations_on_positives(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan, _ = self._plan(cases, vendors_models={"claude": "haiku"}, shape="competitive")
        plan["installed_skills"] = ["pr-description", "code-review"]
        all_by_id = {c.id: c for c in cases}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            events = [
                json.dumps({"type": "system", "subtype": "init", "skills": ["pr-description", "code-review"]}),
                json.dumps({"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": "Skill", "input": {"skill": "code-review"}},
                ]}}),
                json.dumps({"type": "result", "is_error": False, "result": "done", "total_cost_usd": 0.001}),
            ]
            Path(trace_out).write_text("\n".join(events), encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = self._run(plan, all_by_id)
        self.assertEqual(rows[0]["stolen"], ["code-review"])
        summary = activation.build_summary(plan, rows)
        stolen = summary["vendors"]["claude"]["splits"]["train"]["stolen_by"]
        self.assertEqual(stolen, {"code-review": 1})
        # Round 2 finding 6: every competitive record reports what fired first.
        self.assertEqual(rows[0]["first_activated"], "code-review")
        case_id = cases[0].id
        block = summary["vendors"]["claude"]["splits"]["train"]["cases"][case_id]
        self.assertEqual(block["first_activated_by"], {"code-review": 1})

    def test_failure_rate_warning_flag(self):
        cases = [Case(skill="pr-description", prompt=f"p{i}", expect=True) for i in range(5)]
        plan, _ = self._plan(cases, repeats=1)
        all_by_id = {c.id: c for c in cases}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            # 3 of 5 (60%) fail: well above the 20% warn threshold.
            fixture = "claude-auth-error.synthetic.jsonl" if prompt in ("p0", "p1", "p2") \
                else "claude-activate.jsonl"
            Path(trace_out).write_bytes((_TRACE_FIXTURES / fixture).read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = self._run(plan, all_by_id)
        summary = activation.build_summary(plan, rows)
        self.assertTrue(summary["vendors"]["claude"]["failure_rate_warn"])
        self.assertGreater(summary["vendors"]["claude"]["failure_rate"], activation.FAILURE_RATE_WARN)

    def test_each_call_builds_and_cleans_up_its_own_home(self):
        """Round 2 finding 1 (critical): a home reused across calls carries
        sync downloads and session state from one call to the next. Guards
        against reverting to one shared home per vendor by asserting
        build_home/cleanup_home are called once per call, each with a
        distinct home path (never the same path reused across calls)."""
        cases = [Case(skill="pr-description", prompt=f"p{i}", expect=True) for i in range(6)]
        plan, _ = self._plan(cases, repeats=1)
        expected_call_count = plan["call_count_total"]
        self.assertGreater(expected_call_count, 1, "test needs more than one call to be meaningful")
        all_by_id = {c.id: c for c in cases}

        built_homes = []
        cleaned_homes = []
        real_build_home = vendors.build_home
        real_cleanup_home = vendors.cleanup_home

        def spy_build_home(vendor, home, skills, **kwargs):
            built_homes.append(Path(home))
            return real_build_home(vendor, home, skills, **kwargs)

        def spy_cleanup_home(home):
            cleaned_homes.append(Path(home))
            return real_cleanup_home(home)

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec), \
             mock.patch.object(vendors, "build_home", side_effect=spy_build_home), \
             mock.patch.object(vendors, "cleanup_home", side_effect=spy_cleanup_home):
            self._run(plan, all_by_id, concurrency=1)

        self.assertEqual(len(built_homes), expected_call_count, "expected exactly one build_home per call")
        self.assertEqual(len(set(built_homes)), expected_call_count,
                          "every call must get a distinct home path")
        self.assertEqual(sorted(cleaned_homes), sorted(built_homes),
                          "every built home must be cleaned up")

    def test_keep_homes_skips_cleanup(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan, _ = self._plan(cases)
        all_by_id = {c.id: c for c in cases}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec), \
             mock.patch.object(vendors, "cleanup_home") as fake_cleanup:
            activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1, keep_homes=True,
            )
        fake_cleanup.assert_not_called()


class ContaminationChecksTests(unittest.TestCase):
    """Round 2 finding 2: tools-mismatch and outside-read contamination,
    tested directly against `_check_contamination` (pure given a
    hand-built TraceRecord) so they do not depend on trace.py's `roots`
    support landing first."""

    def setUp(self):
        self._claude_tools_patch = mock.patch.object(
            vendors, "CLAUDE_ARM_TOOLS", "Read,Glob,Grep,Bash,Skill", create=True,
        )
        self._claude_tools_patch.start()
        self.addCleanup(self._claude_tools_patch.stop)

    def test_claude_tools_matching_whitelist_is_clean(self):
        record = TraceRecord(vendor="claude", visible_skills=["pr-description"],
                              visible_tools=["Read", "Glob", "Grep", "Bash", "Skill"])
        reasons, foreign, other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertEqual(reasons, [])
        self.assertEqual(foreign, [])
        self.assertEqual(other, [])

    def test_claude_extra_tool_is_tools_mismatch(self):
        record = TraceRecord(vendor="claude", visible_skills=["pr-description"],
                              visible_tools=["Read", "Glob", "Grep", "Bash", "Skill", "SendMessage"])
        reasons, _foreign, _other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertTrue(any("tools-mismatch" in r for r in reasons))

    def test_claude_missing_tool_is_tools_mismatch(self):
        record = TraceRecord(vendor="claude", visible_skills=["pr-description"],
                              visible_tools=["Read", "Glob"])
        reasons, _foreign, _other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertTrue(any("tools-mismatch" in r for r in reasons))

    def test_codex_visible_tools_none_is_never_flagged(self):
        """codex reports no visible_tools (None); the check must not fire
        for a vendor that never reports the field."""
        record = TraceRecord(vendor="codex", visible_skills=None, visible_tools=None)
        reasons, _foreign, _other = activation._check_contamination(
            record, "codex", {"pr-description"}, [])
        self.assertEqual(reasons, [])

    def test_outside_read_under_repo_root_is_contaminated(self):
        from skill_eval import common
        record = TraceRecord(vendor="claude",
                              outside_reads=[str(common.REPO_ROOT / "CLAUDE.md")])
        reasons, _foreign, other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertTrue(any("outside-read" in r for r in reasons))
        self.assertEqual(other, [])

    def test_outside_read_under_real_home_is_contaminated(self):
        record = TraceRecord(vendor="claude",
                              outside_reads=[str(Path.home() / ".claude" / "settings.json")])
        reasons, _foreign, other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertTrue(any("outside-read" in r for r in reasons))

    def test_other_outside_read_is_a_warning_not_contamination(self):
        """A read outside the arm's home/cwd that is NOT under the repo or
        the real user home (e.g. /etc/hostname) is reported separately as a
        warning, never silently dropped and never contaminating the record
        by itself."""
        record = TraceRecord(vendor="claude", outside_reads=["/etc/hostname"])
        reasons, _foreign, other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertEqual([r for r in reasons if "outside-read" in r], [])
        self.assertEqual(other, ["/etc/hostname"])

    def test_namespaced_skill_is_foreign_even_if_baseline_lists_it(self):
        record = TraceRecord(vendor="claude",
                              visible_skills=["pr-description", "anthropic-skills:writing-style"])
        reasons, foreign, _other = activation._check_contamination(
            record, "claude", {"pr-description"}, ["anthropic-skills:writing-style"])
        self.assertIn("anthropic-skills:writing-style", foreign)
        self.assertTrue(any("unexpected visible skills" in r for r in reasons))

    def test_outside_reads_warn_count_reaches_the_summary(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="train",
            cases_by_split={"train": cases, "dev": []},
        )
        row = {"call_index": 0, "case_id": cases[0].id, "skill": "pr-description", "split": "train",
               "vendor": "claude", "model": "haiku", "repeat": 0, "expect": True, "polarity": "positive",
               "tags": [], "skipped_by_cap": False, "ok": True, "error": "", "activated": [],
               "first_activated": None, "activation_signals": {}, "hit": False, "stolen": [],
               "contaminated": False, "contamination_reasons": [], "foreign_skills": [],
               "other_outside_reads_count": 2, "visible_skills": None, "cost_usd": None,
               "tokens": None, "trace_path": ""}
        summary = activation.build_summary(plan, [row])
        self.assertEqual(summary["vendors"]["claude"]["outside_reads_warn_count"], 2)


class HoldoutAggregateOnlyTests(unittest.TestCase):
    """Round 2 finding 3b/3c: holdout results are aggregate only everywhere,
    and holdout traces carry no prompt text."""

    def _holdout_row(self, case_id, hit, polarity="positive"):
        return {"case_id": case_id, "skill": "s", "split": "holdout", "vendor": "claude",
                "model": "haiku", "repeat": 0, "expect": polarity == "positive", "polarity": polarity,
                "tags": [], "skipped_by_cap": False, "ok": True, "error": "", "hit": hit,
                "contaminated": False, "activated": [], "first_activated": None,
                "cost_usd": None, "tokens": None}

    def test_build_summary_never_exposes_holdout_case_ids(self):
        plan = {"shape": "isolated", "vendors": {"claude": "haiku"}, "skill": "s",
                "split": "holdout", "repeats": 1, "description_sha": None}
        records = [self._holdout_row("holdout-case-1", True), self._holdout_row("holdout-case-2", False)]
        summary = activation.build_summary(plan, records)
        self.assertEqual(summary["vendors"]["claude"]["splits"]["holdout"]["cases"], {})
        dumped = json.dumps(summary)
        self.assertNotIn("holdout-case-1", dumped)
        self.assertNotIn("holdout-case-2", dumped)
        # but the aggregate rate is still there (both rows are positives here)
        self.assertEqual(summary["vendors"]["claude"]["splits"]["holdout"]["sensitivity"]["n"], 2)

    def test_render_summary_md_never_lists_holdout_case_ids(self):
        plan = {"shape": "isolated", "vendors": {"claude": "haiku"}, "skill": "s",
                "split": "holdout", "repeats": 1, "description_sha": None}
        records = [self._holdout_row("holdout-case-xyz", True)]
        summary = activation.build_summary(plan, records)
        md = activation.render_summary_md(summary)
        self.assertNotIn("holdout-case-xyz", md)

    def test_compare_runs_never_produces_a_holdout_case_delta(self):
        row_a = self._holdout_row("h1", True)
        row_b = self._holdout_row("h1", False)
        plan_a = {"vendors": {"claude": "haiku"}}
        plan_b = {"vendors": {"claude": "haiku"}}
        result = activation.compare_runs(plan_a, [row_a], plan_b, [row_b])
        self.assertEqual(result["deltas"], [])
        self.assertTrue(result["holdout_aggregate"])
        dumped = json.dumps(result)
        self.assertNotIn("h1", dumped)

    def test_scrub_holdout_trace_replaces_prompt_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = Path(tmp) / "trace.jsonl"
            trace_path.write_text('{"type": "result", "result": "the secret holdout prompt appears here"}',
                                   encoding="utf-8")
            activation._scrub_holdout_trace(trace_path, "the secret holdout prompt")
            text = trace_path.read_text(encoding="utf-8")
        self.assertNotIn("the secret holdout prompt", text)
        self.assertIn(activation._HOLDOUT_REDACTION_MARKER, text)

    def test_scrub_holdout_trace_is_a_noop_when_prompt_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = Path(tmp) / "trace.jsonl"
            original = '{"type": "result", "result": "nothing sensitive"}'
            trace_path.write_text(original, encoding="utf-8")
            activation._scrub_holdout_trace(trace_path, "a prompt never present here")
            text = trace_path.read_text(encoding="utf-8")
        self.assertEqual(text, original)

    def test_holdout_trace_directory_is_0700(self):
        """Guards finding 3c's "holdout traces go into a 0700 subdirectory":
        run_activation must chmod the holdout trace dir, not the default
        traces/ dir shared with train/dev."""
        import os
        import stat

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        run_dir.mkdir()
        scratch = tmp_path / "scratch"

        cases = [Case(skill="pr-description", prompt="a holdout prompt", expect=True, source="sealed")]
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="holdout",
            cases_by_split={"train": [], "dev": [], "holdout": cases},
        )
        all_by_id = {c.id: c for c in cases}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        cached_marker = tmp_path / "cached-baseline.json"
        cached_marker.write_text("{}", encoding="utf-8")
        with mock.patch.object(vendors, "SCRATCH_ROOT", scratch), \
             mock.patch.object(activation, "SCRATCH_ROOT", scratch), \
             mock.patch.object(vendors, "builtin_baseline", return_value=[]), \
             mock.patch.object(vendors, "baseline_cache_path", return_value=cached_marker, create=True), \
             mock.patch.object(vendors, "prepare_workspace", return_value="fixturesha", create=True), \
             mock.patch.object(trace_module, "parse_trace", side_effect=_compat_parse_trace), \
             mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            activation.run_activation(
                plan, run_dir=run_dir, skills_map={"pr-description": Path("/workspace/skills/pr-description")},
                description_overrides={}, run_label="testrun", all_cases_by_id=all_by_id, concurrency=1,
            )

        holdout_dir = run_dir / "traces" / "holdout"
        self.assertTrue(holdout_dir.exists())
        mode = stat.S_IMODE(os.stat(holdout_dir).st_mode)
        self.assertEqual(mode, 0o700)


class HoldoutLedgerFlagRemovedTests(unittest.TestCase):
    """Round 2 finding 3a: `--holdout-ledger` must not exist as a CLI flag
    (it let anyone point at an empty ledger and bypass the look budget); the
    only override is the SKILL_EVAL_HOLDOUT_LEDGER environment variable."""

    def test_holdout_ledger_flag_is_gone_from_run_parser(self):
        parser = _build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["activation", "run", "--skill", "x", "--holdout-ledger", "/tmp/x"])

    def test_resolve_holdout_ledger_uses_env_var_override(self):
        import os
        from skill_eval import common
        with mock.patch.dict(os.environ, {"SKILL_EVAL_HOLDOUT_LEDGER": "/tmp/fake-ledger.jsonl"}):
            self.assertEqual(activation._resolve_holdout_ledger(), Path("/tmp/fake-ledger.jsonl"))
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SKILL_EVAL_HOLDOUT_LEDGER", None)
            self.assertEqual(activation._resolve_holdout_ledger(), common.HOLDOUT_LEDGER)


class HoldoutLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ledger = Path(self.tmp.name) / "holdout-ledger.jsonl"

    def test_new_sha_below_budget_proceeds_quietly(self):
        d = activation.check_holdout_budget("pr-description", "sha-a", ledger=self.ledger, allow_reuse=False)
        self.assertTrue(d.proceed)
        self.assertFalse(d.warning)
        self.assertFalse(d.refusal)

    def test_sha_already_on_ledger_is_free(self):
        from skill_eval import common
        common.record_holdout_look("pr-description", "sha-a", "run-1", ledger=self.ledger)
        d = activation.check_holdout_budget("pr-description", "sha-a", ledger=self.ledger, allow_reuse=False)
        self.assertTrue(d.proceed)
        self.assertFalse(d.is_new_look)
        self.assertFalse(d.warning)

    def test_warns_at_budget(self):
        from skill_eval import common
        common.record_holdout_look("pr-description", "sha-a", "run-1", ledger=self.ledger)
        common.record_holdout_look("pr-description", "sha-b", "run-2", ledger=self.ledger)
        # third distinct sha == HOLDOUT_LOOK_BUDGET (3): warn but proceed.
        d = activation.check_holdout_budget("pr-description", "sha-c", ledger=self.ledger, allow_reuse=False)
        self.assertTrue(d.proceed)
        self.assertTrue(d.warning)

    def test_refuses_past_budget_without_override(self):
        from skill_eval import common
        for sha in ("sha-a", "sha-b", "sha-c"):
            common.record_holdout_look("pr-description", sha, "run", ledger=self.ledger)
        d = activation.check_holdout_budget("pr-description", "sha-d", ledger=self.ledger, allow_reuse=False)
        self.assertFalse(d.proceed)
        self.assertTrue(d.refusal)

    def test_override_allows_past_budget(self):
        from skill_eval import common
        for sha in ("sha-a", "sha-b", "sha-c"):
            common.record_holdout_look("pr-description", sha, "run", ledger=self.ledger)
        d = activation.check_holdout_budget("pr-description", "sha-d", ledger=self.ledger, allow_reuse=True)
        self.assertTrue(d.proceed)
        self.assertTrue(d.warning)


class FeedbackTests(unittest.TestCase):
    def _row(self, case_id, split, polarity, hit, tags=None, ok=True, contaminated=False, vendor="claude",
              first_activated=None):
        return {"case_id": case_id, "split": split, "polarity": polarity, "hit": hit,
                "tags": tags or [], "ok": ok, "contaminated": contaminated, "vendor": vendor,
                "skipped_by_cap": False, "stolen": [], "first_activated": first_activated}

    def test_holdout_is_never_leaked_not_even_case_ids(self):
        records = [
            self._row("train-1", "train", "positive", False),
            self._row("holdout-1", "holdout", "positive", False),
            self._row("holdout-2", "holdout", "negative", True),
        ]
        fb = activation.build_feedback(records, verbatim=True)
        dumped = json.dumps(fb)
        self.assertNotIn("holdout-1", dumped)
        self.assertNotIn("holdout-2", dumped)
        self.assertEqual(fb["holdout_calls_omitted"], 2)

    def test_missed_positive_grouped_by_tags(self):
        records = [
            self._row("c1", "train", "positive", False, tags=["near-miss"]),
            self._row("c2", "train", "positive", False, tags=[]),
        ]
        fb = activation.build_feedback(records, verbatim=False)
        self.assertIn("near-miss", fb["missed_positive_by_tags"])
        self.assertIn("untagged", fb["missed_positive_by_tags"])

    def test_verbatim_flag_gates_prompt_text_for_train_only(self):
        case = Case(skill="pr-description", prompt="the actual prompt text", expect=True)
        records = [self._row(case.id, "train", "positive", False)]
        fb_off = activation.build_feedback(records, verbatim=False, all_cases_by_id={case.id: case})
        fb_on = activation.build_feedback(records, verbatim=True, all_cases_by_id={case.id: case})
        dumped_off = json.dumps(fb_off)
        dumped_on = json.dumps(fb_on)
        self.assertNotIn("the actual prompt text", dumped_off)
        self.assertIn("the actual prompt text", dumped_on)

    def test_false_activation_near_miss_vs_other(self):
        records = [
            self._row("c1", "train", "negative", True, tags=["near-miss"]),
            self._row("c2", "train", "negative", True, tags=[]),
        ]
        fb = activation.build_feedback(records, verbatim=False)
        self.assertEqual(len(fb["false_activation_near_miss"]), 1)
        self.assertEqual(len(fb["false_activation_other"]), 1)

    def test_failed_and_contaminated_rows_excluded(self):
        records = [
            self._row("c1", "train", "positive", False, ok=False),
            self._row("c2", "train", "positive", False, contaminated=True),
        ]
        fb = activation.build_feedback(records, verbatim=False)
        total_missed = sum(len(v) for v in fb["missed_positive_by_tags"].values())
        self.assertEqual(total_missed, 0)

    def test_negatives_report_what_fired_instead(self):
        """Round 2 finding 6: negatives never reported which skill fired."""
        records = [
            self._row("c1", "train", "negative", True, first_activated="code-review"),
            self._row("c2", "train", "negative", True, first_activated="code-review"),
            self._row("c3", "train", "negative", True, first_activated="writing-style"),
        ]
        fb = activation.build_feedback(records, verbatim=False)
        self.assertEqual(fb["false_activation_fired_by"], {"code-review": 2, "writing-style": 1})
        for row in fb["false_activation_other"]:
            self.assertIn("first_activated", row)


class SelftestScoringTests(unittest.TestCase):
    """Proves the self-test can fail: a stub that always activates (no
    signal) and one that never activates (detection broken) must both fail,
    while a discriminating stub passes. This is the "confirm a test can fail
    before trusting it" requirement from DESIGN.md T-C."""

    def _rows(self, hits, n, ok=True):
        return [{"hit": h, "ok": ok} for h in ([True] * hits + [False] * (n - hits))]

    def test_fails_when_stub_always_activates_no_better_than_noise(self):
        real = self._rows(6, 6)
        negative = self._rows(6, 6)  # same rate as real: no discriminative signal
        positive_control = self._rows(6, 6)
        result = activation.evaluate_selftest(real, negative, positive_control)
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["passed"])
        self.assertTrue(result["positive_control_ok"])
        self.assertFalse(result["negative_control_ok"])
        self.assertTrue(any("no better than noise" in r for r in result["reasons"]))

    def test_positive_control_below_threshold_is_inconclusive_never_detection_broken(self):
        """Round 3 finding O1 (blocker): a weak positive control means "the
        environment does not let the skill activate", never "detection is
        broken" -- DESIGN.md is explicit that the verdict must never say
        that. The negative control is not even scored in this case."""
        real = self._rows(6, 6)
        negative = self._rows(0, 6)
        positive_control = self._rows(0, 6)  # explicit mention never activates either
        result = activation.evaluate_selftest(real, negative, positive_control)
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertFalse(result["passed"])
        self.assertFalse(result["positive_control_ok"])
        self.assertIsNone(result["negative_control_ok"])
        self.assertIsNone(result["real_rate"])
        self.assertEqual(result["reasons"], [activation.SELFTEST_INCONCLUSIVE_MESSAGE])
        for r in result["reasons"]:
            self.assertNotIn("detection", r.lower())

    def test_passes_with_a_discriminating_stub(self):
        real = self._rows(6, 6)          # 100%
        negative = self._rows(0, 6)      # 0%: drop of 1.0 >= 0.5
        positive_control = self._rows(6, 6)  # 100% >= 0.5
        result = activation.evaluate_selftest(real, negative, positive_control)
        self.assertEqual(result["verdict"], "pass")
        self.assertTrue(result["passed"])
        self.assertEqual(result["reasons"], [])

    def test_no_valid_calls_yields_none_rate_and_inconclusive(self):
        """An empty positive-control sample can't clear the threshold
        either, so this is inconclusive, not a flat failure."""
        result = activation.evaluate_selftest([], [], [])
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertFalse(result["passed"])
        self.assertIsNone(result["real_rate"])

    def _skipped(self, n, reason="--max-calls 7 reached"):
        return [{"hit": False, "ok": False, "error": f"skipped: {reason}"} for _ in range(n)]

    def test_capped_negative_arm_is_inconclusive_never_fail(self):
        """The recorded sys1-mcp run: a cap starved the negative arm, and the
        missing rate was reported as a failed negative control."""
        result = activation.evaluate_selftest(self._rows(4, 7), self._skipped(7), self._rows(3, 3))
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertIsNone(result["negative_control_ok"])
        self.assertEqual(result["real_rate"], 4 / 7)
        self.assertEqual(len(result["reasons"]), 1)
        self.assertIn("negative arm", result["reasons"][0])
        self.assertIn("--max-calls 7 reached", result["reasons"][0])
        self.assertNotIn("no better than noise", result["reasons"][0])

    def test_capped_positive_control_names_the_cap_not_the_environment(self):
        """The recorded codex result: never dispatched, yet reported as an
        environment that does not let the skill activate."""
        result = activation.evaluate_selftest([], [], self._skipped(3))
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertNotEqual(result["reasons"], [activation.SELFTEST_INCONCLUSIVE_MESSAGE])
        self.assertIn("positive control", result["reasons"][0])
        self.assertIn("skipped", result["reasons"][0])

    def test_failed_calls_are_inconclusive_with_the_vendor_error(self):
        failed = [{"hit": False, "ok": False, "error": "authentication failed"} for _ in range(3)]
        result = activation.evaluate_selftest(self._rows(3, 3), failed, self._rows(3, 3))
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertIn("authentication failed", result["reasons"][0])

    def test_partial_arms_still_score_when_both_have_valid_calls(self):
        """A cap that trips after some paired calls leaves a scoreable run."""
        real = self._rows(2, 2) + self._skipped(1)
        negative = self._rows(0, 2) + self._skipped(1)
        result = activation.evaluate_selftest(real, negative, self._rows(3, 3))
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["real_rate"], 1.0)
        self.assertEqual(result["negative_control_rate"], 0.0)


class SelftestPlanBudgetTests(unittest.TestCase):
    """`--max-calls` sizes the selftest plan instead of truncating it."""

    def test_uncapped_plan_uses_every_train_positive(self):
        plan = activation._selftest_plan("s", {"claude": "haiku", "codex": "luna"}, 3, 7)
        self.assertEqual(plan["cases_used"], 7)
        self.assertEqual(plan["call_count_per_vendor"], {"claude": 45, "codex": 45})
        self.assertIsNone(plan["call_budget_per_vendor"])

    def test_cap_is_split_per_vendor_and_shrinks_cases(self):
        plan = activation._selftest_plan("s", {"claude": "haiku", "codex": "luna"}, 3, 7, max_calls=30)
        # 15 per vendor: 3 positive-control calls leave 12, i.e. 2 paired cases at 3 repeats.
        self.assertEqual(plan["call_budget_per_vendor"], 15)
        self.assertEqual(plan["cases_used"], 2)
        self.assertEqual(plan["call_count_per_vendor"], {"claude": 15, "codex": 15})
        self.assertLessEqual(plan["call_count_total"], 30)

    def test_cap_never_raises_cases_above_the_corpus(self):
        plan = activation._selftest_plan("s", {"claude": "haiku"}, 1, 2, max_calls=100)
        self.assertEqual(plan["cases_used"], 2)
        self.assertEqual(plan["call_count_total"], 5)

    def test_cap_below_one_complete_comparison_is_refused(self):
        with self.assertRaises(activation.SelftestBudgetError) as ctx:
            activation._selftest_plan("s", {"claude": "haiku", "codex": "luna"}, 3, 7, max_calls=17)
        self.assertIn("at least 18", str(ctx.exception))


class NegativeControlSkillTests(unittest.TestCase):
    """Round 2 finding 4: the negative control must rename the skill, not
    just its description, keeping the body identical -- only name and
    description differ from the real skill."""

    def test_renamed_skill_has_neutral_name_and_unrelated_description_same_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest_root = Path(tmp)
            dest = activation._build_negative_control_skill_dir("pr-description", dest_root)
            self.assertEqual(dest.name, activation.SELFTEST_NEGATIVE_CONTROL_NAME)
            from skill_eval import common
            fm = common.read_frontmatter(dest / "SKILL.md")
            self.assertEqual(fm["name"], activation.SELFTEST_NEGATIVE_CONTROL_NAME)
            self.assertEqual(fm["description"], activation.SELFTEST_UNRELATED_DESCRIPTION)

            real_text = (Path("/workspace/skills/pr-description/SKILL.md")).read_text(encoding="utf-8")
            real_body = real_text.split("---\n", 2)[2]
            neg_text = (dest / "SKILL.md").read_text(encoding="utf-8")
            neg_body = neg_text.split("---\n", 2)[2]
            self.assertEqual(real_body, neg_body, "only name/description may differ, never the body")


class PerVendorSelftestTests(unittest.TestCase):
    """Round 2 finding 4: selftest must evaluate per vendor, never pooled --
    one broken vendor fails only that vendor's verdict, and the report lists
    each vendor's own result."""

    def test_evaluate_per_vendor_directly(self):
        """Exercises the aggregation shape `_cmd_selftest` builds, without a
        live call: one vendor discriminates cleanly, the other never
        activates at all (detection broken for that vendor only)."""
        def _rows(hits, n):
            return [{"hit": h, "ok": True} for h in ([True] * hits + [False] * (n - hits))]

        good = activation.evaluate_selftest(_rows(6, 6), _rows(0, 6), _rows(6, 6))
        broken = activation.evaluate_selftest(_rows(0, 6), _rows(0, 6), _rows(0, 6))
        per_vendor = {"claude": {**good, "vendor": "claude"}, "codex": {**broken, "vendor": "codex"}}
        overall_passed = all(v["passed"] for v in per_vendor.values())

        self.assertFalse(overall_passed)
        self.assertTrue(per_vendor["claude"]["passed"])
        self.assertFalse(per_vendor["codex"]["passed"])
        # DESIGN.md/finding 4: the report must list each vendor's own verdict,
        # not just a single pooled boolean.
        self.assertIn("claude", per_vendor)
        self.assertIn("codex", per_vendor)


class CompareTests(unittest.TestCase):
    def _row(self, vendor, split, case_id, hit, ok=True, polarity="positive"):
        return {"vendor": vendor, "split": split, "case_id": case_id, "hit": hit, "ok": ok,
                "contaminated": False, "skipped_by_cap": False, "polarity": polarity}

    def test_delta_math_on_common_cases(self):
        records_a = [self._row("claude", "train", "c1", False)] * 2 + [self._row("claude", "train", "c1", True)] * 2
        records_b = [self._row("claude", "train", "c1", True)] * 4
        plan_a = {"repeats": 4, "vendors": {"claude": "haiku"}}
        plan_b = {"repeats": 4, "vendors": {"claude": "haiku"}}
        result = activation.compare_runs(plan_a, records_a, plan_b, records_b)
        self.assertEqual(len(result["deltas"]), 1)
        d = result["deltas"][0]
        self.assertAlmostEqual(d["rate_a"], 0.5)
        self.assertAlmostEqual(d["rate_b"], 1.0)
        self.assertAlmostEqual(d["delta"], 0.5)
        self.assertEqual(result["warnings"], [])

    def test_warns_when_valid_n_below_floor(self):
        """Round 2 finding 6: the floor check now uses valid n, never the
        planned --repeats -- a run that claims 4 repeats but only produced 1
        valid (non-failed, non-contaminated) record must still warn."""
        records_a = [self._row("claude", "train", "c1", True)]
        records_b = [self._row("claude", "train", "c1", True)] * 4
        plan_a = {"repeats": 4, "vendors": {"claude": "haiku"}}
        plan_b = {"repeats": 4, "vendors": {"claude": "haiku"}}
        result = activation.compare_runs(plan_a, records_a, plan_b, records_b)
        self.assertTrue(any("valid n" in w for w in result["warnings"]))

    def test_only_case_ids_common_to_both_runs_are_compared(self):
        records_a = [self._row("claude", "train", "c1", True), self._row("claude", "train", "c2", True)]
        records_b = [self._row("claude", "train", "c1", True)]
        plan_a = {"repeats": 4, "vendors": {"claude": "haiku"}}
        plan_b = {"repeats": 4, "vendors": {"claude": "haiku"}}
        result = activation.compare_runs(plan_a, records_a, plan_b, records_b)
        self.assertEqual([d["case_id"] for d in result["deltas"]], ["c1"])

    def test_model_mismatch_warns(self):
        """Round 2 finding 6: compare did not check that both runs used the
        same models."""
        records_a = [self._row("claude", "train", "c1", True)] * 4
        records_b = [self._row("claude", "train", "c1", True)] * 4
        plan_a = {"repeats": 4, "vendors": {"claude": "haiku"}}
        plan_b = {"repeats": 4, "vendors": {"claude": "sonnet"}}
        result = activation.compare_runs(plan_a, records_a, plan_b, records_b)
        self.assertTrue(any("model mismatch" in w for w in result["warnings"]))

    def test_same_models_no_mismatch_warning(self):
        records_a = [self._row("claude", "train", "c1", True)] * 4
        records_b = [self._row("claude", "train", "c1", True)] * 4
        plan_a = {"repeats": 4, "vendors": {"claude": "haiku"}}
        plan_b = {"repeats": 4, "vendors": {"claude": "haiku"}}
        result = activation.compare_runs(plan_a, records_a, plan_b, records_b)
        self.assertFalse(any("model mismatch" in w for w in result["warnings"]))

    def test_holdout_compared_as_aggregate_never_per_case(self):
        row_a = self._row("claude", "holdout", "h1", True)
        row_b = self._row("claude", "holdout", "h1", False)
        plan_a = {"repeats": 4, "vendors": {"claude": "haiku"}}
        plan_b = {"repeats": 4, "vendors": {"claude": "haiku"}}
        result = activation.compare_runs(plan_a, [row_a], plan_b, [row_b])
        self.assertEqual(result["deltas"], [])
        self.assertEqual(len(result["holdout_aggregate"]), 1)
        entry = result["holdout_aggregate"][0]
        self.assertEqual(entry["vendor"], "claude")
        self.assertEqual(entry["polarity"], "positive")
        self.assertAlmostEqual(entry["rate_a"], 1.0)
        self.assertAlmostEqual(entry["rate_b"], 0.0)


class CapTests(unittest.TestCase):
    """Round 2 finding 5: --max-codex-tokens as codex's own cap (since
    --max-cost-usd never applies to codex), and atomic reservation so
    concurrency cannot overshoot beyond in-flight calls. R2's mutations M7
    and M13 (cap logic disabled) survived the prior tests, so these assert
    the exact dispatched-call count, not just "some" calls were skipped."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        self.run_dir = self.tmp_path / "run"
        self.run_dir.mkdir()
        scratch = self.tmp_path / "scratch"
        for mod in (vendors, activation):
            p = mock.patch.object(mod, "SCRATCH_ROOT", scratch)
            p.start()
            self.addCleanup(p.stop)
        self._builtin_patch = mock.patch.object(vendors, "builtin_baseline", return_value=[])
        self._builtin_patch.start()
        self.addCleanup(self._builtin_patch.stop)
        # A cached (existing) baseline path by default, so these pre-existing
        # cap-count assertions are unaffected by the round 3 fix that counts
        # an UNCACHED baseline probe against --max-calls (see
        # BaselineProbeCapTests below, which patches this to "missing"
        # deliberately to exercise that behaviour).
        cached_marker = self.tmp_path / "cached-baseline.json"
        cached_marker.write_text("{}", encoding="utf-8")
        self._baseline_cache_patch = mock.patch.object(
            vendors, "baseline_cache_path", return_value=cached_marker, create=True)
        self._baseline_cache_patch.start()
        self.addCleanup(self._baseline_cache_patch.stop)
        self._workspace_patch = mock.patch.object(vendors, "prepare_workspace",
                                                    return_value="fixturesha", create=True)
        self._workspace_patch.start()
        self.addCleanup(self._workspace_patch.stop)
        self._trace_patch = mock.patch.object(trace_module, "parse_trace", side_effect=_compat_parse_trace)
        self._trace_patch.start()
        self.addCleanup(self._trace_patch.stop)
        self.skills_map = {"pr-description": Path("/workspace/skills/pr-description")}

    def _plan(self, n, repeats=1, vendors_models=None, **caps):
        cases = [Case(skill="pr-description", prompt=f"p{i}", expect=True) for i in range(n)]
        splits = {"train": cases, "dev": []}
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models=vendors_models or {"claude": "haiku"}, repeats=repeats, split="train",
            cases_by_split=splits, **caps,
        )
        return plan, {c.id: c for c in cases}

    def test_max_calls_cap_stops_dispatch_exactly_at_the_cap(self):
        plan, all_by_id = self._plan(10, max_calls=3)
        call_count = {"n": 0}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            call_count["n"] += 1
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1,
            )
        self.assertEqual(call_count["n"], 3, "exec_agent must never be called more than max_calls times")
        skipped = [r for r in rows if r["skipped_by_cap"]]
        self.assertEqual(len(skipped), 7)

    def test_max_cost_usd_cap_stops_after_threshold_is_crossed(self):
        plan, all_by_id = self._plan(10, max_cost_usd=0.25)
        call_count = {"n": 0}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            call_count["n"] += 1
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            events = [
                json.dumps({"type": "system", "subtype": "init", "skills": ["pr-description"]}),
                json.dumps({"type": "result", "is_error": False, "result": "done", "total_cost_usd": 0.1}),
            ]
            Path(trace_out).write_text("\n".join(events), encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1,
            )
        # 0.1 * 3 = 0.3 >= 0.25 trips after the 3rd call; a 4th must never dispatch.
        self.assertEqual(call_count["n"], 3)

    def test_max_codex_tokens_cap_stops_after_threshold(self):
        plan, all_by_id = self._plan(10, vendors_models={"codex": "gpt-5.6-luna"}, max_codex_tokens=250)
        call_count = {"n": 0}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            call_count["n"] += 1
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            events = [
                json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "done"}}),
                json.dumps({"type": "turn.completed", "usage": {"input_tokens": 80, "output_tokens": 20}}),
            ]
            Path(trace_out).write_text("\n".join(events), encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1,
            )
        # 100 tokens/call; 250 cap trips after the 3rd call (300 >= 250).
        self.assertEqual(call_count["n"], 3)

    def test_no_cap_runs_every_call(self):
        plan, all_by_id = self._plan(4)
        call_count = {"n": 0}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            call_count["n"] += 1
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=2,
            )
        self.assertEqual(call_count["n"], 4)

    def test_max_calls_argparse_flag_present(self):
        parser = _build_parser()
        args = parser.parse_args([
            "activation", "run", "--skill", "pr-description", "--max-codex-tokens", "1000",
        ])
        self.assertEqual(args.max_codex_tokens, 1000)


class _LiveRunHarness(unittest.TestCase):
    """Shared setUp for tests that drive `run_activation` end to end with a
    stubbed `exec_agent`, mirroring `RunActivationExecutionTests.setUp` but
    kept separate so the round 3 test classes below don't depend on that
    class's internals."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        self.run_dir = self.tmp_path / "run"
        self.run_dir.mkdir()
        scratch = self.tmp_path / "scratch"
        for mod in (vendors, activation):
            p = mock.patch.object(mod, "SCRATCH_ROOT", scratch)
            p.start()
            self.addCleanup(p.stop)
        self.scratch = scratch
        p = mock.patch.object(vendors, "builtin_baseline", return_value=[])
        p.start()
        self.addCleanup(p.stop)
        cached_marker = self.tmp_path / "cached-baseline.json"
        cached_marker.write_text("{}", encoding="utf-8")
        p = mock.patch.object(vendors, "baseline_cache_path", return_value=cached_marker, create=True)
        p.start()
        self.addCleanup(p.stop)
        self._workspace_calls = []

        def fake_prepare_workspace(cwd, kind="git"):
            self._workspace_calls.append((Path(cwd), kind))
            return "fixturesha"

        p = mock.patch.object(vendors, "prepare_workspace", side_effect=fake_prepare_workspace, create=True)
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(trace_module, "parse_trace", side_effect=_compat_parse_trace)
        p.start()
        self.addCleanup(p.stop)
        self.skills_map = {"pr-description": Path("/workspace/skills/pr-description")}


class HoldoutErrorScrubTests(_LiveRunHarness):
    """Round 3 finding I3 (blocker): holdout failures are aggregate-only,
    and a holdout call's `error` field -- which can BE the model's own
    reply for a claude is_error result, not merely an echo of the prompt --
    is scrubbed before it ever reaches records.jsonl, never mind
    summary.json/summary.md."""

    def _holdout_plan_and_case(self):
        case = Case(skill="pr-description", prompt="a secret holdout prompt about quarterly numbers",
                    expect=True, source="sealed")
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="holdout",
            cases_by_split={"train": [], "dev": [], "holdout": [case]},
        )
        return plan, {case.id: case}

    def test_holdout_error_field_is_redacted_in_the_row(self):
        plan, all_by_id = self._holdout_plan_and_case()
        prompt = next(iter(all_by_id.values())).prompt

        def fake_exec(vendor, home, cwd, prompt_arg, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            events = [
                json.dumps({"type": "system", "subtype": "init", "skills": ["pr-description"]}),
                json.dumps({"type": "result", "is_error": True,
                            "result": f"Sure -- you asked me to '{prompt_arg}' but I can't help with that.",
                            "total_cost_usd": 0.0}),
            ]
            Path(trace_out).write_text("\n".join(events), encoding="utf-8")
            stderr_path = Path(str(trace_out) + ".err")
            stderr_path.write_text("", encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(stderr_path), "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1,
            )
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["ok"])
        self.assertEqual(rows[0]["error"], activation._HOLDOUT_ERROR_REDACTION_MARKER)
        self.assertNotIn(prompt, rows[0]["error"])
        self.assertNotIn("quarterly numbers", rows[0]["error"])

    def test_holdout_failures_are_count_only_in_summary_json_and_md(self):
        plan, all_by_id = self._holdout_plan_and_case()
        prompt = next(iter(all_by_id.values())).prompt

        def fake_exec(vendor, home, cwd, prompt_arg, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            events = [
                json.dumps({"type": "system", "subtype": "init", "skills": ["pr-description"]}),
                json.dumps({"type": "result", "is_error": True,
                            "result": f"draft the release notes for '{prompt_arg}' failed", "total_cost_usd": 0.0}),
            ]
            Path(trace_out).write_text("\n".join(events), encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1,
            )
        summary = activation.build_summary(plan, rows)
        case_id = next(iter(all_by_id))
        dumped = json.dumps(summary)
        self.assertNotIn(case_id, dumped)
        self.assertNotIn(prompt, dumped)
        self.assertEqual(summary["vendors"]["claude"]["errors"], [])
        self.assertEqual(summary["vendors"]["claude"]["holdout_failed_count"], 1)
        md = activation.render_summary_md(summary)
        self.assertNotIn(case_id, md)
        self.assertNotIn(prompt, md)
        self.assertIn("holdout failures (count only): 1", md)

    def test_holdout_trace_stderr_file_is_scrubbed(self):
        plan, all_by_id = self._holdout_plan_and_case()
        prompt = next(iter(all_by_id.values())).prompt

        def fake_exec(vendor, home, cwd, prompt_arg, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            stderr_path = Path(str(trace_out) + ".err")
            stderr_path.write_text(f"debug: prompt was {prompt_arg!r}", encoding="utf-8")
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(stderr_path), "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            rows = activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1,
            )
        stderr_text = Path(rows[0]["trace_path"] + ".err").read_text(encoding="utf-8")
        self.assertNotIn(prompt, stderr_text)
        self.assertIn(activation._HOLDOUT_REDACTION_MARKER, stderr_text)

    def test_scrub_holdout_stderr_is_a_noop_when_prompt_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            stderr_path = Path(tmp) / "trace.jsonl.err"
            original = "nothing sensitive here"
            stderr_path.write_text(original, encoding="utf-8")
            activation._scrub_holdout_stderr(stderr_path, "a prompt never present here")
            self.assertEqual(stderr_path.read_text(encoding="utf-8"), original)

    def test_redact_tool_inputs_strips_claude_skill_args(self):
        """The reviewer's example: a Skill-tool `args` value (a path derived
        from, but not identical to, the prompt) must be redacted even though
        a literal-prompt substring scrub never touches it."""
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = Path(tmp) / "trace.jsonl"
            events = [
                {"type": "system", "subtype": "init", "skills": ["pr-description"]},
                {"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": "Skill",
                     "input": {"skill": "pr-description", "args": "docs/briefs/checklist-export.md"}},
                ]}},
                {"type": "result", "result": "done", "total_cost_usd": 0.0},
            ]
            trace_path.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
            activation._redact_tool_inputs_in_trace(trace_path)
            text = trace_path.read_text(encoding="utf-8")
        self.assertNotIn("checklist-export.md", text)
        self.assertIn(activation._HOLDOUT_REDACTION_MARKER, text)
        # Still valid JSONL, and the skill list is untouched.
        first = json.loads(text.splitlines()[0])
        self.assertEqual(first["skills"], ["pr-description"])

    def test_redact_tool_inputs_strips_codex_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = Path(tmp) / "trace.jsonl"
            events = [
                {"type": "item.completed", "item": {
                    "id": "i1", "type": "command_execution",
                    "command": "cat docs/briefs/checklist-export.md", "status": "completed",
                    "exit_code": 0, "aggregated_output": "...checklist-export contents..."}},
                {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
            ]
            trace_path.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
            activation._redact_tool_inputs_in_trace(trace_path)
            text = trace_path.read_text(encoding="utf-8")
        self.assertNotIn("checklist-export.md", text)
        self.assertNotIn("checklist-export contents", text)

    def test_redact_tool_inputs_tolerates_malformed_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = Path(tmp) / "trace.jsonl"
            trace_path.write_text("not json at all\n{\"type\": \"result\", \"result\": \"ok\"}\n",
                                   encoding="utf-8")
            activation._redact_tool_inputs_in_trace(trace_path)  # must not raise
            text = trace_path.read_text(encoding="utf-8")
        self.assertIn("not json at all", text)


class ContaminationScratchReadTests(unittest.TestCase):
    """Round 3 finding I5: a read under SCRATCH_ROOT (outside the arm's own
    home/cwd, which trace.parse_trace already excludes via `roots=`) or
    under RUNS_DIR is another arm's or the harness's own material --
    contaminated, tagged `scratch-read`, same tier as `outside-read`."""

    def test_read_under_scratch_root_is_scratch_read_contamination(self):
        other_arm_home = str(common.SCRATCH_ROOT / "homes" / "other-run-codex-00042")
        record = TraceRecord(vendor="claude", outside_reads=[other_arm_home + "/.claude/.credentials.json"])
        reasons, _foreign, other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertTrue(any("scratch-read" in r for r in reasons))
        self.assertEqual(other, [])

    def test_read_under_runs_dir_is_scratch_read_contamination(self):
        # RUNS_DIR defaults under the real home (DESIGN.md: outside the repo
        # AND outside SCRATCH_ROOT), which the real-home rule already
        # catches as `outside-read` -- both tags are "contaminated", so this
        # test points RUNS_DIR somewhere that is under neither, to exercise
        # the `scratch-read` tag specifically (e.g. $SKILL_EVAL_RUNS_DIR
        # pointed at a durable non-home path, as DESIGN.md suggests).
        fake_runs_dir = Path("/opt/skill-eval-runs")
        with mock.patch.object(activation, "RUNS_DIR", fake_runs_dir):
            record = TraceRecord(vendor="claude", outside_reads=[str(fake_runs_dir / "some-run" / "plan.json")])
            reasons, _foreign, other = activation._check_contamination(
                record, "claude", {"pr-description"}, [])
        self.assertTrue(any("scratch-read" in r for r in reasons))
        self.assertEqual(other, [])

    def test_read_under_real_home_runs_dir_is_still_contaminated_as_outside_read(self):
        """When RUNS_DIR is left at its default (under the real home), a
        read there is still caught -- by the real-home rule, which runs
        first -- so it is never silently downgraded to a warning."""
        record = TraceRecord(vendor="claude", outside_reads=[str(common.RUNS_DIR / "some-run" / "plan.json")])
        reasons, _foreign, other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertTrue(any("outside-read" in r or "scratch-read" in r for r in reasons))
        self.assertEqual(other, [])

    def test_selftest_negctrl_dir_under_scratch_root_is_scratch_read(self):
        negctrl = str(common.SCRATCH_ROOT / "selftest-negctrl" / "some-run" / "unit-converter" / "SKILL.md")
        record = TraceRecord(vendor="claude", outside_reads=[negctrl])
        reasons, _foreign, other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertTrue(any("scratch-read" in r for r in reasons))
        self.assertEqual(other, [])

    def test_unrelated_system_path_is_still_only_a_warning(self):
        record = TraceRecord(vendor="claude", outside_reads=["/etc/hostname"])
        reasons, _foreign, other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertEqual([r for r in reasons if "scratch-read" in r or "outside-read" in r], [])
        self.assertEqual(other, ["/etc/hostname"])


class NonNamespacedForeignSkillTests(unittest.TestCase):
    """Round 3 finding I8 (mutation `contam-foreign-unexpected` survived):
    an unexpected but non-namespaced visible skill name must be flagged
    foreign too, not only a namespaced one."""

    def test_non_namespaced_unexpected_skill_is_foreign(self):
        record = TraceRecord(vendor="claude", visible_skills=["pr-description", "some-other-skill"])
        reasons, foreign, _other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertIn("some-other-skill", foreign)
        self.assertTrue(any("unexpected visible skills" in r for r in reasons))

    def test_expected_only_skills_are_never_foreign(self):
        record = TraceRecord(vendor="claude", visible_skills=["pr-description"])
        reasons, foreign, _other = activation._check_contamination(
            record, "claude", {"pr-description"}, [])
        self.assertEqual(foreign, [])
        self.assertEqual(reasons, [])


class PerCallVerifyEnvironmentGuardTests(_LiveRunHarness):
    """Round 3 finding I8 (mutation `per-call-verify-skipped` survived): a
    per-call `verify_environment` error must block that call -- exec_agent
    must never run, and the row must be marked failed with the reason
    recorded."""

    def test_verify_environment_error_blocks_the_call(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="train",
            cases_by_split={"train": cases, "dev": []},
        )
        all_by_id = {c.id: c for c in cases}
        exec_calls = {"n": 0}

        def fake_exec(*a, **kw):
            exec_calls["n"] += 1
            raise AssertionError("exec_agent must never be called after a verify_environment error")

        bad_finding = Finding(severity="error", code="instruction-file-in-cwd", message="bad cwd")
        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec), \
             mock.patch.object(vendors, "verify_environment", return_value=[bad_finding]):
            rows = activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1,
            )
        self.assertEqual(exec_calls["n"], 0)
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["ok"])
        self.assertIn("verify_environment", rows[0]["error"])
        self.assertIn("instruction-file-in-cwd", rows[0]["error"])


class WorkspaceFlagTests(_LiveRunHarness):
    """Round 3 finding O1 (blocker): --workspace prepares each fresh cwd
    through vendors.prepare_workspace BEFORE verify_environment, and the
    fixture sha is recorded in plan.json / summary.json."""

    def test_execute_one_prepares_workspace_before_verify_environment(self):
        order = []

        def fake_prepare(cwd, kind="git"):
            order.append(("prepare_workspace", kind))
            return "sha-abc"

        def fake_verify(vendor, home, cwd, expected):
            order.append(("verify_environment",))
            return []

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="train",
            cases_by_split={"train": cases, "dev": []}, workspace="empty",
        )
        all_by_id = {c.id: c for c in cases}
        with mock.patch.object(vendors, "prepare_workspace", side_effect=fake_prepare, create=True), \
             mock.patch.object(vendors, "verify_environment", side_effect=fake_verify), \
             mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1, workspace_kind="empty",
            )
        self.assertEqual(order[0], ("prepare_workspace", "empty"))
        self.assertEqual(order[1], ("verify_environment",))

    def test_plan_run_records_workspace_kind(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="train",
            cases_by_split={"train": cases, "dev": []}, workspace="empty",
        )
        self.assertEqual(plan["workspace"], "empty")

    def test_plan_run_defaults_workspace_to_git(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="train",
            cases_by_split={"train": cases, "dev": []},
        )
        self.assertEqual(plan["workspace"], "git")
        self.assertEqual(activation.DEFAULT_WORKSPACE, "git")

    def test_preflight_check_records_workspace_sha_into_plan(self):
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="train",
            cases_by_split={"train": [], "dev": []}, workspace="git",
        )
        with mock.patch.object(vendors, "build_home"), \
             mock.patch.object(vendors, "cleanup_home"), \
             mock.patch.object(vendors, "verify_environment", return_value=[]), \
             mock.patch.object(vendors, "prepare_workspace", return_value="the-fixture-sha", create=True):
            findings = activation._preflight_check(plan, "testrun", {}, keep_homes=False)
        self.assertEqual(findings, [])
        self.assertEqual(plan["workspace_sha"], "the-fixture-sha")

    def test_summary_includes_workspace_sha(self):
        plan = {"shape": "isolated", "vendors": {"claude": "haiku"}, "skill": "s",
                "split": "train", "repeats": 1, "description_sha": None,
                "workspace": "git", "workspace_sha": "the-fixture-sha"}
        summary = activation.build_summary(plan, [])
        self.assertEqual(summary["workspace_sha"], "the-fixture-sha")
        md = activation.render_summary_md(summary)
        self.assertIn("the-fixture-sha", md)

    def test_run_cli_has_workspace_flag_defaulting_to_git(self):
        parser = _build_parser()
        args = parser.parse_args(["activation", "run", "--skill", "pr-description"])
        self.assertEqual(args.workspace, "git")
        args = parser.parse_args(["activation", "run", "--skill", "pr-description", "--workspace", "empty"])
        self.assertEqual(args.workspace, "empty")

    def test_selftest_cli_has_workspace_flag_defaulting_to_git(self):
        parser = _build_parser()
        args = parser.parse_args(["activation", "selftest", "--skill", "pr-description"])
        self.assertEqual(args.workspace, "git")


class CompareWorkspaceMismatchTests(unittest.TestCase):
    def test_compare_warns_on_differing_workspace_sha(self):
        plan_a = {"repeats": 4, "vendors": {"claude": "haiku"}, "workspace_sha": "sha-a"}
        plan_b = {"repeats": 4, "vendors": {"claude": "haiku"}, "workspace_sha": "sha-b"}
        result = activation.compare_runs(plan_a, [], plan_b, [])
        self.assertTrue(any("workspace fixture mismatch" in w for w in result["warnings"]))

    def test_compare_is_quiet_when_workspace_sha_matches(self):
        plan_a = {"repeats": 4, "vendors": {"claude": "haiku"}, "workspace_sha": "sha-a"}
        plan_b = {"repeats": 4, "vendors": {"claude": "haiku"}, "workspace_sha": "sha-a"}
        result = activation.compare_runs(plan_a, [], plan_b, [])
        self.assertFalse(any("workspace fixture mismatch" in w for w in result["warnings"]))

    def test_compare_is_quiet_when_workspace_sha_missing(self):
        plan_a = {"repeats": 4, "vendors": {"claude": "haiku"}}
        plan_b = {"repeats": 4, "vendors": {"claude": "haiku"}}
        result = activation.compare_runs(plan_a, [], plan_b, [])
        self.assertFalse(any("workspace fixture mismatch" in w for w in result["warnings"]))


class SelftestVerdictSemanticsTests(unittest.TestCase):
    """Round 3 finding O1 (blocker): pass | fail | inconclusive per vendor,
    and the overall-verdict aggregation rule."""

    def test_overall_verdict_is_fail_when_any_vendor_fails(self):
        per_vendor = {"claude": {"verdict": "pass"}, "codex": {"verdict": "fail"}}
        self.assertEqual(activation._overall_selftest_verdict(per_vendor), "fail")

    def test_overall_verdict_is_inconclusive_when_no_fail_but_some_inconclusive(self):
        per_vendor = {"claude": {"verdict": "pass"}, "codex": {"verdict": "inconclusive"}}
        self.assertEqual(activation._overall_selftest_verdict(per_vendor), "inconclusive")

    def test_overall_verdict_is_pass_only_when_every_vendor_passes(self):
        per_vendor = {"claude": {"verdict": "pass"}, "codex": {"verdict": "pass"}}
        self.assertEqual(activation._overall_selftest_verdict(per_vendor), "pass")

    def test_fail_outranks_inconclusive(self):
        per_vendor = {"a": {"verdict": "inconclusive"}, "b": {"verdict": "fail"}, "c": {"verdict": "pass"}}
        self.assertEqual(activation._overall_selftest_verdict(per_vendor), "fail")

    def test_exit_codes_match_verdicts(self):
        self.assertEqual(activation.SELFTEST_EXIT_CODES["pass"], 0)
        self.assertEqual(activation.SELFTEST_EXIT_CODES["fail"], 1)
        self.assertEqual(activation.SELFTEST_EXIT_CODES["inconclusive"], 3)


class SelftestCliIntegrationTests(unittest.TestCase):
    """End-to-end `_cmd_selftest` tests against a fully stubbed vendors
    module: dry-run, cap sharing (I7), the positive-control-first ordering
    (O1: "the negative control is judged only once the positive control
    passes"), and the exit code for an inconclusive overall verdict."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        scratch = self.tmp_path / "scratch"
        for mod in (vendors, activation):
            p = mock.patch.object(mod, "SCRATCH_ROOT", scratch)
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.object(activation, "RUNS_DIR", self.tmp_path / "runs")
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(vendors, "build_home")
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(vendors, "cleanup_home")
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(vendors, "verify_environment", return_value=[])
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(vendors, "prepare_workspace", return_value="sha", create=True)
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(vendors, "builtin_baseline", return_value=[])
        p.start()
        self.addCleanup(p.stop)
        self.train_positive = Case(skill="pr-description", prompt="draft the pr description now", expect=True)
        p = mock.patch("skill_eval.cases.load_cases", return_value=[self.train_positive])
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch("skill_eval.cases.lint", return_value=[])
        p.start()
        self.addCleanup(p.stop)
        # split_cases is hash-based; force this single case to land in train
        # regardless of the salted hash outcome, so the test never depends
        # on hash luck.
        p = mock.patch.object(activation, "split_cases", return_value={"train": [self.train_positive], "holdout": []})
        p.start()
        self.addCleanup(p.stop)

    def _args(self, extra):
        parser = _build_parser()
        return parser.parse_args([
            "activation", "selftest", "--skill", "pr-description", "--vendors", "claude",
            "--models", "claude=haiku", "--repeats", "2",
        ] + extra)

    def test_dry_run_prints_plan_and_spends_nothing(self):
        with mock.patch.object(vendors, "exec_agent") as fake_exec:
            args = self._args(["--dry-run"])
            rc = args.func(args)
        self.assertEqual(rc, 0)
        fake_exec.assert_not_called()

    def test_positive_control_below_threshold_is_inconclusive_and_skips_real_and_negative(self):
        """The real and negative arms must never be dispatched once the
        positive control fails -- only positive-control calls run."""
        calls = []

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            calls.append(prompt)
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-no-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec), \
             mock.patch("builtins.print"):
            args = self._args([])
            rc = args.func(args)
        self.assertEqual(rc, activation.SELFTEST_EXIT_CODES["inconclusive"])
        # repeats=2 positive-control calls only; real/negative (2 * repeats
        # each) never ran.
        self.assertEqual(len(calls), 2)

    def test_max_calls_below_one_comparison_refuses_before_any_call(self):
        with mock.patch.object(vendors, "exec_agent") as fake_exec, \
             mock.patch("sys.stderr"):
            args = self._args(["--max-calls", "1"])
            rc = args.func(args)
        self.assertEqual(rc, 2)
        fake_exec.assert_not_called()

    def _stub_execute(self, calls, activate_real=True, cost=None):
        """Stub `_execute_one`: the real skill activates, the renamed
        negative-control skill never does."""
        def fake(*, vendor, label, known_skills, **kwargs):
            calls.append((vendor, label))
            name = next(iter(known_skills))
            hit = activate_real and name != activation.SELFTEST_NEGATIVE_CONTROL_NAME
            record = activation.TraceRecord(vendor=vendor, ok=True, activated=[name] if hit else [],
                                            cost_usd=cost if vendor == "claude" else None)
            return record, {}, []
        return fake

    def test_capped_two_vendor_run_reaches_a_verdict_for_both_vendors(self):
        """The recorded failure: a shared cap spent by claude left codex
        undispatched and claude's negative arm empty. Sized per vendor, both
        vendors get a complete paired comparison."""
        calls = []
        with mock.patch.object(activation, "_execute_one", side_effect=self._stub_execute(calls)), \
             mock.patch.object(activation, "_check_contamination", return_value=([], [], [])), \
             mock.patch.object(activation, "split_cases", return_value={"train": [
                 self.train_positive,
                 Case(skill="pr-description", prompt="write up this branch for review", expect=True),
             ], "holdout": []}), \
             mock.patch("builtins.print"):
            parser = _build_parser()
            args = parser.parse_args([
                "activation", "selftest", "--skill", "pr-description", "--vendors", "claude,codex",
                "--models", "claude=haiku,codex=luna", "--repeats", "2", "--max-calls", "12",
            ])
            rc = args.func(args)
        self.assertEqual(rc, activation.SELFTEST_EXIT_CODES["pass"])
        by_vendor = {v: [l for vv, l in calls if vv == v] for v in ("claude", "codex")}
        for vendor, labels in by_vendor.items():
            self.assertEqual(len(labels), 6, vendor)  # 2 positive control + 2 real + 2 negative
            self.assertEqual(sum(l.startswith("negative-") for l in labels), 2, vendor)
        run_dirs = list((self.tmp_path / "runs").iterdir())
        result = json.loads((run_dirs[0] / "selftest.json").read_text())
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["plan"]["cases_used"], 1)
        self.assertEqual(set(result["vendors"]), {"claude", "codex"})

    def test_cost_cap_mid_run_keeps_arms_paired_and_names_the_cap(self):
        calls = []
        with mock.patch.object(activation, "_execute_one",
                               side_effect=self._stub_execute(calls, cost=0.1)), \
             mock.patch.object(activation, "_check_contamination", return_value=([], [], [])), \
             mock.patch("builtins.print"):
            # 3 positive-control calls spend 0.3; the cap then admits exactly
            # one real/negative pair before it trips.
            args = self._args(["--max-cost-usd", "0.35", "--repeats", "3"])
            rc = args.func(args)
        labels = [l for _, l in calls]
        self.assertEqual(sum(l.startswith("real-") for l in labels), 1)
        self.assertEqual(sum(l.startswith("negative-") for l in labels), 1)
        run_dirs = list((self.tmp_path / "runs").iterdir())
        result = json.loads((run_dirs[0] / "selftest.json").read_text())
        claude = result["vendors"]["claude"]
        self.assertIn("--max-cost-usd", claude["stopped_by_cap"])
        self.assertEqual(claude["verdict"], "pass")
        self.assertEqual(claude["calls"]["valid"], 5)
        self.assertEqual(rc, activation.SELFTEST_EXIT_CODES["pass"])

    def test_vendor_exception_still_writes_a_result(self):
        def boom(**kwargs):
            raise RuntimeError("codex binary vanished")

        with mock.patch.object(activation, "_execute_one", side_effect=boom), \
             mock.patch("builtins.print"):
            args = self._args([])
            rc = args.func(args)
        self.assertEqual(rc, activation.SELFTEST_EXIT_CODES["inconclusive"])
        run_dirs = list((self.tmp_path / "runs").iterdir())
        result = json.loads((run_dirs[0] / "selftest.json").read_text())
        self.assertIn("codex binary vanished", result["vendors"]["claude"]["reasons"][0])

    def test_selftest_cwd_and_negctrl_dir_removed_after_the_run(self):
        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec), \
             mock.patch("builtins.print"):
            args = self._args([])
            args.func(args)
        negctrl_root = self.tmp_path / "scratch" / "selftest-negctrl"
        if negctrl_root.exists():
            self.assertEqual(list(negctrl_root.rglob("*")), [])


class HoldoutLedgerReservationOrderTests(unittest.TestCase):
    """Round 3 finding I7 (minor): the ledger look must be recorded BEFORE
    the first holdout call, not after the run finishes -- an interrupted
    run must not spend a look for free. Exercised directly against
    `_cmd_run`'s source ordering via a call-order spy, since a real holdout
    run needs a sealed set and live vendor calls."""

    def test_record_holdout_look_happens_before_run_activation(self):
        order = []
        real_record = common.record_holdout_look
        real_run_activation = activation.run_activation

        def spy_record(*a, **kw):
            order.append("record_holdout_look")
            return real_record(*a, **kw)

        def spy_run_activation(*a, **kw):
            order.append("run_activation")
            return []

        cases = [Case(skill="pr-description", prompt="a sealed prompt", expect=True, source="sealed")]
        sealed_payload = {"header": {"skill": "pr-description", "kind": "holdout"},
                          "payload": {"cases": [{"prompt": c.prompt, "expect": c.expect} for c in cases]}}

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "ledger.jsonl"
            runs_dir = tmp_path / "runs"
            with mock.patch.object(common, "record_holdout_look", side_effect=spy_record), \
                 mock.patch.object(activation, "run_activation", side_effect=spy_run_activation), \
                 mock.patch.object(activation, "RUNS_DIR", runs_dir), \
                 mock.patch.dict(os.environ, {"SKILL_EVAL_HOLDOUT_LEDGER": str(ledger)}), \
                 mock.patch("skill_eval.integrity.sealed_path", return_value=tmp_path / "sealed.holdout.sealed"), \
                 mock.patch("skill_eval.integrity.unseal", return_value=sealed_payload), \
                 mock.patch.object(activation, "_preflight_check", return_value=[]), \
                 mock.patch.object(activation, "skill_dir", return_value=Path("/workspace/skills/pr-description")):
                (tmp_path / "sealed.holdout.sealed").write_text("x", encoding="utf-8")
                parser = _build_parser()
                args = parser.parse_args([
                    "activation", "run", "--skill", "pr-description", "--vendors", "claude",
                    "--models", "claude=haiku", "--repeats", "1", "--split", "holdout",
                ])
                args.func(args)

        self.assertIn("record_holdout_look", order)
        self.assertIn("run_activation", order)
        self.assertLess(order.index("record_holdout_look"), order.index("run_activation"))


class ExecuteOneCwdCleanupTests(_LiveRunHarness):
    """Round 3 finding I7 (minor): a call's cwd under SCRATCH_ROOT is
    removed with its home, unless --keep-homes."""

    def test_cwd_removed_after_call_by_default(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="train",
            cases_by_split={"train": cases, "dev": []},
        )
        all_by_id = {c.id: c for c in cases}
        seen_cwd = {}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            seen_cwd["cwd"] = Path(cwd)
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1,
            )
        self.assertIn("cwd", seen_cwd)
        self.assertFalse(seen_cwd["cwd"].exists())

    def test_cwd_kept_when_keep_homes(self):
        cases = [Case(skill="pr-description", prompt="p1", expect=True)]
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="train",
            cases_by_split={"train": cases, "dev": []},
        )
        all_by_id = {c.id: c for c in cases}
        seen_cwd = {}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            seen_cwd["cwd"] = Path(cwd)
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec):
            activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1, keep_homes=True,
            )
        self.assertTrue(seen_cwd["cwd"].exists())


class BaselineProbeCapTests(_LiveRunHarness):
    """Round 3 finding (minor): an uncached builtin-baseline probe is a real
    agent call and must count against --max-calls."""

    def test_uncached_baseline_probe_consumes_a_slot_from_max_calls(self):
        cases = [Case(skill="pr-description", prompt=f"p{i}", expect=True) for i in range(3)]
        plan = activation.plan_run(
            skill="pr-description", shape="isolated", installed_skills=["pr-description"],
            vendors_models={"claude": "haiku"}, repeats=1, split="train",
            cases_by_split={"train": cases, "dev": []}, max_calls=2,
        )
        all_by_id = {c.id: c for c in cases}
        call_count = {"n": 0}

        def fake_exec(vendor, home, cwd, prompt, trace_out, **kwargs):
            call_count["n"] += 1
            Path(trace_out).parent.mkdir(parents=True, exist_ok=True)
            Path(trace_out).write_bytes((_TRACE_FIXTURES / "claude-activate.jsonl").read_bytes())
            return {"exit_code": 0, "duration_s": 0.1, "trace_path": str(trace_out),
                    "stderr_path": str(trace_out) + ".err", "cmd": []}

        # An UNCACHED baseline path (nonexistent), overriding this harness's
        # default cached one: the probe must be reserved against max_calls.
        with mock.patch.object(vendors, "exec_agent", side_effect=fake_exec), \
             mock.patch.object(vendors, "baseline_cache_path",
                                return_value=Path("/nonexistent-skill-eval-baseline.json"), create=True):
            rows = activation.run_activation(
                plan, run_dir=self.run_dir, skills_map=self.skills_map, description_overrides={},
                run_label="testrun", all_cases_by_id=all_by_id, concurrency=1,
            )
        # max_calls=2, one slot spent on the uncached baseline probe: only
        # one real call may dispatch.
        self.assertEqual(call_count["n"], 1)
        skipped = [r for r in rows if r["skipped_by_cap"]]
        self.assertEqual(len(skipped), 2)


if __name__ == "__main__":
    unittest.main()


class CorpusGateTests(unittest.TestCase):
    """`run` and `selftest` refuse a corpus with lint errors before any call,
    unless `--allow-corpus-errors` is passed, and the plan records it."""

    _ERROR = Finding("error", "template-residue", "pr-description: residue", "x")

    def _parse(self, argv):
        return _build_parser().parse_args(argv)

    def test_run_refuses_a_corpus_with_lint_errors(self):
        with mock.patch("skill_eval.cases.lint", return_value=[self._ERROR]), \
             mock.patch.object(vendors, "exec_agent") as fake_exec, \
             mock.patch("sys.stderr"):
            args = self._parse(["activation", "run", "--skill", "pr-description", "--dry-run"])
            rc = args.func(args)
        self.assertEqual(rc, 2)
        fake_exec.assert_not_called()

    def test_run_with_override_records_the_errors_in_the_plan(self):
        printed = []
        with mock.patch("skill_eval.cases.lint", return_value=[self._ERROR]), \
             mock.patch("skill_eval.cases.load_cases", return_value=_cases(n_pos=2, n_neg=2)), \
             mock.patch.object(activation, "_print_plan", side_effect=printed.append):
            args = self._parse(["activation", "run", "--skill", "pr-description", "--dry-run",
                                "--allow-corpus-errors", "--vendors", "claude", "--models", "claude=haiku"])
            rc = args.func(args)
        self.assertEqual(rc, 0)
        self.assertEqual(printed[0]["corpus_lint"]["errors"], 1)
        self.assertTrue(printed[0]["corpus_lint"]["allowed_with_errors"])

    def test_selftest_refuses_a_corpus_with_lint_errors(self):
        with mock.patch("skill_eval.cases.lint", return_value=[self._ERROR]), \
             mock.patch.object(vendors, "exec_agent") as fake_exec, \
             mock.patch("sys.stderr"):
            args = self._parse(["activation", "selftest", "--skill", "pr-description", "--dry-run"])
            rc = args.func(args)
        self.assertEqual(rc, 2)
        fake_exec.assert_not_called()

    def test_warnings_alone_do_not_block(self):
        warn = Finding("warn", "no-off-register-positive", "pr-description: warn", "x")
        with mock.patch("skill_eval.cases.lint", return_value=[warn]), \
             mock.patch("skill_eval.cases.load_cases", return_value=_cases(n_pos=2, n_neg=2)), \
             mock.patch.object(activation, "_print_plan"):
            args = self._parse(["activation", "run", "--skill", "pr-description", "--dry-run",
                                "--vendors", "claude", "--models", "claude=haiku"])
            rc = args.func(args)
        self.assertEqual(rc, 0)


class SelftestSweepTests(unittest.TestCase):
    """`selftest-all`: child argv pass-through, per-verdict counts, and a
    table that shows an errored child instead of dropping it."""

    def _args(self, extra=()):
        return _build_parser().parse_args(["activation", "selftest-all", *extra])

    def test_child_argv_passes_caps_and_models_through(self):
        args = self._args(["--max-calls", "14", "--repeats", "1", "--models", "claude=haiku"])
        argv = activation._selftest_child_argv("pr-description", args)
        self.assertIn("selftest", argv)
        self.assertEqual(argv[argv.index("--skill") + 1], "pr-description")
        self.assertEqual(argv[argv.index("--max-calls") + 1], "14")
        self.assertEqual(argv[argv.index("--models") + 1], "claude=haiku")
        self.assertNotIn("--max-cost-usd", argv)

    def test_summary_counts_overall_and_per_vendor_verdicts(self):
        results = {
            "a": {"verdict": "pass", "vendors": {"claude": {"verdict": "pass"}, "codex": {"verdict": "pass"}}},
            "b": {"verdict": "inconclusive", "vendors": {"claude": {"verdict": "pass"},
                                                        "codex": {"verdict": "inconclusive"}}},
            "c": {"verdict": "error", "error": "boom"},
        }
        s = activation.summarize_sweep(results)
        self.assertEqual(s["overall"], {"pass": 1, "inconclusive": 1, "error": 1})
        self.assertEqual(s["per_vendor"]["codex"], {"pass": 1, "inconclusive": 1})
        md = activation.render_sweep_md(results, s)
        self.assertIn("| c | error |", md)
        self.assertIn("boom", md)
        self.assertIn("| b | inconclusive | pass |", md)


class ScratchProbeClassificationTests(unittest.TestCase):
    """With the scratch root hardened, a listing or glob of an unlistable
    directory reaches nothing and is recorded only; a concrete path into
    another arm's material stays contamination. Unhardened, every scratch
    reference stays contamination."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "scratch"
        for mod in (vendors, activation):
            p = mock.patch.object(mod, "SCRATCH_ROOT", self.root)
            p.start()
            self.addCleanup(p.stop)

    def _check(self, paths):
        record = TraceRecord(vendor="codex", ok=True, outside_reads=[str(p) for p in paths])
        reasons, _foreign, other = activation._check_contamination(record, "codex", {"s"}, [])
        return reasons, other

    def test_probes_are_recorded_not_contamination_when_hardened(self):
        vendors.harden_scratch_root()
        probes = [self.root, self.root / "cwd", self.root / "cwd" / "*" / "docs",
                  self.root / "homes" / "*" / "skills" / "s" / "SKILL.md"]
        reasons, other = self._check(probes)
        self.assertEqual(reasons, [])
        self.assertEqual(len(other), 4)

    def test_concrete_sibling_path_is_contamination_when_hardened(self):
        vendors.harden_scratch_root()
        reasons, _ = self._check([self.root / "homes" / "run-codex-negative-r0" / "skills" / "s" / "SKILL.md"])
        self.assertTrue(any(r.startswith("scratch-read") for r in reasons))

    def test_unhardened_root_keeps_every_scratch_reference_as_contamination(self):
        (self.root / "cwd").mkdir(parents=True)
        reasons, _ = self._check([self.root / "cwd"])
        self.assertTrue(any(r.startswith("scratch-read") for r in reasons))
