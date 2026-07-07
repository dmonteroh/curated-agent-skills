#!/usr/bin/env sh
set -eu

# Validate repo work-management artifacts for Tracks Conductor Protocol.
# This is intentionally lightweight: it checks structure + index coverage.

project_dir="${TCD_PROJECT_DIR:-docs/project}"
todo_dir="${TCD_TODO_DIR:-$project_dir/to-do}"
tasks_dir="${TCD_TASKS_DIR:-$project_dir/tasks}"
tracks_dir="${TCD_TRACKS_DIR:-$project_dir/tracks}"
futures_dir="${TCD_FUTURES_DIR:-$project_dir/futures}"
order_file="${TCD_ORDER_FILE:-$project_dir/order.csv}"

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

for f in "$tasks_dir"/S*-T-*.md; do
  [ -f "$f" ] || continue
  id="$(basename "$f" .md)"
  grep -qF "$id" "$work_index" || { echo "index missing task: $id" >&2; missing=1; }
  "$script_dir/tcd_validate_file.sh" task "$f" >/dev/null || missing=1
done

if [ -f "$order_file" ]; then
  # Parsing contract shared with ordered-dispatch runners that consume order.csv:
  # optional header row mapped by name (extra budget columns picked up wherever
  # they sit), RFC-4180-style double-quoted cells (commas inside quotes), and
  # every *_secs budget column validated as integer > 0 when non-empty.
  order_ids_tmp="$(mktemp)"
  awk '
    function trim(s) { gsub(/^[ \t\r\n]+|[ \t\r\n]+$/, "", s); return s }
    function enabled(v, x) {
      x=tolower(trim(v))
      if (x=="" || x=="1" || x=="true" || x=="yes" || x=="y" || x=="on") return 1
      if (x=="0" || x=="false" || x=="no" || x=="n" || x=="off") return 0
      return -1
    }
    # Quote-aware CSV splitter ("" inside a quoted cell is a literal quote).
    # Clears the target array first so short rows never inherit stale cells.
    function split_csv(line, cells,   n, i, c, cur, inq, len, k) {
      for (k in cells) delete cells[k]
      n = 0; cur = ""; inq = 0; len = length(line)
      for (i = 1; i <= len; i++) {
        c = substr(line, i, 1)
        if (inq) {
          if (c == "\"") {
            if (substr(line, i + 1, 1) == "\"") { cur = cur "\""; i++ }
            else inq = 0
          } else cur = cur c
        } else if (c == "\"" && cur == "") inq = 1
        else if (c == ",") { cells[++n] = cur; cur = "" }
        else cur = cur c
      }
      cells[++n] = cur
      return n
    }
    function check_budget(name, v, id) {
      if (v != "" && (v !~ /^[0-9]+$/ || v+0 <= 0)) {
        printf("invalid %s in %s for task %s: %s (must be integer > 0)\n", name, FILENAME, id, v) > "/dev/stderr"
        bad = 1
      }
    }
    BEGIN {
      # v1 positional fallback when no header row is present.
      col_order = 1; col_id = 2; col_enabled = 3; col_timeout = 5
      col_nps = 0; col_hcs = 0
    }
    NR == 1 {
      nc = split_csv($0, cells)
      c1 = tolower(trim(cells[1])); c2 = tolower(trim(cells[2]))
      if ((c1 == "order" || c1 == "run_order") && (c2 == "task_id" || c2 == "id")) {
        col_timeout = 0
        for (i = 3; i <= nc; i++) {
          h = tolower(trim(cells[i]))
          if (h == "enabled") col_enabled = i
          else if (h == "timeout_secs") col_timeout = i
          else if (h == "no_progress_secs") col_nps = i
          else if (h == "hard_ceiling_secs") col_hcs = i
        }
        next
      }
    }
    {
      nc = split_csv($0, cells)
      o = trim(cells[col_order]); id = trim(cells[col_id])
      if (o == "" || id == "") next
      e = enabled(cells[col_enabled])
      if (e == -1) { printf("invalid enabled value in %s for task %s: %s\n", FILENAME, id, cells[col_enabled]) > "/dev/stderr"; bad=1; next }
      if (e == 0) next
      if (o !~ /^[0-9]+$/) { printf("invalid order value in %s for task %s: %s\n", FILENAME, id, o) > "/dev/stderr"; bad=1 }
      if (col_timeout > 0) check_budget("timeout_secs", trim(cells[col_timeout]), id)
      if (col_nps > 0) check_budget("no_progress_secs", trim(cells[col_nps]), id)
      if (col_hcs > 0) check_budget("hard_ceiling_secs", trim(cells[col_hcs]), id)
      if (++seen_order[o] > 1) { printf("duplicate order in %s: %s\n", FILENAME, o) > "/dev/stderr"; bad=1 }
      if (++seen_task[id] > 1) { printf("duplicate task_id in %s: %s\n", FILENAME, id) > "/dev/stderr"; bad=1 }
      print id
    }
    END { if (bad) exit 1 }
  ' "$order_file" >"$order_ids_tmp" || missing=1

  if [ -s "$order_ids_tmp" ]; then
    while IFS= read -r ordered_id; do
      [ -n "$ordered_id" ] || continue
      [ -f "$tasks_dir/$ordered_id.md" ] || { echo "order.csv references missing task: $ordered_id" >&2; missing=1; }
    done <"$order_ids_tmp"
  fi

  rm -f "$order_ids_tmp"
fi

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
