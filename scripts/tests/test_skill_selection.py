from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = Path(__file__).resolve().parent
RUNNER = REPO_ROOT / "scripts" / "auditing" / "run_parallel_skill_reviews.sh"
LOGDIR = REPO_ROOT / "scripts" / "auditing" / "logs"
RETRY_FILE = LOGDIR / "retry-skills.txt"

sys.path.insert(0, str(TESTS_DIR))
from test_read_proof import FIXTURE_SKILL, _run_dual  # noqa: E402


def _list_skills(*skill_args: str) -> subprocess.CompletedProcess:
    # --list-skills exits after selection and before dispatch or skill
    # existence checks, so parse behavior is testable with fabricated names.
    # Client/model banner lines print before the list; the selected names
    # are the final lines of stdout.
    return subprocess.run(
        [str(RUNNER), *skill_args, "--list-skills", "--no-install"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _selected(proc: subprocess.CompletedProcess, count: int) -> list[str]:
    return proc.stdout.strip().split("\n")[-count:]


class SkillFlagCommaListTests(unittest.TestCase):
    def test_comma_separated_value_selects_each_name(self):
        proc = _list_skills("--skill", "alpha,beta")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(_selected(proc, 2), ["alpha", "beta"])

    def test_repeated_flags_and_comma_lists_combine(self):
        proc = _list_skills("--skill", "alpha", "--skill", "beta,gamma")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(_selected(proc, 3), ["alpha", "beta", "gamma"])

    def test_whitespace_around_names_is_stripped(self):
        proc = _list_skills("--skill", " alpha, beta ,gamma")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(_selected(proc, 3), ["alpha", "beta", "gamma"])

    def test_trailing_comma_is_tolerated(self):
        proc = _list_skills("--skill", "alpha,")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(_selected(proc, 1), ["alpha"])

    def test_empty_value_is_refused_not_a_full_roster_run(self):
        for value in ("", ",", " , "):
            with self.subTest(value=repr(value)):
                proc = _list_skills("--skill", value)
                self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
                self.assertIn("--skill needs at least one skill name", proc.stderr)


class RetryListEmissionTests(unittest.TestCase):
    def setUp(self):
        if RETRY_FILE.exists():
            snapshot = RETRY_FILE.read_bytes()
            self.addCleanup(RETRY_FILE.write_bytes, snapshot)
        else:
            self.addCleanup(lambda: RETRY_FILE.unlink(missing_ok=True))

    def test_failed_run_prints_paste_ready_retry_line_and_saves_file(self):
        proc = _run_dual("mismatch")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn(
            f"run_parallel_skill_reviews.sh --skill {FIXTURE_SKILL}", proc.stdout
        )
        self.assertEqual(
            RETRY_FILE.read_text(encoding="utf-8").split(), [FIXTURE_SKILL]
        )

    def test_clean_run_emits_no_retry_line(self):
        proc = _run_dual("match")
        self.assertNotIn("Retry:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
