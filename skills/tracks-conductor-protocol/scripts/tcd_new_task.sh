#!/usr/bin/env sh
set -eu

# Create a new task brief and (optionally) link it to an intake draft and/or track.
#
# Usage:
#   TCD_SEQ=S01 ./tracks-conductor-protocol/scripts/tcd_new_task.sh "Implement X"
#   TCD_SEQ=S02 TCD_TRACK="billing-redesign" TCD_INTAKE="TD-20260130-something" ./.../tcd_new_task.sh "Implement X"

title="${1:-}"
if [ -z "$title" ]; then
  echo "usage: $0 \"title\"" >&2
  exit 2
fi

project_dir="${TCD_PROJECT_DIR:-docs/project}"
tasks_dir="${TCD_TASKS_DIR:-$project_dir/tasks}"

seq="${TCD_SEQ:-}"
track="${TCD_TRACK:-}"
intake_id="${TCD_INTAKE:-}"

mkdir -p "$tasks_dir"

today="$(date +%Y%m%d)"

slugify() {
  printf "%s" "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | tr ' _' '--' \
    | sed -E 's/[^a-z0-9-]+/-/g; s/-+/-/g; s/^-//; s/-$//'
}

if [ -z "$seq" ]; then
  # Best-effort: pick next S## based on existing filenames.
  max=0
  for f in "$tasks_dir"/S[0-9][0-9]-T-*.md; do
    [ -f "$f" ] || continue
    s="$(basename "$f" | sed -n 's/^S\([0-9][0-9]\)-T-.*/\1/p')"
    [ -n "$s" ] || continue
    n=$((10#$s))
    if [ "$n" -gt "$max" ]; then max="$n"; fi
  done
  seq=$(printf "S%02d" $((max + 1)))
fi

slug="$(slugify "$title")"
id="${seq}-T-$today-$slug"
file="$tasks_dir/$id.md"

if [ -e "$file" ]; then
  echo "refusing to overwrite: $file" >&2
  exit 1
fi

{
  echo "---"
  echo "id: $id"
  echo "status: Draft"
  if [ -n "$track" ]; then
    echo "track: $track"
  fi
  if [ -n "$intake_id" ]; then
    echo "intake: $intake_id"
  fi
  echo "---"
  echo
  echo "# $seq - $title"
  echo
  echo "## Intent"
  echo
  echo "<1-2 sentences: user outcome or system behavior>"
  echo
  echo "## Scope"
  echo
  echo "In scope:"
  echo "- ..."
  echo
  echo "Out of scope:"
  echo "- ..."
  echo
  echo "## Dependencies"
  echo
  if [ -n "$track" ]; then
    echo "- Track: docs/project/tracks/$track/"
  else
    echo "- Track: <optional>"
  fi
  echo "- ADRs:"
  echo "  - ADR-XXXX: ..."
  echo "- Futures:"
  echo "  - FUT-XXX: ..."
  echo "- Other tasks:"
  echo "  - $seq-T-$today-...: ..."
  echo
  echo "## Acceptance Criteria"
  echo
  echo "- [ ] ..."
  echo "- [ ] ..."
  echo
  echo "## Risks/Notes"
  echo
  echo "- <only if invariants, security, or major constraints>"
  echo
  echo "## Links"
  echo
  if [ -n "$intake_id" ]; then
    echo "- Intake draft: docs/project/to-do/$intake_id.md"
  else
    echo "- Intake draft: <optional>"
  fi
  echo "- Context (CDD):"
  echo "  - docs/context/product.md"
  echo "  - docs/context/tech-stack.md"
  echo "  - docs/context/workflow.md"
} >"$file"

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$script_dir/tcd_update_index.sh" >/dev/null

echo "OK: created $file"
