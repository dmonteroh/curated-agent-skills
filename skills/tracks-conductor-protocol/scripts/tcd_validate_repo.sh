#!/usr/bin/env sh
set -eu

# Validate repo work-management artifacts for Tracks Conductor Protocol.
# This is intentionally lightweight: it checks structure + index coverage.

project_dir="${TCD_PROJECT_DIR:-docs/project}"
todo_dir="${TCD_TODO_DIR:-$project_dir/to-do}"
tasks_dir="${TCD_TASKS_DIR:-$project_dir/tasks}"
tracks_dir="${TCD_TRACKS_DIR:-$project_dir/tracks}"
futures_dir="${TCD_FUTURES_DIR:-$project_dir/futures}"

work_index="${TCD_WORK_INDEX:-$project_dir/work_index.md}"

require_file() {
  [ -f "$1" ] || { echo "missing required file: $1" >&2; exit 1; }
}

require_dir() {
  [ -d "$1" ] || { echo "missing required dir: $1" >&2; exit 1; }
}

require_dir "$project_dir"
require_dir "$todo_dir"
require_dir "$tasks_dir"
require_dir "$tracks_dir"
require_dir "$futures_dir"
require_file "$work_index"

for marker in \
  "<!-- TCD:INTAKE:START -->" "<!-- TCD:INTAKE:END -->" \
  "<!-- TCD:TASKS:START -->" "<!-- TCD:TASKS:END -->" \
  "<!-- TCD:TRACKS:START -->" "<!-- TCD:TRACKS:END -->" \
  "<!-- TCD:FUTURES:START -->" "<!-- TCD:FUTURES:END -->"
do
  grep -qF "$marker" "$work_index" || { echo "missing marker in $work_index: $marker" >&2; exit 1; }
done

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

# Coverage checks: every artifact id should appear at least once in the index.
missing=0

for f in "$todo_dir"/TD-*.md; do
  [ -f "$f" ] || continue
  id="$(basename "$f" .md)"
  grep -qF "$id" "$work_index" || { echo "index missing intake: $id" >&2; missing=1; }
  "$script_dir/tcd_validate_file.sh" intake "$f" >/dev/null || missing=1
done

for f in "$tasks_dir"/S[0-9][0-9]-T-*.md; do
  [ -f "$f" ] || continue
  id="$(basename "$f" .md)"
  grep -qF "$id" "$work_index" || { echo "index missing task: $id" >&2; missing=1; }
  "$script_dir/tcd_validate_file.sh" task "$f" >/dev/null || missing=1
done

for d in "$tracks_dir"/*; do
  [ -d "$d" ] || continue
  slug="$(basename "$d")"
  grep -qF "| $slug |" "$work_index" || { echo "index missing track: $slug" >&2; missing=1; }
  [ -f "$d/spec.md" ] || { echo "track missing spec.md: $d" >&2; missing=1; }
  [ -f "$d/plan.md" ] || { echo "track missing plan.md: $d" >&2; missing=1; }
  [ -f "$d/context.md" ] || { echo "track missing context.md: $d" >&2; missing=1; }
  [ -f "$d/spec.md" ] && "$script_dir/tcd_validate_file.sh" track-spec "$d/spec.md" >/dev/null || missing=1
  [ -f "$d/plan.md" ] && "$script_dir/tcd_validate_file.sh" track-plan "$d/plan.md" >/dev/null || missing=1
  [ -f "$d/context.md" ] && "$script_dir/tcd_validate_file.sh" track-context "$d/context.md" >/dev/null || missing=1
done

for f in "$futures_dir"/FUT-*.md; do
  [ -f "$f" ] || continue
  id="$(basename "$f" .md | sed -n 's/\(FUT-[0-9][0-9][0-9]\).*/\1/p')"
  [ -n "$id" ] || continue
  grep -qF "$id" "$work_index" || { echo "index missing future: $id ($f)" >&2; missing=1; }
  "$script_dir/tcd_validate_file.sh" future "$f" >/dev/null || missing=1
done

if [ "$missing" -ne 0 ]; then
  echo "FAILED: validation issues found" >&2
  exit 1
fi

echo "OK: Tracks Conductor repo validation passed"
