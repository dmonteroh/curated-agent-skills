#!/usr/bin/env sh
set -eu

# Promote an intake draft (TD-YYYYMMDD-...) to a task brief.
#
# Usage:
#   ./tracks-conductor-protocol/scripts/tcd_promote_intake.sh docs/project/to-do/TD-20260130-something.md
#
# Optional env vars:
#   TCD_SEQ=S01
#   TCD_TRACK=<track-slug>

intake_path="${1:-}"
if [ -z "$intake_path" ] || [ ! -f "$intake_path" ]; then
  echo "usage: $0 path/to/TD-YYYYMMDD-*.md" >&2
  exit 2
fi

project_dir="${TCD_PROJECT_DIR:-docs/project}"
todo_dir="${TCD_TODO_DIR:-$project_dir/to-do}"

intake_base="$(basename "$intake_path")"
intake_id="${intake_base%.md}"

# Extract title from first H1.
title="$(awk 'NR==1{ sub(/^#[[:space:]]+/, "", $0); print; exit }' "$intake_path")"
if [ -z "$title" ]; then
  echo "could not find title in $intake_path" >&2
  exit 1
fi

# Mark intake status as Accepted (best-effort replace first status line).
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
awk '
  $0 == "## Status" {print; getline; print ""; getline; print "Accepted"; in_status=1; next}
  in_status==1 {in_status=0}
  {print}
' "$intake_path" >"$tmp" || true

# If the awk approach produced an empty file, don't clobber.
if [ -s "$tmp" ]; then
  mv "$tmp" "$intake_path"
fi

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

TCD_INTAKE="$intake_id" TCD_SEQ="${TCD_SEQ:-}" TCD_TRACK="${TCD_TRACK:-}" \
  "$script_dir/tcd_new_task.sh" "$title" >/dev/null

"$script_dir/tcd_update_index.sh" >/dev/null

echo "OK: promoted $intake_base to a task brief"
