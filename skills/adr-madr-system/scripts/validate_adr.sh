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

# $1 = display name, $2 = anchored ERE matching the accepted heading variants.
# Anchored so e.g. "## Decision Drivers" cannot satisfy the "## Decision" requirement.
require_heading() {
  name="$1"
  pattern="$2"
  if [ "$have_rg" -eq 1 ]; then
    rg -q "$pattern" "$file" 2>/dev/null || {
      echo "missing required section: $name" >&2
      return 1
    }
  else
    grep -Eq "$pattern" "$file" 2>/dev/null || {
      echo "missing required section: $name" >&2
      return 1
    }
  fi
}

# Alternatives cover the MADR-canonical spellings alongside this skill's template.
require_heading "## Status" '^## Status[[:space:]]*$'
require_heading "## Date" '^## Date[[:space:]]*$'
require_heading "## Deciders" '^## Deciders[[:space:]]*$'
require_heading "## Context" '^## Context( and Problem Statement)?[[:space:]]*$'
require_heading "## Decision" '^## Decision( Outcome)?[[:space:]]*$'
require_heading "## Rationale" '^(###? Rationale|## Decision Outcome)[[:space:]]*$'
require_heading "## Consequences" '^###? (Positive |Negative )?Consequences( Summary| and Mitigations)?[[:space:]]*$'

# Strongly recommended for quality; treat as required for this skill's standard template.
require_heading "## Decision Drivers" '^## Decision Drivers[[:space:]]*$'
require_heading "## Considered Options" '^## Considered Options[[:space:]]*$'

echo "OK: $file"
