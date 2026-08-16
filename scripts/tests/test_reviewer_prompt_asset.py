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

_CODEX_STUB = """#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--version" ]]; then
  echo "codex-stub 0.0.0"
  exit 0
fi
out=""
args=("$@")
for ((i=0;i<${#args[@]};i++)); do
  if [[ "${args[$i]}" == "--output-last-message" ]]; then
    out="${args[$((i+1))]}"
  fi
done
last=""
if (( ${#args[@]} > 0 )); then
  last="${args[$((${#args[@]}-1))]}"
fi
printf '%s' "$last" > "$CAPTURE_FILE"
if [[ -n "$out" ]]; then
  printf 'REVIEW_STATUS: NO-CHANGE\\n' > "$out"
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
cat >/dev/null
printf 'REVIEW_STATUS: NO-CHANGE\\n'
exit 0
"""

_POSIX_SED_STUB = """#!/usr/bin/env bash
exec /usr/bin/sed --posix "$@"
"""

PLACEHOLDER_TOKENS = (
    "SKILL_DIRECTORY",
    "CHECKLIST_PATH",
    "GUIDANCE_PATH",
    "OPEN_ITEMS_PATH",
    "VENV_PYTHON_PATH",
    "AUTHORITY_TASK",
    "AUTHORITY_RULE",
    "CHALLENGE_LINE",
)


def _make_stub_bin(tmpdir: Path, extra_stubs: dict[str, str] | None = None) -> Path:
    bindir = tmpdir / "bin"
    bindir.mkdir()
    stubs = {"codex": _CODEX_STUB, "claude": _CLAUDE_STUB}
    if extra_stubs:
        stubs.update(extra_stubs)
    for name, body in stubs.items():
        path = bindir / name
        path.write_text(body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return bindir


def _run_runner(
    extra_args: list[str],
    extra_stubs: dict[str, str] | None = None,
) -> tuple[subprocess.CompletedProcess, str]:
    for stale in LOGDIR.glob(f"{FIXTURE_SKILL}.*"):
        stale.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        bindir = _make_stub_bin(tmp_path, extra_stubs)
        capture_file = tmp_path / "codex.prompt"
        env = dict(os.environ)
        env["PATH"] = f"{bindir}{os.pathsep}{env.get('PATH', '')}"
        env["CAPTURE_FILE"] = str(capture_file)
        result = subprocess.run(
            [str(RUNNER), "--skill", FIXTURE_SKILL, "--no-install", *extra_args],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        capture = capture_file.read_text(encoding="utf-8") if capture_file.exists() else ""
        return result, capture


def _capture_dispatched_prompt(
    extra_args: list[str],
    extra_stubs: dict[str, str] | None = None,
) -> str:
    _result, capture = _run_runner(extra_args, extra_stubs)
    return capture


class ReviewerPromptAssetRenderTests(unittest.TestCase):
    def test_dual_mode_rendering_carries_no_marker_line(self):
        prompt = _capture_dispatched_prompt([])
        for line in prompt.splitlines():
            self.assertNotRegex(line, r"^<!-- parity:")

    def test_dual_mode_rendering_carries_no_unsubstituted_placeholder(self):
        prompt = _capture_dispatched_prompt([])
        for token in PLACEHOLDER_TOKENS:
            self.assertNotIn(token, prompt)


class ReviewerPromptMarkerStripPosixSedTests(unittest.TestCase):
    """The shipped marker-strip sed pattern must be portable POSIX BRE.

    GNU sed accepts `\\|` for alternation inside `\\( \\)` even outside
    --posix mode, which masks a BSD/macOS-sed-only defect in this
    container. `sed --posix` reproduces strict POSIX BRE semantics and is
    used here as the portability proxy.
    """

    def test_marker_lines_are_stripped_under_posix_sed(self):
        prompt = _capture_dispatched_prompt([], extra_stubs={"sed": _POSIX_SED_STUB})
        for line in prompt.splitlines():
            self.assertNotRegex(line, r"^<!-- parity:")



if __name__ == "__main__":
    unittest.main()
