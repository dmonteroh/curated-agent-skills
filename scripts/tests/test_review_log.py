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

    def test_mermaid_401_unauthorized_line_is_not_infra_failure(self):
        result = _classify_fixture("infra-negative-mermaid-401.txt")
        self.assertEqual(result.outcome, Outcome.MALFORMED)

    def test_bare_503_token_count_is_not_infra_failure(self):
        result = _classify_fixture("infra-negative-token-count-503.txt")
        self.assertEqual(result.outcome, Outcome.MALFORMED)

    def test_upstream_errors_prose_is_not_infra_failure(self):
        result = _classify_fixture("infra-negative-upstream-errors-prose.txt")
        self.assertEqual(result.outcome, Outcome.MALFORMED)

    def test_backticked_error_mid_sentence_is_not_infra_failure(self):
        result = _classify_fixture("infra-negative-backticked-error.txt")
        self.assertEqual(result.outcome, Outcome.MALFORMED)


if __name__ == "__main__":
    unittest.main()
