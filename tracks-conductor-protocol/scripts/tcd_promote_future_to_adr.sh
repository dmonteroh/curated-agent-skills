#!/usr/bin/env sh
set -eu

# Promote a Future entry into an ADR using adr-madr-system (if available).
#
# Usage:
#   ./tracks-conductor-protocol/scripts/tcd_promote_future_to_adr.sh path/to/FUT-XXX-....md
#
# Behavior:
# - Marks the Future as Triggered (best-effort).
# - Creates a new ADR titled "Address <FUT-XXX>: <topic>".
# - Adds links in the ADR back to the Future path.

future_path="${1:-}"
if [ -z "$future_path" ] || [ ! -f "$future_path" ]; then
  echo "usage: $0 path/to/FUT-XXX-*.md" >&2
  exit 2
fi

future_base="$(basename "$future_path")"
future_id="$(printf "%s" "$future_base" | sed -n 's/^\(FUT-[0-9][0-9][0-9]\).*/\1/p')"
if [ -z "$future_id" ]; then
  echo "could not parse FUT id from: $future_base" >&2
  exit 1
fi

topic="$(awk 'NR==1{ sub(/^#[[:space:]]+/, "", $0); print; exit }' "$future_path")"
if [ -z "$topic" ]; then
  echo "missing H1 topic in: $future_path" >&2
  exit 1
fi

# Mark future as Triggered (replace first status line).
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
awk '
  $0 == "## Status" {print; getline; print ""; getline; print "Triggered"; in_status=1; next}
  in_status==1 {in_status=0}
  {print}
' "$future_path" >"$tmp" || true
if [ -s "$tmp" ]; then mv "$tmp" "$future_path"; fi

# Find adr-madr-system scripts relative to repo root.
if [ ! -x "adr-madr-system/scripts/new_adr.sh" ]; then
  echo "adr-madr-system not found or not executable: adr-madr-system/scripts/new_adr.sh" >&2
  exit 2
fi

adr_title="Address $future_id: $topic"

# Create ADR.
ADR_DECIDERS="${ADR_DECIDERS:-}" \
  ./adr-madr-system/scripts/new_adr.sh "$adr_title" >/dev/null

# Best-effort: append link to the future into the newest ADR created (highest number).
adr_dir="${ADR_DIR:-docs/adr}"
newest="$(ls -1 "$adr_dir"/ADR-[0-9][0-9][0-9][0-9]-*.md 2>/dev/null | sort | tail -n 1 || true)"
if [ -n "$newest" ]; then
  printf '\n- Futures:\n  - docs/project/futures/%s\n' "$future_base" >>"$newest"
fi

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$script_dir/tcd_update_index.sh" >/dev/null

echo "OK: promoted $future_id -> ADR (created via adr-madr-system)"
