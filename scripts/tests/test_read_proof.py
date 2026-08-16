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
