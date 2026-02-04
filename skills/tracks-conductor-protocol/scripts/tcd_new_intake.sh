#!/usr/bin/env sh
set -eu

# Create a new intake draft (to-do) and update the work index.
#
# Usage:
#   TCD_OWNER="@you" ./tracks-conductor-protocol/scripts/tcd_new_intake.sh "Short title"

title="${1:-}"
if [ -z "$title" ]; then
  echo "usage: $0 \"title\"" >&2
  exit 2
fi

project_dir="${TCD_PROJECT_DIR:-docs/project}"
todo_dir="${TCD_TODO_DIR:-$project_dir/to-do}"

owner="${TCD_OWNER:-}"
status="${TCD_TODO_STATUS:-Draft}"

mkdir -p "$todo_dir"

today="$(date +%Y%m%d)"

slugify() {
  printf "%s" "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | tr ' _' '--' \
    | sed -E 's/[^a-z0-9-]+/-/g; s/-+/-/g; s/^-//; s/-$//'
}

slug="$(slugify "$title")"
file="$todo_dir/TD-$today-$slug.md"

if [ -e "$file" ]; then
  echo "refusing to overwrite: $file" >&2
  exit 1
fi

{
  echo "# $title"
  echo
  echo "## Status"
  echo
  echo "$status"
  echo
  echo "## Problem Statement"
  echo
  echo "<2-4 sentences: user truth + business invariant at risk>"
  echo
  echo "## Intent"
  echo
  echo "<1-2 sentences: desired outcome (no solutioning)>"
  echo
  echo "## Scope"
  echo
  echo "In scope:"
  echo "- ..."
  echo
  echo "Out of scope:"
  echo "- ..."
  echo
  echo "## Evidence"
  echo
  echo "- <link>"
  echo
  echo "## Dependencies"
  echo
  echo "- ADRs:"
  echo "  - ADR-XXXX: ..."
  echo "- Tasks:"
  echo "  - S##-T-YYYYMMDD-...: ..."
  echo "- Futures:"
  echo "  - FUT-XXX: ..."
  echo
  echo "## Risks/Notes"
  echo
  echo "- <only if invariants, security, compliance, or long-term constraints>"
  echo
  echo "## Success Signal"
  echo
  echo "- <one measurable signal>"
  echo
  echo "## Links"
  echo
  if [ -n "$owner" ]; then
    echo "- Owner: $owner"
  fi
  echo "- Context (CDD):"
  echo "  - docs/context/product.md"
  echo "  - docs/context/tech-stack.md"
  echo "  - docs/context/workflow.md"
} >"$file"

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$script_dir/tcd_update_index.sh" >/dev/null

echo "OK: created $file"

