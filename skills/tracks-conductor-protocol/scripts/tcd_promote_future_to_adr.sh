#!/usr/bin/env sh
set -eu

# Promote a Future entry into an ADR using the adr-madr-system scripts.
#
# Usage:
#   scripts/tcd_promote_future_to_adr.sh path/to/FUT-XXX-....md
#
# Behavior:
# - Marks the Future as Triggered (best-effort).
# - Creates a new ADR titled "Address <FUT-XXX>: <topic>".
# - Adds links in the ADR back to the Future path.
#
# Env overrides:
#   TCD_NEW_ADR=path/to/new_adr.sh (explicit location of the ADR scaffold script)

future_path="${1:-}"
if [ -z "$future_path" ] || [ ! -f "$future_path" ]; then
  echo "usage: $0 path/to/FUT-XXX-*.md" >&2
  exit 2
fi

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

# Locate new_adr.sh: env override, vendored next to these scripts, sibling
# skill install, or skill folder copied into the target repo root (cwd).
new_adr=""
for candidate in \
  "${TCD_NEW_ADR:-}" \
  "$script_dir/adr-madr/new_adr.sh" \
  "$script_dir/../../adr-madr-system/scripts/new_adr.sh" \
  "adr-madr-system/scripts/new_adr.sh"; do
  [ -n "$candidate" ] || continue
  if [ -x "$candidate" ]; then new_adr="$candidate"; break; fi
done

if [ -z "$new_adr" ]; then
  echo "adr-madr-system new_adr.sh not found; set TCD_NEW_ADR=path/to/new_adr.sh" >&2
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

adr_title="Address $future_id: $topic"

# Create ADR.
ADR_DECIDERS="${ADR_DECIDERS:-}" \
  "$new_adr" "$adr_title" >/dev/null

# Best-effort: append link to the future into the newest ADR created (highest number).
adr_dir="${ADR_DIR:-docs/adr}"
newest="$(ls -1 "$adr_dir"/ADR-[0-9][0-9][0-9][0-9]-*.md 2>/dev/null | sort | tail -n 1 || true)"
if [ -n "$newest" ]; then
  printf '\n- Futures:\n  - docs/project/futures/%s\n' "$future_base" >>"$newest"
fi

"$script_dir/tcd_update_index.sh" >/dev/null

echo "OK: promoted $future_id -> ADR (created via adr-madr-system scripts)"
