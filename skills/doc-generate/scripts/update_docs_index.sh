#!/usr/bin/env sh
set -eu

# Deterministically rebuild a docs index table inside docs/README.md.
#
# Managed block markers:
#   <!-- DOC-INDEX:START -->
#   <!-- DOC-INDEX:END -->
#
# The script is conservative: it only rewrites between markers.

docs_dir="${DOCS_DIR:-docs}"
index_file="${DOCS_INDEX_FILE:-$docs_dir/README.md}"

start="<!-- DOC-INDEX:START -->"
end="<!-- DOC-INDEX:END -->"

if [ ! -d "$docs_dir" ]; then
  echo "docs dir not found: $docs_dir" >&2
  exit 2
fi

touch "$index_file"

if ! grep -qF "$start" "$index_file" || ! grep -qF "$end" "$index_file"; then
  cat >>"$index_file" <<EOF

$start
| Doc | Purpose |
| --- | --- |
$end
EOF
fi

tmp="$(mktemp)"
tmp_out="$(mktemp)"
cleanup() { rm -f "$tmp" "$tmp_out"; }
trap cleanup EXIT

# Build a simple table:
# - Include markdown files under docs/ excluding docs/_docgen and docs/README.md itself.
# - Keep stable alphabetical ordering.
{
  echo "$start"
  echo "| Doc | Purpose |"
  echo "| --- | --- |"

  find "$docs_dir" -type f -name "*.md" \
    ! -path "$docs_dir/_docgen/*" \
    ! -path "$docs_dir/README.md" \
    | LC_ALL=C sort \
    | while read -r f; do
        rel="./${f#$docs_dir/}"
        # Best-effort purpose: first H1 line if present, else empty.
        h1="$(awk 'NR==1 && $0 ~ /^# / { sub(/^#[[:space:]]+/, \"\", $0); print; exit }' "$f" 2>/dev/null || true)"
        printf '| %s | %s |\n' "$rel" "${h1:-}"
      done

  echo "$end"
} >"$tmp_out"

awk -v start="$start" -v end="$end" -v block="$tmp_out" '
  BEGIN {
    while ((getline line < block) > 0) { newblock = newblock line "\n" }
    close(block)
  }
  $0 == start { printing=1; printf "%s", newblock; next }
  printing && $0 == end { printing=0; next }
  !printing { print }
' "$index_file" >"$tmp"
mv "$tmp" "$index_file"

echo "OK: updated docs index in $index_file"
