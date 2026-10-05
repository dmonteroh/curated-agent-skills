import sys
import unittest
from pathlib import Path

_AUDITING_DIR = Path(__file__).resolve().parent.parent / "auditing"
if str(_AUDITING_DIR) not in sys.path:
    sys.path.insert(0, str(_AUDITING_DIR))

from skill_eval import cases as C  # noqa: E402
from skill_eval.common import library_skills  # noqa: E402

_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "auditing" / "skill_eval" / "fixtures" / "cases"

# A description shared by the near-miss / off-register / echo fixtures so
# tests control overlap deliberately instead of depending on a real skill's
# wording (SKILL.md files are outside this task's claim set).
_BAKING_DESCRIPTION = (
    "Bake sourdough bread at home with starter maintenance and "
    "troubleshooting tips for beginners."
)


def _fixture_path(name: str) -> Path:
    return _FIXTURES_DIR / f"{name}.md"


def _codes(findings) -> set[str]:
    return {f.code for f in findings}


def _lint_fixture(name: str, description: str | None = None, **kw):
    return C.lint(name, path=_fixture_path(name), description=description, **kw)


class ParsingTests(unittest.TestCase):
    """load_cases / the underlying parser: format variants, never crashes."""

    def test_clean_file_parses_ten_cases(self):
        cases = C.load_cases("clean", path=_fixture_path("clean"))
        self.assertEqual(len(cases), 10)
        self.assertEqual(sum(1 for c in cases if c.expect), 5)
        self.assertEqual(sum(1 for c in cases if not c.expect), 5)

    def test_tags_line_parses_into_case_tags(self):
        cases = C.load_cases("tags", path=_fixture_path("tags"))
        by_prompt = {c.prompt: c for c in cases}
        tagged_pos = [c for c in cases if c.expect and c.tags]
        self.assertTrue(tagged_pos)
        self.assertIn("generated", tagged_pos[0].tags)
        self.assertIn("paraphrase-of:abc123", tagged_pos[0].tags)
        tagged_neg = [c for c in cases if not c.expect and "near-miss" in c.tags]
        self.assertEqual(len(tagged_neg), 1)

    def test_malformed_file_never_raises_and_records_findings(self):
        # The parser must tolerate: an empty prompt, a case with the wrong
        # field name instead of expect_activate, a bad expect_activate
        # value, an unparsable tags line, and a stray bullet outside any
        # case block -- recording each as a Finding instead of crashing.
        cases = C.load_cases("malformed", path=_fixture_path("malformed"))
        findings = C.parse_findings("malformed", path=_fixture_path("malformed"))
        self.assertEqual(len(cases), 10)  # recoverable cases still come through
        codes = _codes(findings)
        self.assertIn("unparsable-case", codes)
        self.assertIn("bad-expect-activate", codes)
        self.assertIn("missing-expect-activate", codes)
        self.assertIn("unparsable-tags-line", codes)
        self.assertIn("unrecognised-list-item", codes)
        severities = {f.code: f.severity for f in findings}
        self.assertEqual(severities["unparsable-case"], "error")
        self.assertEqual(severities["bad-expect-activate"], "error")

    def test_missing_file_is_a_finding_not_an_exception(self):
        cases = C.load_cases("does-not-exist", path=_fixture_path("does-not-exist"))
        findings = C.parse_findings("does-not-exist", path=_fixture_path("does-not-exist"))
        self.assertEqual(cases, [])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, "missing-corpus-file")
        self.assertEqual(findings[0].severity, "error")

    def test_load_cases_never_raises_on_malformed_input(self):
        try:
            C.load_cases("malformed", path=_fixture_path("malformed"))
        except Exception as exc:  # pragma: no cover - failure path
            self.fail(f"load_cases raised {exc!r} instead of returning findings")


class FloorTests(unittest.TestCase):
    def test_below_floor_fires_on_both_polarities(self):
        codes = _codes(_lint_fixture("below-floor"))
        self.assertIn("below-floor-positive", codes)
        self.assertIn("below-floor-negative", codes)

    def test_clean_file_stays_under_the_floor_findings(self):
        codes = _codes(_lint_fixture("clean"))
        self.assertNotIn("below-floor-positive", codes)
        self.assertNotIn("below-floor-negative", codes)
        self.assertNotIn("no-negative-cases", codes)

    def test_zero_negatives_is_its_own_error_code(self):
        codes = _codes(_lint_fixture("no-negative"))
        self.assertIn("no-negative-cases", codes)

    def test_custom_floor_can_be_relaxed(self):
        findings = C.lint("below-floor", path=_fixture_path("below-floor"), min_pos=2, min_neg=1)
        codes = {f.code for f in findings}
        self.assertNotIn("below-floor-positive", codes)
        self.assertNotIn("below-floor-negative", codes)


class NearMissTests(unittest.TestCase):
    def test_overlap_negative_counts_as_near_miss(self):
        codes = _codes(_lint_fixture("near-miss-present", description=_BAKING_DESCRIPTION))
        self.assertNotIn("no-near-miss-negative", codes)

    def test_unrelated_negatives_trigger_the_warning(self):
        codes = _codes(_lint_fixture("near-miss-absent", description=_BAKING_DESCRIPTION))
        self.assertIn("no-near-miss-negative", codes)
        sev = {f.code: f.severity for f in _lint_fixture("near-miss-absent", description=_BAKING_DESCRIPTION)}
        self.assertEqual(sev["no-near-miss-negative"], "warn")

    def test_tag_alone_satisfies_near_miss_without_overlap(self):
        # "clean" fixture's last negative is tagged near-miss but shares no
        # words with an unrelated description -- the tag must still count.
        codes = _codes(_lint_fixture("clean", description="Completely unrelated topic about kayaks."))
        self.assertNotIn("no-near-miss-negative", codes)

    def test_echo_score_and_longest_echo_are_symmetric_with_zero_overlap(self):
        self.assertEqual(C.echo_score("nothing shared here", "totally different words"), 0.0)
        self.assertEqual(C.longest_echo("nothing shared here", "totally different words"), 0)


class OffRegisterTests(unittest.TestCase):
    def test_no_off_register_positive_at_all_fires(self):
        # "off-register-clean" has only realistic sentences: no positive is
        # tagged or detected as off-register, so the corpus never probes
        # register variation. That is the finding, not the absence of one.
        findings = _lint_fixture("off-register-clean")
        codes = _codes(findings)
        self.assertIn("no-off-register-positive", codes)
        sev = {f.code: f.severity for f in findings}
        self.assertEqual(sev["no-off-register-positive"], "warn")

    def test_tagged_off_register_positive_satisfies_the_check(self):
        codes = _codes(_lint_fixture("off-register-tagged"))
        self.assertNotIn("no-off-register-positive", codes)

    def test_detected_off_register_positive_satisfies_the_check(self):
        # "off-register" carries one untagged, short, lowercase, unpunctuated
        # positive ("fix bug now") that the heuristic detects on its own.
        codes = _codes(_lint_fixture("off-register"))
        self.assertNotIn("no-off-register-positive", codes)


class TemplateResidueTests(unittest.TestCase):
    def test_generator_boilerplate_is_flagged_as_error(self):
        findings = _lint_fixture("residue")
        residue = [f for f in findings if f.code == "template-residue"]
        self.assertEqual(len(residue), 2)  # one positive, one negative marker
        self.assertTrue(all(f.severity == "error" for f in residue))

    def test_hand_written_prompts_carry_no_residue(self):
        codes = _codes(_lint_fixture("residue-clean"))
        self.assertNotIn("template-residue", codes)

    def test_residue_markers_match_the_removed_generator(self):
        # These two markers must keep matching the two template shapes
        # cases.py cites from commit 1358f47's parent, so a future edit
        # cannot silently drift.
        self.assertIn("I need help with this:", C.TEMPLATE_RESIDUE_MARKERS)
        self.assertIn("Please do this exactly now:", C.TEMPLATE_RESIDUE_MARKERS)


class DuplicateTests(unittest.TestCase):
    def test_exact_duplicate_prompt_fires(self):
        codes = _codes(_lint_fixture("duplicate"))
        self.assertIn("duplicate-prompt", codes)

    def test_distinct_prompts_stay_quiet(self):
        codes = _codes(_lint_fixture("duplicate-clean"))
        self.assertNotIn("duplicate-prompt", codes)
        self.assertNotIn("near-duplicate-prompt", codes)


class HighEchoTests(unittest.TestCase):
    def test_long_shared_run_fires(self):
        findings = _lint_fixture("high-echo", description=_BAKING_DESCRIPTION)
        hits = [f for f in findings if f.code == "high-echo-positive"]
        self.assertTrue(hits)
        self.assertEqual(hits[0].severity, "warn")

    def test_scattered_overlap_stays_quiet(self):
        codes = _codes(_lint_fixture("high-echo-clean", description=_BAKING_DESCRIPTION))
        self.assertNotIn("high-echo-positive", codes)

    def test_longest_echo_matches_the_threshold_boundary(self):
        run = C.longest_echo(
            "I want to bake sourdough bread at home this weekend.",
            _BAKING_DESCRIPTION,
        )
        self.assertGreaterEqual(run, C.HIGH_ECHO_RUN)


class ExpectContradictsSectionTests(unittest.TestCase):
    def test_expect_activate_against_its_heading_fires(self):
        findings = _lint_fixture("expect-contradicts")
        codes = _codes(findings)
        self.assertIn("expect-contradicts-section", codes)
        sev = {f.code: f.severity for f in findings}
        self.assertEqual(sev["expect-contradicts-section"], "warn")

    def test_matching_sections_stay_quiet(self):
        codes = _codes(_lint_fixture("clean"))
        self.assertNotIn("expect-contradicts-section", codes)

    def test_expect_activate_remains_the_source_of_truth_for_case_expect(self):
        cases = C.load_cases("expect-contradicts", path=_fixture_path("expect-contradicts"))
        by_prompt = {c.prompt: c for c in cases}
        # Under "Positive" but expect_activate: no -> Case.expect is False.
        self.assertFalse(by_prompt["Recommend a good beginner sourdough recipe with a starter guide."].expect)
        # Under "Negative" but expect_activate: yes -> Case.expect is True.
        self.assertTrue(by_prompt["Give me sourdough baking troubleshooting tips for a dense loaf."].expect)


class CrossSkillCollisionTests(unittest.TestCase):
    def test_shared_positive_prompt_is_a_warn_collision(self):
        results = C.lint_all(["collision-a", "collision-b"], cases_dir=_FIXTURES_DIR)
        for skill in ("collision-a", "collision-b"):
            codes = {f.code for f in results[skill]}
            self.assertIn("cross-skill-positive-collision", codes)
            sev = {f.code: f.severity for f in results[skill]}
            self.assertEqual(sev["cross-skill-positive-collision"], "warn")

    def test_positive_for_one_negative_for_other_is_info(self):
        results = C.lint_all(["collision-a", "collision-b"], cases_dir=_FIXTURES_DIR)
        for skill in ("collision-a", "collision-b"):
            sev = {f.code: f.severity for f in results[skill]}
            self.assertEqual(sev["cross-skill-competitive-probe"], "info")

    def test_unrelated_skills_have_no_collisions(self):
        results = C.lint_all(["clean", "residue-clean"], cases_dir=_FIXTURES_DIR)
        for skill in ("clean", "residue-clean"):
            codes = {f.code for f in results[skill]}
            self.assertNotIn("cross-skill-positive-collision", codes)
            self.assertNotIn("cross-skill-competitive-probe", codes)


class StatsTests(unittest.TestCase):
    def test_stats_counts_match_load_cases(self):
        # stats() reads the real corpus by default; smoke-test its shape on
        # one real skill rather than duplicating a fixture-based parse.
        skill = library_skills()[0]
        data = C.stats([skill])
        self.assertIn(skill, data)
        cases = C.load_cases(skill)
        self.assertEqual(data[skill]["positive"], sum(1 for c in cases if c.expect))
        self.assertEqual(data[skill]["negative"], sum(1 for c in cases if not c.expect))


class LibraryIntegrationTests(unittest.TestCase):
    """Acceptance smoke tests: the CLI paths run over the whole real corpus
    without crashing (they may, and are expected to, report findings)."""

    def test_lint_all_runs_over_the_whole_library(self):
        skills = library_skills()
        self.assertGreater(len(skills), 50)
        results = C.lint_all(skills)
        self.assertEqual(set(results), set(skills))

    def test_stats_runs_over_the_whole_library(self):
        skills = library_skills()
        data = C.stats(skills)
        self.assertEqual(set(data), set(skills))
        for row in data.values():
            self.assertIn("positive", row)
            self.assertIn("max_echo", row)

    def test_lint_all_and_stats_smoke_over_the_real_corpus(self):
        # Smoke test only: lint_all() and stats() must run over the whole
        # real corpus without crashing and return exactly one entry per
        # skill. Behavioural assertions (floor, near-miss, off-register,
        # expect-contradicts-section, residue) are pinned on fixtures above,
        # never on the live corpus -- asserting a live defect stays present
        # would make fixing that defect a test failure, which is the rule
        # this repo learned not to violate. See the task report for the
        # corpus's measured counts at time of writing.
        skills = library_skills()
        results = C.lint_all(skills)
        data = C.stats(skills)
        self.assertEqual(set(results), set(skills))
        self.assertEqual(set(data), set(skills))


if __name__ == "__main__":
    unittest.main()
