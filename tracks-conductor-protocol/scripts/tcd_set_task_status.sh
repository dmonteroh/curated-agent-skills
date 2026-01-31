#!/usr/bin/env sh
set -eu

# Move a task id into a status section in docs/project/task_status.md.
#
# Usage:
#   ./tracks-conductor-protocol/scripts/tcd_set_task_status.sh S01-T-20260130-foo "In Progress"
#
# Notes:
# - Removes the task id from other sections to keep it unique.
# - Creates the target section if missing.

task_id="${1:-}"
new_status="${2:-}"

if [ -z "$task_id" ] || [ -z "$new_status" ]; then
  echo "usage: $0 <task-id> <status>" >&2
  exit 2
fi

project_dir="${TCD_PROJECT_DIR:-docs/project}"
task_status_file="${TCD_TASK_STATUS:-$project_dir/task_status.md}"

if [ ! -f "$task_status_file" ]; then
  echo "missing task status file: $task_status_file (run tcd.sh init?)" >&2
  exit 2
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

awk -v id="$task_id" -v target="$new_status" '
  BEGIN { in_target=0; wrote=0 }
  function is_header(line) { return line ~ /^##[[:space:]]+/ }
  function header_name(line) { sub(/^##[[:space:]]+/, "", line); return line }
  {
    # Drop existing mentions of the task id to keep uniqueness.
    if ($0 ~ id) {
      # If the entire line is just a bullet/link containing id, drop it.
      next
    }
  }
  is_header($0) {
    # On entering a new header, if we were in the target and have not inserted, insert now.
    if (in_target && !wrote) {
      print "- " id
      wrote=1
    }
    in_target = (header_name($0) == target)
    print
    next
  }
  {
    print
  }
  END {
    if (!wrote) {
      # Target section missing; append it at end.
      print ""
      print "## " target
      print ""
      print "- " id
    }
  }
' "$task_status_file" >"$tmp"

mv "$tmp" "$task_status_file"

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$script_dir/tcd_update_index.sh" >/dev/null

echo "OK: set $task_id -> $new_status"
