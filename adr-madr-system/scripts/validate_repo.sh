#!/usr/bin/env sh
set -eu

# Validate all ADR files in a repo and ensure the ADR index has a managed block.
#
# Usage:
#   ADR_DIR=docs/adr ADR_INDEX=docs/adr/README.md ./adr-madr-system/scripts/validate_repo.sh

adr_dir="${ADR_DIR:-docs/adr}"
index_file="${ADR_INDEX:-$adr_dir/README.md}"

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if [ ! -d "$adr_dir" ]; then
  echo "adr dir not found: $adr_dir" >&2
  exit 2
fi

found=0
for f in "$adr_dir"/ADR-[0-9][0-9][0-9][0-9]-*.md "$adr_dir"/ADR-[0-9][0-9][0-9][0-9].md; do
  [ -f "$f" ] || continue
  found=1
  "$script_dir/validate_adr.sh" "$f" >/dev/null
done

if [ "$found" -eq 0 ]; then
  echo "no ADR files found under: $adr_dir" >&2
  exit 2
fi

if [ ! -f "$index_file" ]; then
  echo "ADR index not found: $index_file" >&2
  exit 2
fi

start_marker="<!-- ADR-INDEX:START -->"
end_marker="<!-- ADR-INDEX:END -->"
if ! grep -qF "$start_marker" "$index_file" || ! grep -qF "$end_marker" "$index_file"; then
  echo "ADR index missing managed block markers in: $index_file" >&2
  exit 1
fi

# Check coverage: every ADR ID should appear at least once in the index file.
missing=0
for f in "$adr_dir"/ADR-[0-9][0-9][0-9][0-9]-*.md "$adr_dir"/ADR-[0-9][0-9][0-9][0-9].md; do
  [ -f "$f" ] || continue
  id="$(awk 'NR==1{print; exit}' "$f" | sed -n 's/^# \(ADR-[0-9][0-9][0-9][0-9]\):.*/\1/p')"
  if [ -z "$id" ]; then
    echo "bad ADR header (missing ID): $f" >&2
    missing=1
    continue
  fi
  if ! grep -qF "$id" "$index_file"; then
    echo "index missing ADR entry: $id ($f)" >&2
    missing=1
  fi
done

if [ "$missing" -ne 0 ]; then
  echo "FAILED: index coverage issues" >&2
  exit 1
fi

echo "OK: ADR repo validation passed ($adr_dir)"
