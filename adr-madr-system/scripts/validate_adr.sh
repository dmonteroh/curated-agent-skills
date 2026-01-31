#!/usr/bin/env sh
set -eu

file="${1:-}"
if [ -z "$file" ] || [ ! -f "$file" ]; then
  echo "usage: $0 path/to/ADR-XXXX-something.md" >&2
  exit 2
fi

# Prefer rg if available (faster + better exit codes), fallback to grep.
have_rg=0
if command -v rg >/dev/null 2>&1; then
  have_rg=1
fi

require_heading() {
  heading="$1"
  if [ "$have_rg" -eq 1 ]; then
    rg -n --fixed-strings "$heading" "$file" >/dev/null 2>&1 || {
      echo "missing required section: $heading" >&2
      return 1
    }
  else
    grep -nF "$heading" "$file" >/dev/null 2>&1 || {
      echo "missing required section: $heading" >&2
      return 1
    }
  fi
}

require_heading "## Status"
require_heading "## Date"
require_heading "## Deciders"
require_heading "## Context"
require_heading "## Decision"
require_heading "## Rationale"
require_heading "## Consequences"

# Strongly recommended for quality; treat as required for this skill's standard template.
require_heading "## Decision Drivers"
require_heading "## Considered Options"

echo "OK: $file"
