from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "auditing" / "run_parallel_skill_reviews.sh"
LOGDIR = REPO_ROOT / "scripts" / "auditing" / "logs"
SKILLS_LIST = REPO_ROOT / "scripts" / "auditing" / "skills_list.txt"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "auditing"))
from review_log import classify  # noqa: E402

FIXTURE_SKILL = "testing"

_STUB_COMMON = """\
mode="${FIXTURE_MODE:-match}"
skill="${FIXTURE_SKILL:?FIXTURE_SKILL not set}"
readproof="scripts/auditing/logs/${skill}.readproof"
expected=""
if [[ -f "$readproof" ]]; then
  expected="$(sed -n '2p' "$readproof")"
fi
build_message() {
  case "$mode" in
    match)
      printf 'READ_PROOF: %s\\n' "$expected"
      printf 'Files changed: none\\n'
      printf 'Summary: no changes (0 removed, 0 added)\\n'
      printf 'REMOVAL PROPOSALS: none\\n'
      printf 'DIFFERENTIATION: STRONG one line of evidence\\n'
      printf 'REVIEW_STATUS: NO-CHANGE\\n'
      ;;
    backtick_interior_whitespace)
      printf 'READ_PROOF: `   %s`\\n' "$expected"
      printf 'Files changed: none\\n'
      printf 'Summary: no changes (0 removed, 0 added)\\n'
      printf 'REMOVAL PROPOSALS: none\\n'
      printf 'DIFFERENTIATION: STRONG one line of evidence\\n'
      printf 'REVIEW_STATUS: NO-CHANGE\\n'
      ;;
    absent)
      printf 'Files changed: none\\n'
      printf 'Summary: no changes (0 removed, 0 added)\\n'
      printf 'REMOVAL PROPOSALS: none\\n'
      printf 'DIFFERENTIATION: STRONG one line of evidence\\n'
      printf 'REVIEW_STATUS: NO-CHANGE\\n'
      ;;
    mismatch)
      printf 'READ_PROOF: this text does not match the challenge line at all\\n'
      printf 'Files changed: none\\n'
      printf 'Summary: no changes (0 removed, 0 added)\\n'
      printf 'REMOVAL PROPOSALS: none\\n'
      printf 'DIFFERENTIATION: STRONG one line of evidence\\n'
      printf 'REVIEW_STATUS: NO-CHANGE\\n'
      ;;
    questions_no_proof)
      printf 'QUESTIONS\\n'
      ;;
    infra_failure_no_proof)
      printf 'ERROR: unexpected status 500 Internal Server Error\\n'
      ;;
  esac
}
"""

_CODEX_STUB = """#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--version" ]]; then
  echo "codex-stub 0.0.0"
  exit 0
fi
source "$(dirname "$0")/_fixture_common.sh"
out=""
args=("$@")
for ((i=0;i<${#args[@]};i++)); do
  if [[ "${args[$i]}" == "--output-last-message" ]]; then
    out="${args[$((i+1))]}"
  fi
done
if [[ -n "$out" ]]; then
  build_message > "$out"
fi
if [[ "$mode" == "infra_failure_no_proof" ]]; then
  build_message
fi
echo "codex-stub-banner"
exit 0
"""

_CLAUDE_STUB = """#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--version" ]]; then
  echo "claude-stub 0.0.0"
  exit 0
fi
source "$(dirname "$0")/_fixture_common.sh"
cat >/dev/null
build_message
exit 0
"""


def _make_stub_bin(tmpdir: Path) -> Path:
    bindir = tmpdir / "bin"
    bindir.mkdir()
    (bindir / "_fixture_common.sh").write_text(_STUB_COMMON, encoding="utf-8")
    for name, body in (("codex", _CODEX_STUB), ("claude", _CLAUDE_STUB)):
        path = bindir / name
        path.write_text(body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return bindir


def _run_dual(mode: str, skill: str = FIXTURE_SKILL) -> subprocess.CompletedProcess:
    for stale in LOGDIR.glob(f"{skill}.*"):
        stale.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        bindir = _make_stub_bin(Path(tmp))
        env = dict(os.environ)
        env["PATH"] = f"{bindir}{os.pathsep}{env.get('PATH', '')}"
        env["FIXTURE_MODE"] = mode
        env["FIXTURE_SKILL"] = skill
        return subprocess.run(
            [str(RUNNER), "--skill", skill, "--no-install"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )


def _run_single(mode: str, skill: str = FIXTURE_SKILL) -> subprocess.CompletedProcess:
    for stale in LOGDIR.glob(f"{skill}.*"):
        stale.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        bindir = _make_stub_bin(Path(tmp))
        env = dict(os.environ)
        env["PATH"] = f"{bindir}{os.pathsep}{env.get('PATH', '')}"
        env["FIXTURE_MODE"] = mode
        env["FIXTURE_SKILL"] = skill
        return subprocess.run(
            [str(RUNNER), "--single-model", "--skill", skill, "--no-install"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )


BACKTICK_FIXTURE_SKILL = "__test_backtick_challenge_line__"
BACKTICK_LINE = "`scripts/auditing/references/authoring-guidance.md`"


class BacktickWrappedChallengeLineTests(unittest.TestCase):
    def setUp(self):
        skills_list_snapshot = SKILLS_LIST.read_bytes()
        self.addCleanup(SKILLS_LIST.write_bytes, skills_list_snapshot)
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        fixture_dir = Path(self.tmpdir.name) / "skill"
        fixture_dir.mkdir()
        content = (
            "---\n"
            "name: placeholder\n"
            "---\n"
            "short\n"
            f"{BACKTICK_LINE}\n"
            "short\n"
        )
        (fixture_dir / "SKILL.md").write_text(content, encoding="utf-8")
        self.skill_link = REPO_ROOT / "skills" / BACKTICK_FIXTURE_SKILL
        if self.skill_link.is_symlink() or self.skill_link.exists():
            self.skill_link.unlink()
        os.symlink(fixture_dir, self.skill_link, target_is_directory=True)
        self.addCleanup(self._remove_link_and_logs)

    def _remove_link_and_logs(self):
        if self.skill_link.is_symlink() or self.skill_link.exists():
            self.skill_link.unlink()
        for stale in LOGDIR.glob(f"{BACKTICK_FIXTURE_SKILL}.*"):
            stale.unlink()

    def test_wholly_backtick_wrapped_challenge_line_reproduced_verbatim_is_arm_ok(self):
        proc = _run_dual("match", skill=BACKTICK_FIXTURE_SKILL)
        self.assertIn(f"[arm-ok] {BACKTICK_FIXTURE_SKILL}/codex", proc.stdout)
        self.assertIn(f"[arm-ok] {BACKTICK_FIXTURE_SKILL}/claude", proc.stdout)
        self.assertNotIn("read-proof mismatch", proc.stdout)
        self.assertNotIn("read-proof absent", proc.stdout)


REGEN_FIXTURE_SKILL = "__test_skills_list_not_regenerated__"


class SkillsListNotRegeneratedTests(unittest.TestCase):
    def setUp(self):
        skills_list_snapshot = SKILLS_LIST.read_bytes()
        self.addCleanup(SKILLS_LIST.write_bytes, skills_list_snapshot)
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        fixture_dir = Path(self.tmpdir.name) / "skill"
        fixture_dir.mkdir()
        (fixture_dir / "SKILL.md").write_text(
            "---\nname: placeholder\n---\nshort\n", encoding="utf-8"
        )
        self.skill_link = REPO_ROOT / "skills" / REGEN_FIXTURE_SKILL
        if self.skill_link.is_symlink() or self.skill_link.exists():
            self.skill_link.unlink()
        os.symlink(fixture_dir, self.skill_link, target_is_directory=True)
        self.addCleanup(self._remove_link)
        self.snapshot = skills_list_snapshot

    def _remove_link(self):
        if self.skill_link.is_symlink() or self.skill_link.exists():
            self.skill_link.unlink()

    def _assert_unchanged(self, proc):
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(SKILLS_LIST.read_bytes(), self.snapshot)

    def test_default_full_list_dry_run_does_not_regenerate(self):
        proc = subprocess.run(
            [str(RUNNER), "--dry-run", "--no-install"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self._assert_unchanged(proc)

    def test_skill_flag_dry_run_does_not_regenerate(self):
        proc = subprocess.run(
            [str(RUNNER), "--skill", REGEN_FIXTURE_SKILL, "--dry-run", "--no-install"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self._assert_unchanged(proc)

    def test_skills_file_flag_dry_run_does_not_regenerate(self):
        override = Path(self.tmpdir.name) / "skills_override.txt"
        override.write_text(f"{REGEN_FIXTURE_SKILL}\n", encoding="utf-8")
        proc = subprocess.run(
            [str(RUNNER), "--skills-file", str(override), "--dry-run", "--no-install"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self._assert_unchanged(proc)


class SingleModeInfraFailureOrderingTests(unittest.TestCase):
    def test_infra_failure_is_classified_before_read_proof_check(self):
        proc = _run_single("infra_failure_no_proof")
        self.assertIn(f"[infra-failure] {FIXTURE_SKILL}", proc.stdout)
        self.assertIn("unexpected status 500 Internal Server Error", proc.stdout)
        self.assertNotIn(f"[failed] {FIXTURE_SKILL} (read-proof absent)", proc.stdout)
        self.assertNotIn("read-proof absent", proc.stdout)
        self.assertNotIn("read-proof mismatch", proc.stdout)


class ReadProofArmOutcomeTests(unittest.TestCase):
    def test_matching_proof_is_arm_ok(self):
        proc = _run_dual("match")
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/codex", proc.stdout)
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/claude", proc.stdout)
        self.assertNotIn("read-proof absent", proc.stdout)
        self.assertNotIn("read-proof mismatch", proc.stdout)

    def test_absent_proof_is_arm_failed(self):
        proc = _run_dual("absent")
        self.assertIn(f"[arm-failed] {FIXTURE_SKILL}/codex (read-proof absent)", proc.stdout)
        self.assertIn(f"[arm-failed] {FIXTURE_SKILL}/claude (read-proof absent)", proc.stdout)
        self.assertNotIn(f"[arm-ok] {FIXTURE_SKILL}/codex", proc.stdout)
        self.assertNotIn(f"[arm-ok] {FIXTURE_SKILL}/claude", proc.stdout)

    def test_wrong_text_proof_is_arm_failed_mismatch(self):
        proc = _run_dual("mismatch")
        self.assertIn(f"[arm-failed] {FIXTURE_SKILL}/codex (read-proof mismatch)", proc.stdout)
        self.assertIn(f"[arm-failed] {FIXTURE_SKILL}/claude (read-proof mismatch)", proc.stdout)
        self.assertNotIn(f"[arm-ok] {FIXTURE_SKILL}/codex", proc.stdout)
        self.assertNotIn(f"[arm-ok] {FIXTURE_SKILL}/claude", proc.stdout)

    def test_bare_questions_with_no_proof_is_arm_failed_never_arm_ok(self):
        proc = _run_dual("questions_no_proof")
        self.assertIn(f"[arm-failed] {FIXTURE_SKILL}/codex (read-proof absent)", proc.stdout)
        self.assertIn(f"[arm-failed] {FIXTURE_SKILL}/claude (read-proof absent)", proc.stdout)
        self.assertNotIn(f"[arm-ok] {FIXTURE_SKILL}/codex", proc.stdout)
        self.assertNotIn(f"[arm-ok] {FIXTURE_SKILL}/claude", proc.stdout)

    def test_backtick_wrapped_value_with_interior_whitespace_is_arm_ok(self):
        proc = _run_dual("backtick_interior_whitespace")
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/codex", proc.stdout)
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/claude", proc.stdout)
        self.assertNotIn("read-proof absent", proc.stdout)
        self.assertNotIn("read-proof mismatch", proc.stdout)

    def test_a_skill_with_a_failed_arm_never_reaches_synthesis(self):
        proc = _run_dual("absent")
        self.assertNotIn(f"[queued] {FIXTURE_SKILL}/synthesis", proc.stdout)
        self.assertIn(f"[blocked] {FIXTURE_SKILL}", proc.stdout)


class ReadProofDoesNotAffectClassifyTest(unittest.TestCase):
    def test_classify_is_identical_with_and_without_leading_read_proof_line(self):
        without = (
            "Files changed: none\n"
            "Summary: no changes\n"
            "REMOVAL PROPOSALS: none\n"
            "DIFFERENTIATION: STRONG evidence\n"
            "REVIEW_STATUS: NO-CHANGE\n"
        )
        with_proof = "READ_PROOF: some challenge line text\n" + without
        self.assertEqual(classify(without), classify(with_proof))


if __name__ == "__main__":
    unittest.main()
