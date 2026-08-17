from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(TESTS_DIR))

SCRIPT = REPO_ROOT / "scripts" / "auditing" / "review-result.sh"


def _run(args, *, review_result_file=None, unset_var=False, removals_file=None):
    env = os.environ.copy()
    if unset_var:
        env.pop("REVIEW_RESULT_FILE", None)
    elif review_result_file is not None:
        env["REVIEW_RESULT_FILE"] = review_result_file
    if removals_file is None:
        env.pop("REVIEW_REMOVALS_FILE", None)
    else:
        env["REVIEW_REMOVALS_FILE"] = removals_file
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _tmp_siblings(directory):
    return sorted(p.name for p in Path(directory).glob("*.tmp.*"))


class OutcomeQuestionsSuccessTest(unittest.TestCase):
    def test_status_questions_with_read_proof_writes_exact_four_lines(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proc = _run(["--status", "questions", "--read-proof", "x"], review_result_file=target)
            self.assertEqual(proc.returncode, 0)
            content = Path(target).read_text(encoding="utf-8")
            self.assertEqual(
                content,
                "OUTCOME=QUESTIONS\nDIFFERENTIATION=None\nREMOVAL_PROPOSALS=0\nREAD_PROOF=x\n",
            )
            self.assertEqual(_tmp_siblings(d), [])


class CrossFieldRequirementsTest(unittest.TestCase):
    def test_status_changed_missing_differentiation_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proc = _run(["--status", "changed", "--removals", "none"], review_result_file=target)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("--differentiation", proc.stderr)
            self.assertFalse(Path(target).exists())
            self.assertEqual(_tmp_siblings(d), [])

    def test_status_changed_missing_removals_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proc = _run(["--status", "changed", "--differentiation", "strong"], review_result_file=target)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("--removals", proc.stderr)
            self.assertFalse(Path(target).exists())
            self.assertEqual(_tmp_siblings(d), [])

    def test_status_questions_forbids_differentiation(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            pre = "PREEXISTING\n"
            Path(target).write_text(pre, encoding="utf-8")
            proc = _run(["--status", "questions", "--differentiation", "strong"], review_result_file=target)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("--differentiation", proc.stderr)
            self.assertEqual(Path(target).read_text(encoding="utf-8"), pre)
            self.assertEqual(_tmp_siblings(d), [])

    def test_status_questions_forbids_removals(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            pre = "PREEXISTING\n"
            Path(target).write_text(pre, encoding="utf-8")
            proc = _run(["--status", "questions", "--removals", "none"], review_result_file=target)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("--removals", proc.stderr)
            self.assertEqual(Path(target).read_text(encoding="utf-8"), pre)
            self.assertEqual(_tmp_siblings(d), [])


class EnumAndFlagValidationTest(unittest.TestCase):
    def test_unknown_status_value_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            pre = "PREEXISTING\n"
            Path(target).write_text(pre, encoding="utf-8")
            proc = _run(
                ["--status", "bogus", "--differentiation", "strong", "--removals", "none"],
                review_result_file=target,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("--status", proc.stderr)
            self.assertEqual(Path(target).read_text(encoding="utf-8"), pre)
            self.assertEqual(_tmp_siblings(d), [])

    def test_unknown_differentiation_value_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            pre = "PREEXISTING\n"
            Path(target).write_text(pre, encoding="utf-8")
            proc = _run(
                ["--status", "changed", "--differentiation", "bogus", "--removals", "none"],
                review_result_file=target,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("--differentiation", proc.stderr)
            self.assertEqual(Path(target).read_text(encoding="utf-8"), pre)
            self.assertEqual(_tmp_siblings(d), [])

    def test_unknown_flag_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            pre = "PREEXISTING\n"
            Path(target).write_text(pre, encoding="utf-8")
            proc = _run(["--bogus", "value"], review_result_file=target)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("--bogus", proc.stderr)
            self.assertEqual(Path(target).read_text(encoding="utf-8"), pre)
            self.assertEqual(_tmp_siblings(d), [])


class ReviewResultFileRequirementTest(unittest.TestCase):
    def test_unset_review_result_file_rejected(self):
        proc = _run(["--status", "questions"], unset_var=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("REVIEW_RESULT_FILE", proc.stderr)

    def test_empty_review_result_file_rejected(self):
        proc = _run(["--status", "questions"], review_result_file="")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("REVIEW_RESULT_FILE", proc.stderr)


class ReadProofTest(unittest.TestCase):
    def test_read_proof_round_trips_verbatim(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proof = "a=b and `x` \\n tab\tend"
            proc = _run(["--status", "questions", "--read-proof", proof], review_result_file=target)
            self.assertEqual(proc.returncode, 0)
            content = Path(target).read_text(encoding="utf-8")
            self.assertEqual(content.splitlines()[-1], f"READ_PROOF={proof}")

    def test_read_proof_omitted_writes_three_lines_no_key(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proc = _run(["--status", "questions"], review_result_file=target)
            self.assertEqual(proc.returncode, 0)
            content = Path(target).read_text(encoding="utf-8")
            self.assertEqual(
                content,
                "OUTCOME=QUESTIONS\nDIFFERENTIATION=None\nREMOVAL_PROPOSALS=0\n",
            )
            self.assertNotIn("READ_PROOF", content)

    def test_read_proof_with_embedded_newline_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            pre = "PREEXISTING\n"
            Path(target).write_text(pre, encoding="utf-8")
            proc = _run(
                ["--status", "questions", "--read-proof", "first line\nOUTCOME=FORGED\nfake=1"],
                review_result_file=target,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("--read-proof", proc.stderr)
            self.assertEqual(Path(target).read_text(encoding="utf-8"), pre)
            self.assertEqual(_tmp_siblings(d), [])


class ReinvocationTest(unittest.TestCase):
    def test_last_call_wins_no_appended_residue(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proc1 = _run(
                ["--status", "changed", "--differentiation", "strong", "--removals", "none"],
                review_result_file=target,
            )
            self.assertEqual(proc1.returncode, 0)
            proc2 = _run(["--status", "questions", "--read-proof", "y"], review_result_file=target)
            self.assertEqual(proc2.returncode, 0)
            content = Path(target).read_text(encoding="utf-8")
            self.assertEqual(
                content,
                "OUTCOME=QUESTIONS\nDIFFERENTIATION=None\nREMOVAL_PROPOSALS=0\nREAD_PROOF=y\n",
            )
            self.assertEqual(_tmp_siblings(d), [])

    def test_failed_call_between_successes_does_not_corrupt(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proc1 = _run(
                ["--status", "changed", "--differentiation", "strong", "--removals", "none"],
                review_result_file=target,
            )
            self.assertEqual(proc1.returncode, 0)
            first_content = Path(target).read_text(encoding="utf-8")

            proc_fail = _run(["--status", "bogus"], review_result_file=target)
            self.assertNotEqual(proc_fail.returncode, 0)
            self.assertEqual(Path(target).read_text(encoding="utf-8"), first_content)
            self.assertEqual(_tmp_siblings(d), [])

            proc3 = _run(["--status", "questions", "--read-proof", "z"], review_result_file=target)
            self.assertEqual(proc3.returncode, 0)
            content = Path(target).read_text(encoding="utf-8")
            self.assertEqual(
                content,
                "OUTCOME=QUESTIONS\nDIFFERENTIATION=None\nREMOVAL_PROPOSALS=0\nREAD_PROOF=z\n",
            )
            self.assertEqual(_tmp_siblings(d), [])


class RemovalsAndDifferentiationNormalizationTest(unittest.TestCase):
    def test_removals_free_text_counts_as_proposal(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proc = _run(
                ["--status", "changed", "--differentiation", "weak", "--removals", "trim the intro"],
                review_result_file=target,
            )
            self.assertEqual(proc.returncode, 0)
            content = Path(target).read_text(encoding="utf-8")
            self.assertEqual(
                content,
                "OUTCOME=CHANGED\nDIFFERENTIATION=WEAK\nREMOVAL_PROPOSALS=1\n",
            )
            self.assertEqual(_tmp_siblings(d), [])

    def test_removals_none_variants_normalize_to_zero(self):
        for value in (
            "none",
            "None",
            "NONE",
            "nOnE",
            " none ",
            "  NONE  ",
            "\tnone\t",
            " \t nOnE \t ",
        ):
            with self.subTest(removals=value):
                with tempfile.TemporaryDirectory() as d:
                    target = str(Path(d) / "result.txt")
                    proc = _run(
                        ["--status", "changed", "--differentiation", "weak", "--removals", value],
                        review_result_file=target,
                    )
                    self.assertEqual(proc.returncode, 0)
                    content = Path(target).read_text(encoding="utf-8")
                    self.assertEqual(
                        content,
                        "OUTCOME=CHANGED\nDIFFERENTIATION=WEAK\nREMOVAL_PROPOSALS=0\n",
                    )
                    self.assertEqual(_tmp_siblings(d), [])

    def test_status_no_change_differentiation_strong_removals_none(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proc = _run(
                ["--status", "no-change", "--differentiation", "strong", "--removals", "none"],
                review_result_file=target,
            )
            self.assertEqual(proc.returncode, 0)
            content = Path(target).read_text(encoding="utf-8")
            self.assertEqual(
                content,
                "OUTCOME=NO-CHANGE\nDIFFERENTIATION=STRONG\nREMOVAL_PROPOSALS=0\n",
            )
            self.assertEqual(_tmp_siblings(d), [])

    def test_removals_empty_string_counts_as_proposal(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proc = _run(
                ["--status", "changed", "--differentiation", "weak", "--removals", ""],
                review_result_file=target,
            )
            self.assertEqual(proc.returncode, 0)
            content = Path(target).read_text(encoding="utf-8")
            self.assertEqual(
                content,
                "OUTCOME=CHANGED\nDIFFERENTIATION=WEAK\nREMOVAL_PROPOSALS=1\n",
            )
            self.assertEqual(_tmp_siblings(d), [])


class RemovalsSidecarTest(unittest.TestCase):
    """REVIEW_REMOVALS_FILE is the runner's opt-in: set only on the synthesis
    call, it captures the --removals text verbatim for proposals.py record."""

    def test_removals_text_written_verbatim_when_sidecar_requested(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            sidecar = str(Path(d) / "result.removals")
            text = "1. `SKILL.md`, `## X` (whole section) - evidence.\n2. second."
            proc = _run(
                ["--status", "changed", "--differentiation", "strong", "--removals", text],
                review_result_file=target,
                removals_file=sidecar,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(Path(sidecar).read_text(encoding="utf-8"), text + "\n")
            self.assertIn("REMOVAL_PROPOSALS=1", Path(target).read_text(encoding="utf-8"))
            self.assertEqual(_tmp_siblings(d), [])

    def test_removals_none_clears_a_stale_sidecar(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            sidecar = Path(d) / "result.removals"
            sidecar.write_text("stale\n", encoding="utf-8")
            proc = _run(
                ["--status", "no-change", "--differentiation", "strong", "--removals", "none"],
                review_result_file=target,
                removals_file=str(sidecar),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse(sidecar.exists())
            self.assertEqual(_tmp_siblings(d), [])

    def test_status_questions_clears_a_stale_sidecar(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            sidecar = Path(d) / "result.removals"
            sidecar.write_text("stale\n", encoding="utf-8")
            proc = _run(
                ["--status", "questions", "--read-proof", "x"],
                review_result_file=target,
                removals_file=str(sidecar),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse(sidecar.exists())

    def test_no_sidecar_env_means_no_sidecar_file(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            proc = _run(
                ["--status", "changed", "--differentiation", "weak", "--removals", "1. cut it."],
                review_result_file=target,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(sorted(p.name for p in Path(d).iterdir()), ["result.txt"])

    def test_validation_failure_leaves_existing_sidecar_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            target = str(Path(d) / "result.txt")
            sidecar = Path(d) / "result.removals"
            sidecar.write_text("previous\n", encoding="utf-8")
            proc = _run(
                ["--status", "changed", "--removals", "1. cut."],
                review_result_file=target,
                removals_file=str(sidecar),
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual(sidecar.read_text(encoding="utf-8"), "previous\n")


class ShellStaticChecksTest(unittest.TestCase):
    def test_bash_dash_n_is_silent_and_exits_zero(self):
        proc = subprocess.run(
            ["bash", "-n", str(SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")
        self.assertEqual(proc.stderr, "")

    def test_shellcheck_gcc_format_reports_zero_lines(self):
        proc = subprocess.run(
            ["shellcheck", "-f", "gcc", str(SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.stdout.splitlines(), [])


if __name__ == "__main__":
    unittest.main()
