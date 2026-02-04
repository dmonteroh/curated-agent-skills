#!/usr/bin/env sh
set -eu

# Set task status in task frontmatter and update the Work Index.
#
# Usage:
#   ./tracks-conductor-protocol/scripts/tcd_set_task_status.sh S01-T-20260130-foo "In Progress"

task_id="${1:-}"
new_status="${2:-}"

if [ -z "$task_id" ] || [ -z "$new_status" ]; then
  echo "usage: $0 <task-id> <status>" >&2
  exit 2
fi

case "$new_status" in
  Draft|Approved|In\ Progress|Review|Blocked|Done|Partially\ Done) ;;
  *)
    echo "invalid status: $new_status (allowed: Draft, Approved, In Progress, Review, Blocked, Done, Partially Done)" >&2
    exit 2
    ;;
esac

project_dir="${TCD_PROJECT_DIR:-docs/project}"
tasks_dir="${TCD_TASKS_DIR:-$project_dir/tasks}"

if [ ! -d "$tasks_dir" ]; then
  echo "missing tasks directory: $tasks_dir (run tcd.sh init?)" >&2
  exit 2
fi

task_file=""
matches=0
if [ -f "$tasks_dir/$task_id.md" ]; then
  task_file="$tasks_dir/$task_id.md"
  matches=1
else
  for f in "$tasks_dir/$task_id"*.md; do
    [ -f "$f" ] || continue
    task_file="$f"
    matches=$((matches + 1))
  done
fi

if [ "$matches" -eq 0 ]; then
  echo "task not found: $task_id (searched $tasks_dir)" >&2
  exit 2
fi
if [ "$matches" -gt 1 ]; then
  echo "multiple tasks match $task_id; be more specific" >&2
  exit 2
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

first_line="$(head -n 1 "$task_file" || true)"
if [ "$first_line" = "---" ]; then
  awk -v status="$new_status" '
    BEGIN { in_fm=0; done=0 }
    NR==1 && $0=="---" { in_fm=1; print; next }
    in_fm && $0=="---" {
      if (!done) { print "status: " status; done=1 }
      in_fm=0
      print
      next
    }
    in_fm && $0 ~ /^status:[[:space:]]*/ {
      print "status: " status
      done=1
      next
    }
    { print }
  ' "$task_file" >"$tmp"
else
  {
    echo "---"
    echo "status: $new_status"
    echo "---"
    echo
    cat "$task_file"
  } >"$tmp"
fi

mv "$tmp" "$task_file"

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$script_dir/tcd_update_index.sh" >/dev/null

echo "OK: set $task_id -> $new_status"
