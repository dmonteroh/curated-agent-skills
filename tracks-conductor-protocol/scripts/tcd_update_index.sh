#!/usr/bin/env sh
set -eu

# Rebuild the Work Index managed blocks deterministically.
# This is designed for multi-agent usage: it only rewrites within START/END markers.

project_dir="${TCD_PROJECT_DIR:-docs/project}"
todo_dir="${TCD_TODO_DIR:-$project_dir/to-do}"
tasks_dir="${TCD_TASKS_DIR:-$project_dir/tasks}"
tracks_dir="${TCD_TRACKS_DIR:-$project_dir/tracks}"
futures_dir="${TCD_FUTURES_DIR:-$project_dir/futures}"

work_index="${TCD_WORK_INDEX:-$project_dir/work_index.md}"
tracks_registry="${TCD_TRACKS_REGISTRY:-$project_dir/tracks.md}"
task_status="${TCD_TASK_STATUS:-$project_dir/task_status.md}"

start_end_replace() {
  file="$1"
  start="$2"
  end="$3"
  block_file="$4"

  if [ ! -f "$file" ]; then
    echo "missing file: $file" >&2
    return 1
  fi

  if ! grep -qF "$start" "$file" || ! grep -qF "$end" "$file"; then
    echo "missing block markers in $file: $start / $end" >&2
    return 1
  fi

  awk -v start="$start" -v end="$end" -v block="$block_file" '
    BEGIN {
      while ((getline line < block) > 0) { newblock = newblock line "\n" }
      close(block)
    }
    $0 == start { printing=1; printf "%s", newblock; next }
    printing && $0 == end { printing=0; next }
    !printing { print }
  ' "$file" >"${file}.tmp"
  mv "${file}.tmp" "$file"
}

extract_first_h1() {
  # Prints the first H1 line without "# ".
  awk 'NR==1{ sub(/^#[[:space:]]+/, "", $0); print; exit }' "$1"
}

extract_status() {
  # Extract first non-empty line after "## Status".
  awk '
    $0 == "## Status" {found=1; next}
    found {
      if ($0 ~ /^## /) { exit }
      if ($0 ~ /^[[:space:]]*$/) { next }
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
      print $0
      exit
    }
  ' "$1"
}

tmp="$(mktemp)"
cleanup() { rm -f "$tmp" "$tmp".*; }
trap cleanup EXIT

mkdir -p "$project_dir"
touch "$work_index"

# Build a best-effort task id -> status map from task_status.md.
# Expected: sections like "## In Progress" containing lines that include the task id.
task_map="$tmp.taskmap"
: >"$task_map"
if [ -f "$task_status" ]; then
  awk '
    function flush() {}
    /^##[[:space:]]+/ {
      status = $0
      sub(/^##[[:space:]]+/, "", status)
      next
    }
    {
      # Extract task ids from arbitrary lines.
      while (match($0, /(S[0-9][0-9]-T-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[a-z0-9-]+)/)) {
        id = substr($0, RSTART, RLENGTH)
        print id "\t" status
        $0 = substr($0, RSTART + RLENGTH)
      }
    }
  ' "$task_status" | awk '!seen[$1]++' >"$task_map"
fi

task_status_for() {
  # $1 = task id
  awk -v id="$1" '$1==id{print $2; exit}' "$task_map"
}

# --- Intake table ---
intake_block="$tmp.intake"
{
  echo "<!-- TCD:INTAKE:START -->"
  echo "| ID | Title | Status | Date | Owner | Links | Track | Tags |"
  echo "| --- | --- | --- | --- | --- | --- | --- | --- |"

  if [ -d "$todo_dir" ]; then
    for f in "$todo_dir"/TD-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-*.md; do
      [ -f "$f" ] || continue
      base="$(basename "$f")"
      id="${base%.md}"
      date="$(printf "%s" "$base" | sed -n 's/^TD-\([0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]\).*/\1/p')"
      title="$(extract_first_h1 "$f")"
      status="$(extract_status "$f")"
      rel="./to-do/$base"
      printf '| %s | %s | %s | %s |  | %s |  | |\n' "$id" "$title" "${status:-}" "${date:-}" "$rel"
    done
  fi

  echo "<!-- TCD:INTAKE:END -->"
} >"$intake_block"

# Sort rows inside block (stable). Keep header/footer lines fixed.
awk 'NR<=3{print; next} $0 ~ /^\\| TD-/{print}' "$intake_block" | sort -t '|' -k4,4 -k2,2 >"$tmp.intake.rows" 2>/dev/null || true
{
  sed -n '1,3p' "$intake_block"
  cat "$tmp.intake.rows"
  echo "<!-- TCD:INTAKE:END -->"
} >"$tmp.intake.final"
start_end_replace "$work_index" "<!-- TCD:INTAKE:START -->" "<!-- TCD:INTAKE:END -->" "$tmp.intake.final"

# --- Tasks table (best-effort; status truth lives in task_status.md) ---
tasks_block="$tmp.tasks"
{
  echo "<!-- TCD:TASKS:START -->"
  echo "| ID | Title | Status | Seq | Date | Links | Track | ADRs | Futures |"
  echo "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"

  if [ -d "$tasks_dir" ]; then
    for f in "$tasks_dir"/S[0-9][0-9]-T-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-*.md; do
      [ -f "$f" ] || continue
      base="$(basename "$f")"
      id="${base%.md}"
      seq="$(printf "%s" "$base" | sed -n 's/^\(S[0-9][0-9]\)-T-.*/\1/p')"
      date="$(printf "%s" "$base" | sed -n 's/^S[0-9][0-9]-T-\([0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]\).*/\1/p')"
      title="$(extract_first_h1 "$f")"
      rel="./tasks/$base"
      status="$(task_status_for "$id")"
      printf '| %s | %s | %s | %s | %s | %s |  |  |  |\n' "$id" "$title" "${status:-}" "${seq:-}" "${date:-}" "$rel"
    done
  fi

  echo "<!-- TCD:TASKS:END -->"
} >"$tasks_block"

awk 'NR<=3{print; next} $0 ~ /^\\| S[0-9][0-9]-T-/{print}' "$tasks_block" | sort -t '|' -k4,4 -k5,5 -k2,2 >"$tmp.tasks.rows" 2>/dev/null || true
{
  sed -n '1,3p' "$tasks_block"
  cat "$tmp.tasks.rows"
  echo "<!-- TCD:TASKS:END -->"
} >"$tmp.tasks.final"
start_end_replace "$work_index" "<!-- TCD:TASKS:START -->" "<!-- TCD:TASKS:END -->" "$tmp.tasks.final"

# --- Tracks table + tracks registry ---
tracks_block="$tmp.tracks"
registry_block="$tmp.tracks_registry"
{
  echo "<!-- TCD:TRACKS:START -->"
  echo "| Track | Title | Status | Owner | Links | ADRs | Futures |"
  echo "| --- | --- | --- | --- | --- | --- | --- |"

  if [ -d "$tracks_dir" ]; then
    for d in "$tracks_dir"/*; do
      [ -d "$d" ] || continue
      slug="$(basename "$d")"
      spec="$d/spec.md"
      plan="$d/plan.md"
      title=""
      status=""
      if [ -f "$spec" ]; then
        title="$(extract_first_h1 "$spec")"
        status="$(extract_status "$spec")"
      fi
      rel="./tracks/$slug/"
      printf '| %s | %s | %s |  | %s |  |  |\n' "$slug" "${title:-}" "${status:-}" "$rel"
    done
  fi

  echo "<!-- TCD:TRACKS:END -->"
} >"$tracks_block"

awk 'NR<=3{print; next} $0 ~ /^\\| [^ ]/{print}' "$tracks_block" | grep -vF -- '---' | sort -t '|' -k2,2 >"$tmp.tracks.rows" 2>/dev/null || true
{
  sed -n '1,3p' "$tracks_block"
  cat "$tmp.tracks.rows"
  echo "<!-- TCD:TRACKS:END -->"
} >"$tmp.tracks.final"
start_end_replace "$work_index" "<!-- TCD:TRACKS:START -->" "<!-- TCD:TRACKS:END -->" "$tmp.tracks.final"

if [ -f "$tracks_registry" ]; then
  {
    echo "<!-- TCD:TRACK-REGISTRY:START -->"
    echo "| Track | Title | Status | Links |"
    echo "| --- | --- | --- | --- |"
    awk 'NR>3 && $0 ~ /^\\| [^ ]/{print}' "$tmp.tracks.final" \
      | sed -E 's/^\\| ([^|]+) \\| ([^|]+) \\| ([^|]+) \\| ([^|]+) \\| ([^|]+) \\|.*$/| \\1 | \\2 | | \\4 |/' \
      | sort -t '|' -k2,2
    echo "<!-- TCD:TRACK-REGISTRY:END -->"
  } >"$registry_block"

  start_end_replace "$tracks_registry" "<!-- TCD:TRACK-REGISTRY:START -->" "<!-- TCD:TRACK-REGISTRY:END -->" "$registry_block"
fi

# --- Futures table (file-per-entry) ---
futures_block="$tmp.futures"
{
  echo "<!-- TCD:FUTURES:START -->"
  echo "| ID | Topic | Status | Strategy | Trigger | Links |"
  echo "| --- | --- | --- | --- | --- | --- |"

  if [ -d "$futures_dir" ]; then
    for f in "$futures_dir"/FUT-[0-9][0-9][0-9]-*.md "$futures_dir"/FUT-[0-9][0-9][0-9].md; do
      [ -f "$f" ] || continue
      base="$(basename "$f")"
      id="$(printf "%s" "$base" | sed -n 's/\(FUT-[0-9][0-9][0-9]\).*/\1/p')"
      topic="$(extract_first_h1 "$f")"
      status="$(extract_status "$f")"
      rel="./futures/$base"
      printf '| %s | %s | %s |  |  | %s |\n' "$id" "$topic" "${status:-}" "$rel"
    done
  fi

  echo "<!-- TCD:FUTURES:END -->"
} >"$futures_block"

awk 'NR<=3{print; next} $0 ~ /^\\| FUT-/{print}' "$futures_block" | sort -t '|' -k2,2 >"$tmp.futures.rows" 2>/dev/null || true
{
  sed -n '1,3p' "$futures_block"
  cat "$tmp.futures.rows"
  echo "<!-- TCD:FUTURES:END -->"
} >"$tmp.futures.final"
start_end_replace "$work_index" "<!-- TCD:FUTURES:START -->" "<!-- TCD:FUTURES:END -->" "$tmp.futures.final"

echo "OK: rebuilt index blocks in $work_index"
