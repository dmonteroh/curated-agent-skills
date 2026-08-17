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


class BootstrapExemptionTests(unittest.TestCase):
    """Dispatched calls must not obey the repo's CLAUDE.md session-bootstrap:
    measured 2026-08-17, an arm ran status.sh, was silently denied under
    dontAsk, and burned the run to an empty MALFORMED result. The exemption
    rides in both prompt assets and, for claude calls, the system prompt."""

    def test_claude_calls_append_the_exemption_at_system_prompt_level(self):
        proc = _run(["--dry-run"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        for prefix in ("[dry-run] reviewer arm claude:", "[dry-run] synthesis:"):
            lines = [l for l in proc.stdout.splitlines() if l.startswith(prefix)]
            self.assertTrue(lines, proc.stdout)
            self.assertIn("--append-system-prompt", lines[0])
            self.assertIn("status.sh", lines[0])

    def test_every_dispatch_prompt_asset_opens_with_the_dispatch_context(self):
        for asset in ("reviewer-prompt.md", "synthesis-prompt.md", "apply-prompt.md"):
            text = (REPO_ROOT / "scripts" / "auditing" / asset).read_text(encoding="utf-8")
            self.assertIn("Dispatch context:", text, asset)
            self.assertIn(".agent/scripts/status.sh", text, asset)

    def test_bootstrap_carves_out_pipeline_dispatches(self):
        # CLAUDE.md/AGENTS.md are local files, but the dispatch exemption only
        # works while both sides agree: the bootstrap names the marker the
        # prompt assets open with.
        for name in ("CLAUDE.md", "AGENTS.md"):
            path = REPO_ROOT / name
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            self.assertIn('"Dispatch context:"', text, name)


class EffortFlagTests(unittest.TestCase):
    """--effort / --synthesis-effort render into the dispatched argvs; the
    dry-run plan prints those argvs verbatim, so it is the assertion surface."""

    @staticmethod
    def _lines(stdout, prefix):
        return [line for line in stdout.splitlines() if line.startswith(prefix)]

    def test_default_pins_medium_on_both_arms_and_standard_service_tier(self):
        proc = _run(["--dry-run"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        codex_lines = self._lines(proc.stdout, "[dry-run] reviewer arm codex:")
        claude_lines = self._lines(proc.stdout, "[dry-run] reviewer arm claude:")
        self.assertTrue(codex_lines and claude_lines, proc.stdout)
        self.assertIn("model_reasoning_effort=medium", codex_lines[0])
        self.assertIn("service_tier=default", codex_lines[0])
        self.assertIn("--effort medium", claude_lines[0])
        for line in self._lines(proc.stdout, "[dry-run] synthesis:"):
            self.assertNotIn("--effort", line)

    def test_effort_override_reaches_both_arms_but_not_synthesis(self):
        proc = _run(["--dry-run", "--effort", "xhigh"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        codex_lines = self._lines(proc.stdout, "[dry-run] reviewer arm codex:")
        claude_lines = self._lines(proc.stdout, "[dry-run] reviewer arm claude:")
        self.assertIn("model_reasoning_effort=xhigh", codex_lines[0])
        self.assertIn("--effort xhigh", claude_lines[0])
        for line in self._lines(proc.stdout, "[dry-run] synthesis:"):
            self.assertNotIn("--effort", line)

    def test_synthesis_effort_renders_only_on_the_synthesis_call(self):
        proc = _run(["--dry-run", "--synthesis-effort", "low"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        synth_lines = self._lines(proc.stdout, "[dry-run] synthesis:")
        self.assertTrue(synth_lines, proc.stdout)
        self.assertIn("--effort low", synth_lines[0])
        for line in self._lines(proc.stdout, "[dry-run] reviewer arm claude:"):
            self.assertIn("--effort medium", line)
            self.assertNotIn("--effort low", line)

    def test_invalid_effort_level_is_refused(self):
        for flag in ("--effort", "--synthesis-effort"):
            proc = _run(["--dry-run", flag, "turbo"])
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn("low, medium, high, xhigh, max", proc.stderr)
            self.assertIn(flag, proc.stderr)


if __name__ == "__main__":
    unittest.main()
