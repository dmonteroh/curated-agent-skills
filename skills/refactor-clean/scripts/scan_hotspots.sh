#!/usr/bin/env sh
set -eu

# Quick hotspot scan to accelerate refactoring.
# Prints:
# - largest files by line count (best-effort)
# - TODO/FIXME counts
# - common smell markers (best-effort grep patterns)
#
# Safe-by-default: read-only.

limit="${HOTSPOT_LIMIT:-20}"

have_rg=0
if command -v rg >/dev/null 2>&1; then
  have_rg=1
fi

echo "== Largest Files (by line count, top $limit) =="
if [ "$have_rg" -eq 1 ]; then
  rg --files . | while read -r f; do
    [ -f "$f" ] || continue
    # Skip huge vendor dirs if present.
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

echo
echo "== TODO / FIXME Counts =="
if [ "$have_rg" -eq 1 ]; then
  rg -n --no-heading "TODO|FIXME|HACK|XXX" . 2>/dev/null \
    | awk -F: '{print $1}' | sort | uniq -c | sort -nr | head -n "$limit" || true
else
  grep -RIn -- "TODO\\|FIXME\\|HACK\\|XXX" . 2>/dev/null \
    | awk -F: '{print $1}' | sort | uniq -c | sort -nr | head -n "$limit" || true
fi

echo
echo "== Smell Markers (best-effort) =="
echo "- Long parameter lists: grep for patterns like \", , ,\" / many args"
echo "- Exception swallowing: \"catch (e) { }\" / empty catch blocks"
echo "- Deep nesting: identify files with many indented blocks"
echo
echo "Tip: use this output to pick 1-3 targets, then refactor incrementally with tests."

