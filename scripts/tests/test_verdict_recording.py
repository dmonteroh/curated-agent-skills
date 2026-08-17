from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "auditing" / "run_parallel_skill_reviews.sh"
LOGDIR = REPO_ROOT / "scripts" / "auditing" / "logs"

FIXTURE_SKILL = "testing"

_STUB_COMMON = """\
readproof="scripts/auditing/logs/${FIXTURE_SKILL}.readproof"
result_tool="scripts/auditing/review-result.sh"
expected=""
if [[ -f "$readproof" ]]; then
  expected="$(sed -n '2p' "$readproof")"
fi

reviewer_body() {
  case "${REVIEWER_MODE:-tool_ok}" in
    tool_ok)
      "$result_tool" --status no-change --read-proof "$expected" --differentiation strong --removals none
      printf 'Files changed: none\\n'
      printf 'DIFFERENTIATION: STRONG evidence\\n'
      printf 'REVIEW_STATUS: NO-CHANGE\\n'
      ;;
    tool_changed_prose_nochange)
      "$result_tool" --status changed --read-proof "$expected" --differentiation strong --removals none
      printf 'Files changed: none\\n'
      printf 'DIFFERENTIATION: STRONG evidence\\n'
      printf 'REVIEW_STATUS: NO-CHANGE\\n'
      ;;
    prose_only)
      printf 'Files changed: none\\n'
      printf 'DIFFERENTIATION: STRONG evidence\\n'
      printf 'REVIEW_STATUS: CHANGED\\n'
      ;;
    guard_recovers_status)
      "$result_tool" --status changed --read-proof "$expected" --differentiation strong --removals none
      cat scripts/auditing/test-fixtures/infra-guard-recovers-status-line.txt
      ;;
    guard_recovers_questions)
      "$result_tool" --status questions --read-proof "$expected"
      cat scripts/auditing/test-fixtures/infra-guard-recovers-questions.txt
      ;;
  esac
}

synthesis_body() {
  case "${SYNTH_MODE:-tool_changed}" in
    tool_changed)
      "$result_tool" --status changed --differentiation weak --removals "trim the intro"
      printf 'Files changed under skills/%s: trigger-cases updated\\n' "$FIXTURE_SKILL"
      printf 'DIFFERENTIATION: WEAK one line of evidence\\n'
      printf 'REVIEW_STATUS: CHANGED\\n'
      ;;
    prose_only)
      printf 'Files changed under skills/%s: trigger-cases updated\\n' "$FIXTURE_SKILL"
      printf 'DIFFERENTIATION: STRONG evidence\\n'
      printf 'REVIEW_STATUS: CHANGED\\n'
      ;;
    tool_questions_prose_quoted_nochange)
      "$result_tool" --status questions
      printf 'Synthesis for skills/%s: reviews conflict.\\n' "$FIXTURE_SKILL"
      printf '\\n'
      printf 'REVIEW_STATUS: NO-CHANGE\\n'
      printf '\\n'
      printf 'QUESTIONS\\n'
      printf '1. skills/%s/SKILL.md - unresolved conflict between reviews.\\n' "$FIXTURE_SKILL"
      ;;
    guard_recovers_status)
      "$result_tool" --status changed --differentiation weak --removals none
      printf 'ERROR: unexpected status 503 Service Unavailable: {"detail":"upstream saturated"}\\n'
      printf 'Files changed under skills/%s: trigger-cases updated\\n' "$FIXTURE_SKILL"
      printf 'REVIEW_STATUS: CHANGED\\n'
      ;;
    guard_recovers_questions)
      "$result_tool" --status questions
      printf 'stream error: unexpected status 429 Too Many Requests: {"detail":"rate limited"}; retrying 1/5 in 200ms\\xe2\\x80\\xa6\\n'
      printf 'Synthesis for skills/%s: reviews conflict.\\n' "$FIXTURE_SKILL"
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
  reviewer_body > "$out"
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
is_synthesis=0
for arg in "$@"; do
  if [[ "$arg" == "acceptEdits" ]]; then
    is_synthesis=1
  fi
done
if [[ "$is_synthesis" == "1" ]]; then
  synthesis_body
else
  reviewer_body
fi
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


def _run_dual(reviewer_mode: str, synth_mode: str = "tool_changed", skill: str = FIXTURE_SKILL) -> subprocess.CompletedProcess:
    for stale in LOGDIR.glob(f"{skill}.*"):
        stale.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        bindir = _make_stub_bin(Path(tmp))
        env = dict(os.environ)
        env["PATH"] = f"{bindir}{os.pathsep}{env.get('PATH', '')}"
        env["FIXTURE_SKILL"] = skill
        env["REVIEWER_MODE"] = reviewer_mode
        env["SYNTH_MODE"] = synth_mode
        return subprocess.run(
            [str(RUNNER), "--skill", skill, "--no-install"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )


def _run_single(reviewer_mode: str, skill: str = FIXTURE_SKILL) -> subprocess.CompletedProcess:
    for stale in LOGDIR.glob(f"{skill}.*"):
        stale.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        bindir = _make_stub_bin(Path(tmp))
        env = dict(os.environ)
        env["PATH"] = f"{bindir}{os.pathsep}{env.get('PATH', '')}"
        env["FIXTURE_SKILL"] = skill
        env["REVIEWER_MODE"] = reviewer_mode
        return subprocess.run(
            [str(RUNNER), "--single-model", "--skill", skill, "--no-install"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )


class ReviewerArmToolVerdictTests(unittest.TestCase):
    def test_tool_recorded_verdict_is_arm_ok(self):
        proc = _run_dual("tool_ok")
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/codex (NO-CHANGE)", proc.stdout)
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/claude (NO-CHANGE)", proc.stdout)

    def test_verdict_file_outcome_wins_over_contradicting_prose(self):
        proc = _run_dual("tool_changed_prose_nochange")
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/codex (CHANGED)", proc.stdout)
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/claude (CHANGED)", proc.stdout)
        self.assertNotIn(f"[arm-ok] {FIXTURE_SKILL}/codex (NO-CHANGE)", proc.stdout)
        self.assertNotIn(f"[arm-ok] {FIXTURE_SKILL}/claude (NO-CHANGE)", proc.stdout)

    def test_prose_only_arm_falls_back_to_classify_review_and_reports(self):
        proc = _run_dual("prose_only")
        self.assertIn(f"[arm-failed] {FIXTURE_SKILL}/codex (MALFORMED)", proc.stdout)
        self.assertIn(f"[arm-failed] {FIXTURE_SKILL}/claude (MALFORMED)", proc.stdout)
        self.assertNotIn("[infra-failure]", proc.stdout)
        self.assertNotIn("[malformed]", proc.stdout)


class SingleModelBatchVerdictTests(unittest.TestCase):
    def test_prose_only_batch_reports_malformed_not_parsed_verdict(self):
        proc = _run_single("prose_only")
        self.assertIn(f"[malformed] {FIXTURE_SKILL}\n", proc.stdout)
        self.assertNotIn(f"[ok] {FIXTURE_SKILL} (status", proc.stdout)
        self.assertNotIn("[infra-failure]", proc.stdout)
        verdict = LOGDIR / f"{FIXTURE_SKILL}.verdict"
        self.assertTrue(verdict.exists())
        self.assertIn("OUTCOME=MALFORMED", verdict.read_text(encoding="utf-8"))


class SynthesisToolVerdictTests(unittest.TestCase):
    def test_synthesis_tool_verdict_reported_ok(self):
        proc = _run_dual("tool_ok", synth_mode="tool_changed")
        self.assertIn(f"[ok] {FIXTURE_SKILL} (status CHANGED", proc.stdout)
        verdict = LOGDIR / f"{FIXTURE_SKILL}.synthesis.verdict"
        self.assertTrue(verdict.exists())
        self.assertIn("OUTCOME=CHANGED", verdict.read_text(encoding="utf-8"))

    def test_synthesis_tool_questions_wins_over_plain_line_quoted_no_change(self):
        proc = _run_dual("tool_ok", synth_mode="tool_questions_prose_quoted_nochange")
        self.assertIn(f"[failed] {FIXTURE_SKILL} (synthesis blocked: QUESTIONS", proc.stdout)
        self.assertNotIn(f"[ok] {FIXTURE_SKILL} (status NO-CHANGE", proc.stdout)
        verdict = LOGDIR / f"{FIXTURE_SKILL}.synthesis.verdict"
        self.assertTrue(verdict.exists())
        self.assertIn("OUTCOME=QUESTIONS", verdict.read_text(encoding="utf-8"))

    def test_prose_only_synthesis_reports_malformed_not_parsed_verdict(self):
        proc = _run_dual("tool_ok", synth_mode="prose_only")
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/codex (NO-CHANGE)", proc.stdout)
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/claude (NO-CHANGE)", proc.stdout)
        self.assertIn(f"[malformed] {FIXTURE_SKILL} (synthesis", proc.stdout)
        self.assertNotIn(f"[ok] {FIXTURE_SKILL} (status", proc.stdout)
        self.assertNotIn("[infra-failure]", proc.stdout)
        verdict = LOGDIR / f"{FIXTURE_SKILL}.synthesis.verdict"
        self.assertTrue(verdict.exists())
        self.assertIn("OUTCOME=MALFORMED", verdict.read_text(encoding="utf-8"))


class GuardBannerVerdictFileWinsTests(unittest.TestCase):
    def test_guard_recovers_status_line_verdict_file_wins_over_banner(self):
        proc = _run_dual("guard_recovers_status", synth_mode="guard_recovers_status")
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/codex (CHANGED)", proc.stdout)
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/claude (CHANGED)", proc.stdout)
        self.assertNotIn("(INFRA-FAILURE)", proc.stdout)
        self.assertNotIn("[arm-failed]", proc.stdout)
        self.assertIn(f"[ok] {FIXTURE_SKILL} (status CHANGED", proc.stdout)
        verdict = LOGDIR / f"{FIXTURE_SKILL}.synthesis.verdict"
        self.assertTrue(verdict.exists())
        self.assertIn("OUTCOME=CHANGED", verdict.read_text(encoding="utf-8"))

    def test_guard_recovers_questions_verdict_file_wins_over_banner(self):
        proc = _run_dual("guard_recovers_questions", synth_mode="guard_recovers_questions")
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/codex (QUESTIONS)", proc.stdout)
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/claude (QUESTIONS)", proc.stdout)
        self.assertNotIn("(INFRA-FAILURE)", proc.stdout)
        self.assertNotIn("[arm-failed]", proc.stdout)
        self.assertIn(f"[failed] {FIXTURE_SKILL} (synthesis blocked: QUESTIONS", proc.stdout)
        verdict = LOGDIR / f"{FIXTURE_SKILL}.synthesis.verdict"
        self.assertTrue(verdict.exists())
        self.assertIn("OUTCOME=QUESTIONS", verdict.read_text(encoding="utf-8"))


class StaleVerdictFileNeverReadTests(unittest.TestCase):
    def test_stale_verdict_file_is_removed_before_dispatch(self):
        for stale in LOGDIR.glob(f"{FIXTURE_SKILL}.*"):
            stale.unlink()
        LOGDIR.mkdir(parents=True, exist_ok=True)
        stale_verdict = LOGDIR / f"{FIXTURE_SKILL}.codex.verdict"
        stale_verdict.write_text("OUTCOME=CHANGED\nDIFFERENTIATION=STRONG\nREMOVAL_PROPOSALS=0\n", encoding="utf-8")
        proc = _run_dual("tool_ok")
        self.assertIn(f"[arm-ok] {FIXTURE_SKILL}/codex (NO-CHANGE)", proc.stdout)
        self.assertNotIn(f"[arm-ok] {FIXTURE_SKILL}/codex (CHANGED)", proc.stdout)


if __name__ == "__main__":
    unittest.main()
