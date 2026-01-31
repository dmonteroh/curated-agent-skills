#!/usr/bin/env sh
set -eu

# Create a new Future entry (file-per-entry) and update the work index.
#
# Usage:
#   ./tracks-conductor-protocol/scripts/tcd_new_future.sh "PII / Right to Erasure"
#
# Optional env vars:
#   TCD_FUT_ID=FUT-001
#   TCD_FUT_STATUS=Open

topic="${1:-}"
if [ -z "$topic" ]; then
  echo "usage: $0 \"topic\"" >&2
  exit 2
fi

project_dir="${TCD_PROJECT_DIR:-docs/project}"
futures_dir="${TCD_FUTURES_DIR:-$project_dir/futures}"

status="${TCD_FUT_STATUS:-Open}"

mkdir -p "$futures_dir"

slugify() {
  printf "%s" "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | tr ' _' '--' \
    | sed -E 's/[^a-z0-9-]+/-/g; s/-+/-/g; s/^-//; s/-$//'
}

next_id() {
  max=0
  for f in "$futures_dir"/FUT-[0-9][0-9][0-9]-*.md "$futures_dir"/FUT-[0-9][0-9][0-9].md; do
    [ -f "$f" ] || continue
    n="$(basename "$f" | sed -n 's/^FUT-\([0-9][0-9][0-9]\).*/\1/p')"
    [ -n "$n" ] || continue
    n10=$((10#$n))
    if [ "$n10" -gt "$max" ]; then max="$n10"; fi
  done
  printf "FUT-%03d" $((max + 1))
}

id="${TCD_FUT_ID:-$(next_id)}"
slug="$(slugify "$topic")"
file="$futures_dir/${id}-${slug}.md"

if [ -e "$file" ]; then
  echo "refusing to overwrite: $file" >&2
  exit 1
fi

{
  echo "# $topic"
  echo
  echo "## Status"
  echo
  echo "$status"
  echo
  echo "## Strategy"
  echo
  echo "<high-level pivot strategy>"
  echo
  echo "## Trigger"
  echo
  echo "<what milestone makes this current?>"
  echo
  echo "## Links"
  echo
  echo "- Tracks:"
  echo "  - docs/project/tracks/<slug>/"
  echo "- Tasks:"
  echo "  - docs/project/tasks/S##-T-YYYYMMDD-...md"
  echo "- ADRs (when triggered):"
  echo "  - docs/adr/ADR-XXXX-...md"
} >"$file"

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$script_dir/tcd_update_index.sh" >/dev/null

echo "OK: created $file"
