from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = Path(__file__).resolve().parent
RUNNER = REPO_ROOT / "scripts" / "auditing" / "run_parallel_skill_reviews.sh"
LOGDIR = REPO_ROOT / "scripts" / "auditing" / "logs"

sys.path.insert(0, str(TESTS_DIR))
from test_read_proof import FIXTURE_SKILL, _make_stub_bin  # noqa: E402

# Runs the real runner with extra_args ahead of --skill/--no-install,
# against a stub bin that always writes both a codex and a claude
# executable: an --arms selection that still shells out to the unselected
# client is caught here rather than falling through to a real one.
def _run(extra_args, mode: str = "match", skill: str = FIXTURE_SKILL) -> subprocess.CompletedProcess:
    for stale in LOGDIR.glob(f"{skill}.*"):
        stale.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        bindir = _make_stub_bin(Path(tmp))
        env = dict(os.environ)
        env["PATH"] = f"{bindir}{os.pathsep}{env.get('PATH', '')}"
        env["FIXTURE_MODE"] = mode
        env["FIXTURE_SKILL"] = skill
        return subprocess.run(
            [str(RUNNER), *extra_args, "--skill", skill, "--no-install"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )


class OneArmDispatchTests(unittest.TestCase):
    def test_arms_claude_dispatches_one_reviewer_arm_and_reaches_a_result(self):
        proc = _run(["--arms", "claude"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("reviewer arms: claude (count 1)", proc.stdout)
        self.assertIn(f"[queued] {FIXTURE_SKILL}/claude", proc.stdout)
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/claude (NO-CHANGE)", proc.stdout)
        self.assertIn(f"[queued] {FIXTURE_SKILL}/synthesis", proc.stdout)
        self.assertIn(f"[ok] {FIXTURE_SKILL} (status NO-CHANGE", proc.stdout)
        self.assertNotIn("codex", proc.stdout)


class ArmsValidationRefusalTests(unittest.TestCase):
    def test_unknown_arm_name_is_refused(self):
        proc = _run(["--arms", "cursor"])
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("codex", proc.stderr)
        self.assertIn("claude", proc.stderr)

    def test_duplicate_arm_name_is_refused(self):
        proc = _run(["--arms", "codex,codex"])
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("codex", proc.stderr)
        self.assertIn("claude", proc.stderr)


class InfraFailureOrderingTests(unittest.TestCase):
    # reap_phase_one classifies a non-empty final message with no verdict
    # file before any read-proof check; on INFRA-FAILURE it records the
    # outcome and never calls verify_read_proof on that branch at all.
    def test_infra_failure_is_classified_before_read_proof_check(self):
        proc = _run([], mode="infra_failure_no_proof")
        self.assertIn(f"[arm-failed] {FIXTURE_SKILL}/codex (INFRA-FAILURE)", proc.stdout)
        self.assertIn(f"[arm-failed] {FIXTURE_SKILL}/claude (INFRA-FAILURE)", proc.stdout)
        self.assertIn(f"[blocked] {FIXTURE_SKILL} (arm failure: arm codex: INFRA-FAILURE)", proc.stdout)
        self.assertNotIn("read-proof absent", proc.stdout)
        self.assertNotIn("read-proof mismatch", proc.stdout)


if __name__ == "__main__":
    unittest.main()
