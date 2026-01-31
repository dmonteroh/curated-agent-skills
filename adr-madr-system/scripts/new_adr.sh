#!/usr/bin/env sh
set -eu

# Create a new ADR file (MADR) and update the index managed block.
#
# Usage:
#   ADR_DIR=docs/adr ADR_INDEX=docs/adr/README.md ./adr-madr-system/scripts/new_adr.sh "Use PostgreSQL for primary DB"
#
# Optional env vars:
#   ADR_DECIDERS="@alice @bob"
#   ADR_STATUS="Proposed"
#   ADR_SUPERSEDES="ADR-0002"

title="${1:-}"
if [ -z "$title" ]; then
  echo "usage: $0 \"ADR title\"" >&2
  exit 2
fi

adr_dir="${ADR_DIR:-docs/adr}"
index_file="${ADR_INDEX:-$adr_dir/README.md}"
status="${ADR_STATUS:-Proposed}"
deciders="${ADR_DECIDERS:-}"
supersedes="${ADR_SUPERSEDES:-}"

mkdir -p "$adr_dir"

today="$(date +%F)"

next_num() {
  # Find max ADR number in dir, then +1. Supports ADR-0001-*.md or ADR-0001.md.
  max=0
  for f in "$adr_dir"/ADR-[0-9][0-9][0-9][0-9]-*.md "$adr_dir"/ADR-[0-9][0-9][0-9][0-9].md; do
    [ -f "$f" ] || continue
    n="$(printf "%s" "$f" | sed -n 's/.*ADR-\\([0-9][0-9][0-9][0-9]\\).*/\\1/p' | head -n1)"
    [ -n "$n" ] || continue
    # strip leading zeros safely
    n10=$((10#$n))
    if [ "$n10" -gt "$max" ]; then max="$n10"; fi
  done
  printf "%04d" $((max + 1))
}

slugify() {
  # Lowercase, keep alnum and dashes, collapse whitespace/underscores to dashes.
  printf "%s" "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | tr ' _' '--' \
    | sed -E 's/[^a-z0-9-]+/-/g; s/-+/-/g; s/^-//; s/-$//'
}

num="$(next_num)"
id="ADR-$num"
slug="$(slugify "$title")"
file="$adr_dir/${id}-${slug}.md"

if [ -e "$file" ]; then
  echo "refusing to overwrite existing file: $file" >&2
  exit 1
fi

{
  echo "# $id: $title"
  echo
  echo "## Status"
  echo
  echo "$status"
  echo
  echo "## Date"
  echo
  echo "$today"
  echo
  echo "## Deciders"
  echo
  if [ -n "$deciders" ]; then
    for d in $deciders; do
      echo "- $d"
    done
  else
    echo "- <fill>"
  fi
  echo
  echo "## Context"
  echo
  echo "<why now, what problem, constraints>"
  echo
  echo "## Decision Drivers"
  echo
  echo "1. <driver>"
  echo "2. <driver>"
  echo
  echo "## Considered Options"
  echo
  echo "### Option A: <name>"
  echo
  echo "- Pros:"
  echo "  - <...>"
  echo "- Cons:"
  echo "  - <...>"
  echo
  echo "### Option B: <name>"
  echo
  echo "- Pros:"
  echo "  - <...>"
  echo "- Cons:"
  echo "  - <...>"
  echo
  echo "## Decision"
  echo
  echo "We will <decision>."
  echo
  echo "## Rationale"
  echo
  echo "<tie back to decision drivers>"
  echo
  if [ -n "$supersedes" ]; then
    echo "## Supersedes"
    echo
    echo "- $supersedes"
    echo
  fi
  echo "## Consequences"
  echo
  echo "- Positive:"
  echo "  - <...>"
  echo "- Negative:"
  echo "  - <...>"
  echo "- Risks:"
  echo "  - <...>"
  echo "- Mitigations:"
  echo "  - <...>"
  echo
  echo "## Follow-ups"
  echo
  echo "- [ ] <...>"
  echo
  echo "## Links"
  echo
  echo "- Spec/track/task: <path or URL>"
  echo "- Related ADRs:"
  echo "  - <ADR-XXXX>: <title>"
} >"$file"

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$script_dir/validate_adr.sh" "$file" >/dev/null

ADR_DIR="$adr_dir" ADR_INDEX="$index_file" "$script_dir/update_index.sh" >/dev/null

echo "OK: created $file"
