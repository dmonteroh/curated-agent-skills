import sys
import unittest
from pathlib import Path

_AUDITING_DIR = Path(__file__).resolve().parent.parent / "auditing"
if str(_AUDITING_DIR) not in sys.path:
    sys.path.insert(0, str(_AUDITING_DIR))

from review_log import Outcome, classify  # noqa: E402

_FIXTURES_DIR = _AUDITING_DIR / "test-fixtures"


def _read(name: str) -> str:
    return (_FIXTURES_DIR / name).read_text()


def _classify_fixture(name: str):
    return classify(_read(name))


class InfraFailurePrecheckTests(unittest.TestCase):
    def test_transport_failure_with_zero_model_output_is_infra_failure(self):
        result = _classify_fixture("infra-failure-http400.txt")
        self.assertEqual(result.outcome, Outcome.INFRA_FAILURE)
        self.assertIsNone(result.differentiation)
        self.assertIsNone(result.removal_proposals)

    def test_mermaid_401_unauthorized_line_is_not_infra_failure(self):
        result = _classify_fixture("infra-negative-mermaid-401.txt")
        self.assertEqual(result.outcome, Outcome.CHANGED)

    def test_bare_503_token_count_is_not_infra_failure(self):
        result = _classify_fixture("infra-negative-token-count-503.txt")
        self.assertEqual(result.outcome, Outcome.NO_CHANGE)

    def test_upstream_errors_prose_is_not_infra_failure(self):
        result = _classify_fixture("infra-negative-upstream-errors-prose.txt")
        self.assertEqual(result.outcome, Outcome.NO_CHANGE)

    def test_backticked_error_mid_sentence_is_not_infra_failure(self):
        result = _classify_fixture("infra-negative-backticked-error.txt")
        self.assertEqual(result.outcome, Outcome.CHANGED)

    def test_positional_guard_recovers_status_line_after_banner(self):
        result = _classify_fixture("infra-guard-recovers-status-line.txt")
        self.assertEqual(result.outcome, Outcome.CHANGED)
        self.assertEqual(result.differentiation, "STRONG")
        self.assertIsNone(result.removal_proposals)

    def test_positional_guard_recovers_questions_after_banner(self):
        result = _classify_fixture("infra-guard-recovers-questions.txt")
        self.assertEqual(result.outcome, Outcome.QUESTIONS)
        self.assertIsNone(result.differentiation)
        self.assertIsNone(result.removal_proposals)


class QuestionsDetectionTests(unittest.TestCase):
    def test_bare_questions_line(self):
        self.assertEqual(_classify_fixture("questions-bare.txt").outcome, Outcome.QUESTIONS)

    def test_questions_with_colon(self):
        self.assertEqual(_classify_fixture("questions-colon.txt").outcome, Outcome.QUESTIONS)

    def test_questions_as_markdown_heading(self):
        self.assertEqual(_classify_fixture("questions-heading.txt").outcome, Outcome.QUESTIONS)

    def test_questions_bold(self):
        self.assertEqual(_classify_fixture("questions-bold.txt").outcome, Outcome.QUESTIONS)

    def test_real_log_with_duplicated_final_message_still_detects_questions(self):
        result = _classify_fixture("questions-real.txt")
        self.assertEqual(result.outcome, Outcome.QUESTIONS)
        self.assertIsNone(result.differentiation)
        self.assertIsNone(result.removal_proposals)


class DuplicateFinalMessageTests(unittest.TestCase):
    def test_duplicated_none_removal_proposals_does_not_false_positive(self):
        result = _classify_fixture("removal-duplicate-none.txt")
        self.assertEqual(result.outcome, Outcome.CHANGED)
        self.assertIsNone(result.removal_proposals)
        self.assertEqual(result.differentiation, "STRONG")


class SilentMissTableTests(unittest.TestCase):
    """One test per row of the nine-row silent-miss table."""

    def test_row1_compliant_form_is_detected_and_not_malformed(self):
        result = _classify_fixture("removal-compliant-baseline.txt")
        self.assertEqual(result.outcome, Outcome.CHANGED)
        self.assertIsNotNone(result.removal_proposals)

    def test_row2_markdown_heading_lowercase(self):
        result = _classify_fixture("removal-row2-heading-lowercase.txt")
        self.assertEqual(result.outcome, Outcome.NO_CHANGE)
        self.assertIsNotNone(result.removal_proposals)

    def test_row3_markdown_heading_uppercase_with_colon(self):
        result = _classify_fixture("removal-row3-heading-upper-colon.txt")
        self.assertEqual(result.outcome, Outcome.CHANGED)
        self.assertIsNotNone(result.removal_proposals)

    def test_row4_bold_no_colon(self):
        result = _classify_fixture("removal-row4-bold-no-colon.txt")
        self.assertEqual(result.outcome, Outcome.NO_CHANGE)
        self.assertIsNotNone(result.removal_proposals)

    def test_row4_bold_with_colon(self):
        result = _classify_fixture("removal-row4-bold-colon.txt")
        self.assertEqual(result.outcome, Outcome.CHANGED)
        self.assertIsNotNone(result.removal_proposals)

    def test_row5_title_case_with_colon(self):
        result = _classify_fixture("removal-row5-titlecase-colon.txt")
        self.assertEqual(result.outcome, Outcome.NO_CHANGE)
        self.assertIsNotNone(result.removal_proposals)

    def test_row6_indented(self):
        result = _classify_fixture("removal-row6-indented.txt")
        self.assertEqual(result.outcome, Outcome.CHANGED)
        self.assertIsNotNone(result.removal_proposals)

    def test_row6_dash_bulleted(self):
        result = _classify_fixture("removal-row6-bulleted.txt")
        self.assertEqual(result.outcome, Outcome.NO_CHANGE)
        self.assertIsNotNone(result.removal_proposals)

    def test_row7_underscore_label(self):
        result = _classify_fixture("removal-row7-underscore.txt")
        self.assertEqual(result.outcome, Outcome.CHANGED)
        self.assertIsNotNone(result.removal_proposals)

    def test_row8_no_colon(self):
        result = _classify_fixture("removal-row8-no-colon.txt")
        self.assertEqual(result.outcome, Outcome.NO_CHANGE)
        self.assertIsNotNone(result.removal_proposals)

    def test_row9_block_omitted_entirely_is_malformed(self):
        result = _classify_fixture("removal-row9-omitted.txt")
        self.assertEqual(result.outcome, Outcome.MALFORMED)
        self.assertIsNone(result.removal_proposals)


class MalformedResidualBucketTests(unittest.TestCase):
    def test_no_status_and_no_questions_anywhere_is_malformed(self):
        result = _classify_fixture("malformed-no-status-no-questions.txt")
        self.assertEqual(result.outcome, Outcome.MALFORMED)


class QuestionsOptionalBlocksTests(unittest.TestCase):
    def test_questions_outcome_never_reports_malformed_for_missing_blocks(self):
        for name in ("questions-bare.txt", "questions-colon.txt", "questions-heading.txt", "questions-bold.txt"):
            with self.subTest(fixture=name):
                result = _classify_fixture(name)
                self.assertEqual(result.outcome, Outcome.QUESTIONS)
                self.assertIsNone(result.removal_proposals)
                self.assertIsNone(result.differentiation)

    def test_questions_outcome_returns_present_differentiation_and_removal_blocks(self):
        result = _classify_fixture("questions-with-differentiation-and-removal.txt")
        self.assertEqual(result.outcome, Outcome.QUESTIONS)
        self.assertEqual(result.differentiation, "WEAK")
        self.assertIsNotNone(result.removal_proposals)
        self.assertIn("appendix.md", result.removal_proposals)


if __name__ == "__main__":
    unittest.main()
