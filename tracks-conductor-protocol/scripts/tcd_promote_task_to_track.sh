#!/usr/bin/env sh
set -eu

# Link a task brief into a track plan (and optionally ensure track exists).
#
# Usage:
#   ./tracks-conductor-protocol/scripts/tcd_promote_task_to_track.sh path/to/S01-T-....md <track-slug> [phase]
#
# Behavior:
# - Adds/updates the "Track:" line in the task brief Dependencies section.
# - Inserts a task link into the track's plan under the given phase (default: Phase 1).

task_path="${1:-}"
track_slug="${2:-}"
phase="${3:-Phase 1}"

if [ -z "$task_path" ] || [ -z "$track_slug" ] || [ ! -f "$task_path" ]; then
  echo "usage: $0 path/to/S##-T-YYYYMMDD-*.md <track-slug> [phase]" >&2
  exit 2
fi

project_dir="${TCD_PROJECT_DIR:-docs/project}"
tracks_dir="${TCD_TRACKS_DIR:-$project_dir/tracks}"
tasks_dir="${TCD_TASKS_DIR:-$project_dir/tasks}"

track_dir="$tracks_dir/$track_slug"
plan_file="$track_dir/plan.md"

if [ ! -d "$track_dir" ] || [ ! -f "$plan_file" ]; then
  echo "track not found or missing plan.md: $track_dir (create with tcd.sh track ...)" >&2
  exit 2
fi

task_base="$(basename "$task_path")"
task_rel="docs/project/tasks/$task_base"

# Patch the task brief to reference the track in Dependencies (best-effort).
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
awk -v track="docs/project/tracks/'"$track_slug"'/" '
  BEGIN { in_deps=0; wrote=0 }
  $0 == "## Dependencies" { in_deps=1; print; next }
  in_deps && $0 ~ /^## / {
    if (!wrote) {
      print ""
      print "- Track: " track
      wrote=1
    }
    in_deps=0
    print
    next
  }
  in_deps && $0 ~ /^- Track:/ { print "- Track: " track; wrote=1; next }
  { print }
  END {
    if (in_deps && !wrote) {
      print ""
      print "- Track: " track
    }
  }
' "$task_path" >"$tmp"
mv "$tmp" "$task_path"

# Insert into track plan under the phase.
tmp2="$(mktemp)"
trap 'rm -f "$tmp2"' EXIT

phase_header="### $phase"
task_line="- [ ] Task: $task_rel"

if ! grep -qF -- "$phase_header" "$plan_file"; then
  # Create the phase at end of phases section (best-effort: append before checkpoints if present).
  awk -v ph="$phase_header" -v tl="$task_line" '
    $0 == "## Checkpoints" && !added {
      print ""
      print ph
      print ""
      print tl
      print ""
      added=1
      print
      next
    }
    { print }
    END {
      if (!added) {
        print ""
        print ph
        print ""
        print tl
      }
    }
  ' "$plan_file" >"$tmp2"
  mv "$tmp2" "$plan_file"
else
  # Add task line right after phase header if not present.
  awk -v ph="$phase_header" -v tl="$task_line" '
    $0 == ph {
      print
      in_phase=1
      next
    }
    in_phase && $0 ~ /^### / {
      if (!added) { print tl; added=1 }
      in_phase=0
      print
      next
    }
    {
      if (in_phase && $0 == tl) { added=1 }
      print
    }
    END {
      if (in_phase && !added) { print tl }
    }
  ' "$plan_file" >"$tmp2"
  mv "$tmp2" "$plan_file"
fi

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$script_dir/tcd_update_index.sh" >/dev/null

echo "OK: linked $task_base -> track $track_slug ($phase)"

