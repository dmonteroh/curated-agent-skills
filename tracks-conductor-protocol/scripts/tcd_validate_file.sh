#!/usr/bin/env sh
set -eu

# Validate required sections for protocol artifacts (intake/task/track/future).
#
# Usage:
#   ./tracks-conductor-protocol/scripts/tcd_validate_file.sh <kind> path/to/file
#
# Kinds:
#   intake  - TD-YYYYMMDD-*.md
#   task    - S##-T-YYYYMMDD-*.md
#   track-spec, track-plan, track-context
#   future  - FUT-XXX-*.md

kind="${1:-}"
file="${2:-}"

if [ -z "$kind" ] || [ -z "$file" ] || [ ! -f "$file" ]; then
  echo "usage: $0 <kind> <file>" >&2
  exit 2
fi

have_rg=0
if command -v rg >/dev/null 2>&1; then
  have_rg=1
fi

require_heading() {
  heading="$1"
  if [ "$have_rg" -eq 1 ]; then
    rg -n --fixed-strings "$heading" "$file" >/dev/null 2>&1 || {
      echo "missing required section: $heading ($file)" >&2
      return 1
    }
  else
    grep -nF -- "$heading" "$file" >/dev/null 2>&1 || {
      echo "missing required section: $heading ($file)" >&2
      return 1
    }
  fi
}

case "$kind" in
  intake)
    require_heading "## Status"
    require_heading "## Problem Statement"
    require_heading "## Intent"
    require_heading "## Scope"
    require_heading "## Evidence"
    require_heading "## Dependencies"
    require_heading "## Success Signal"
    require_heading "## Links"
    ;;
  task)
    require_heading "## Intent"
    require_heading "## Scope"
    require_heading "## Dependencies"
    require_heading "## Acceptance Criteria"
    require_heading "## Links"
    ;;
  track-spec)
    require_heading "## Status"
    require_heading "## Problem / Context"
    require_heading "## Goals"
    require_heading "## Non-goals"
    require_heading "## Requirements"
    require_heading "## Acceptance Criteria"
    require_heading "## Dependencies"
    require_heading "## Links"
    ;;
  track-plan)
    require_heading "## Phases"
    require_heading "## Checkpoints"
    ;;
  track-context)
    require_heading "## What this track changes"
    require_heading "## Assumptions"
    require_heading "## Open questions"
    require_heading "## Links"
    ;;
  future)
    require_heading "## Status"
    require_heading "## Strategy"
    require_heading "## Trigger"
    require_heading "## Links"
    ;;
  *)
    echo "unknown kind: $kind" >&2
    exit 2
    ;;
esac

echo "OK: $kind $file"

