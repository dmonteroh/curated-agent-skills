#!/usr/bin/env sh
set -eu

# Fast, read-only debt signal scan.
# Emits a markdown report to docs/_docgen/tech_debt_scan.md by default.
#
# This is intentionally generic and should be run inside a real code repo (not the skills repo).

out_dir="${DEBT_SCAN_OUT_DIR:-docs/_docgen}"
out_file="${DEBT_SCAN_OUT_FILE:-$out_dir/tech_debt_scan.md}"
limit="${DEBT_SCAN_LIMIT:-20}"

mkdir -p "$out_dir"

have_rg=0
if command -v rg >/dev/null 2>&1; then
  have_rg=1
fi

echo "== Debt scan -> $out_file =="

largest_files() {
  if [ "$have_rg" -eq 1 ]; then
    rg --files . | while read -r f; do
      [ -f "$f" ] || continue
      case "$f" in
        */node_modules/*|*/dist/*|*/build/*|*/.git/*) continue ;;
      esac
      lc="$(wc -l <"$f" 2>/dev/null || echo 0)"
      printf "%10s %s\n" "$lc" "$f"
    done | sort -nr | head -n "$limit"
  else
    find . -type f ! -path '*/.git/*' ! -path '*/node_modules/*' -print0 \
      | while IFS= read -r -d '' f; do
          lc="$(wc -l <"$f" 2>/dev/null || echo 0)"
          printf "%10s %s\n" "$lc" "$f"
        done | sort -nr | head -n "$limit"
  fi
}

grep_counts() {
  pat="$1"
  label="$2"
  echo "### $label"
  if [ "$have_rg" -eq 1 ]; then
    rg -n --no-heading "$pat" . 2>/dev/null \
      | awk -F: '{print $1}' | sort | uniq -c | sort -nr | head -n "$limit" || true
  else
    grep -RIn -- "$pat" . 2>/dev/null \
      | awk -F: '{print $1}' | sort | uniq -c | sort -nr | head -n "$limit" || true
  fi
  echo
}

{
  echo "# Tech Debt Signal Scan"
  echo
  echo "Generated: $(date -u +%F) (UTC)"
  echo
  echo "## Large files (proxy for complexity)"
  echo
  echo '```'
  largest_files
  echo '```'
  echo
  echo "## Common debt markers (file hit counts)"
  echo
  grep_counts "TODO|FIXME|HACK|XXX" "TODO/FIXME/HACK/XXX"
  grep_counts "deprecated|DEPRECATED" "Deprecated usage"
  grep_counts "eslint-disable|ts-ignore|ts-nocheck" "Lint/type suppression"
  grep_counts "any\\b" "TypeScript any (best-effort)"
  grep_counts "console\\.log\\b|print\\(" "Debug logging (best-effort)"
  echo "## Notes"
  echo
  echo "- Treat this as a signal generator. Convert findings into a debt register with evidence + ROI."
  echo "- Use \`tracks-conductor-protocol\` to turn the top items into a track + tasks."
} >"$out_file"

echo "OK: wrote $out_file"

