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


class SynthesisArtifactClassificationTests(unittest.TestCase):
    def test_no_change_artifact_classifies_no_change(self):
        result = _classify_fixture("synthesis-no-change.txt")
        self.assertEqual(result.outcome, Outcome.NO_CHANGE)
        self.assertEqual(result.differentiation, "STRONG")
        self.assertIsNone(result.removal_proposals)

    def test_changed_artifact_classifies_changed(self):
        result = _classify_fixture("synthesis-changed.txt")
        self.assertEqual(result.outcome, Outcome.CHANGED)
        self.assertEqual(result.differentiation, "WEAK")
        self.assertIsNotNone(result.removal_proposals)
        self.assertIn("Example Output Skeleton", result.removal_proposals)

    def test_questions_artifact_classifies_questions(self):
        result = _classify_fixture("synthesis-questions.txt")
        self.assertEqual(result.outcome, Outcome.QUESTIONS)
        self.assertEqual(result.differentiation, "STRONG")
        self.assertIsNone(result.removal_proposals)

    def test_malformed_artifact_classifies_malformed(self):
        result = _classify_fixture("synthesis-malformed-truncated.txt")
        self.assertEqual(result.outcome, Outcome.MALFORMED)
        self.assertIsNone(result.differentiation)
        self.assertIsNone(result.removal_proposals)

    def test_quoted_reviewer_text_artifact_classifies_questions(self):
        # Regression pin: the fixture quotes a complete REVIEW_STATUS: +
        # REMOVAL PROPOSALS: pair from a reviewer's own log, using the
        # synthesis prompt's inline escape so the quoted pair never opens
        # its own line. If the escape is dropped in favor of leading
        # whitespace, a fence, a bullet, or bold, review_log.classify()
        # reads the quoted REVIEW_STATUS: NO-CHANGE as this artifact's own
        # and the trailing QUESTIONS line is never reached.
        result = _classify_fixture("synthesis-questions-quoted-reviewer.txt")
        self.assertEqual(result.outcome, Outcome.QUESTIONS)
        self.assertEqual(result.differentiation, "STRONG")
        self.assertIsNone(result.removal_proposals)


if __name__ == "__main__":
    unittest.main()
