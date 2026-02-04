#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

usage() {
  cat <<USAGE
Usage: scripts/audit-skills.sh [--no-token-checks]

Creates .venv (if missing), installs audit dependencies, and runs the audit.

Environment:
  PYTHON_BIN   Python interpreter to use (default: python3)
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "error: $PYTHON_BIN not found" >&2
  exit 1
fi

if [[ ! -d "$VENV" ]]; then
  "$PYTHON_BIN" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install -r "$ROOT/scripts/requirements-audit.txt" >/dev/null

"$VENV/bin/python" "$ROOT/scripts/audit_skills.py" "$@"
