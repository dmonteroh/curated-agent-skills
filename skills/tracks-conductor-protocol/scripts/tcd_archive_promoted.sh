#!/usr/bin/env sh
set -eu

# Archive promoted intake drafts.
#
# Any TD-*.md in to-do/ that is referenced by a task brief's `intake:`
# frontmatter is considered promoted: its `## Status` is stamped
# `Accepted (promoted to <task-ids> on <date>)` and the file is moved to
# archive/to-do/. Idempotent and safe to re-run (already-archived intakes are
# no longer in to-do/, so they are simply not found).
#
# Usage:
#   tcd_archive_promoted.sh                  # sweep: archive every promoted intake
#   tcd_archive_promoted.sh path/to/TD-*.md  # archive one specific intake (by path)
#   tcd_archive_promoted.sh TD-YYYYMMDD-...  # ... or by id
#
# Env overrides: TCD_PROJECT_DIR, TCD_TODO_DIR, TCD_TASKS_DIR,
#                TCD_ARCHIVE_TODO_DIR

project_dir="${TCD_PROJECT_DIR:-docs/project}"
todo_dir="${TCD_TODO_DIR:-$project_dir/to-do}"
tasks_dir="${TCD_TASKS_DIR:-$project_dir/tasks}"
archive_dir="${TCD_ARCHIVE_TODO_DIR:-$project_dir/archive/to-do}"
today="$(date +%Y-%m-%d)"

archived=0

# Task-id prefixes (SNN-T-YYYYMMDD) of tasks that reference the given intake id,
# de-duplicated and joined with ", ". Empty when the intake is not promoted.
referencing_targets() {
  _id="$1"
  grep -lE "^intake:[[:space:]]+${_id}[[:space:]]*\$" "$tasks_dir"/*.md 2>/dev/null \
    | while IFS= read -r _t; do
        basename "$_t" .md | sed -E 's/^(S[0-9]+-T-[0-9]{8}).*/\1/'
      done | sort -u | awk 'NR>1{printf ", "}{printf "%s",$0}'
}

archive_one() {
  _path="$1"
  _base="$(basename "$_path")"
  _id="${_base%.md}"

  _targets="$(referencing_targets "$_id")"
  if [ -z "$_targets" ]; then
    echo "skip: $_base is not referenced by any task (not promoted)" >&2
    return 0
  fi

  mkdir -p "$archive_dir"

  # Replace the value line under `## Status` (format: heading, blank, value).
  _tmp="$(mktemp)"
  awk -v repl="Accepted (promoted to ${_targets} on ${today})" '
    $0 == "## Status" {print; getline; print ""; getline; print repl; in_s=1; next}
    in_s==1 {in_s=0}
    {print}
  ' "$_path" >"$_tmp" || true
  if [ -s "$_tmp" ]; then mv "$_tmp" "$_path"; else rm -f "$_tmp"; fi

  _dest="$archive_dir/$_base"
  if git ls-files --error-unmatch "$_path" >/dev/null 2>&1; then
    git mv -f "$_path" "$_dest"
  else
    mv -f "$_path" "$_dest"
  fi
  echo "OK: archived $_base -> $archive_dir/ (promoted to $_targets)"
  archived=$((archived + 1))
}

if [ "$#" -ge 1 ] && [ -n "${1:-}" ]; then
  arg="$1"
  if [ -f "$arg" ]; then
    archive_one "$arg"
  elif [ -f "$todo_dir/$arg" ]; then
    archive_one "$todo_dir/$arg"
  elif [ -f "$todo_dir/$arg.md" ]; then
    archive_one "$todo_dir/$arg.md"
  else
    echo "not found: $arg" >&2
    exit 2
  fi
else
  for f in "$todo_dir"/TD-*.md; do
    [ -e "$f" ] || continue
    archive_one "$f"
  done
fi

echo "OK: archive-promoted complete ($archived archived)"
