#!/usr/bin/env sh
set -eu

# Deterministically rebuild docs/context/README.md inside a managed block.

context_dir="${CONTEXT_DIR:-docs/context}"
index_file="${CONTEXT_INDEX:-$context_dir/README.md}"

start="<!-- CONTEXT-INDEX:START -->"
end="<!-- CONTEXT-INDEX:END -->"

if [ ! -d "$context_dir" ]; then
  echo "context dir not found: $context_dir (run context.sh init?)" >&2
  exit 2
fi

touch "$index_file"

if ! grep -qF "$start" "$index_file" || ! grep -qF "$end" "$index_file"; then
  echo "index missing markers: $index_file (run context.sh init?)" >&2
  exit 2
fi

tmp="$(mktemp)"
tmp_out="$(mktemp)"
cleanup() { rm -f "$tmp" "$tmp_out"; }
trap cleanup EXIT

{
  echo "$start"
  echo "| File | Purpose |"
  echo "| --- | --- |"

  find "$context_dir" -type f -name "*.md" \
    ! -path "$context_dir/README.md" \
    | LC_ALL=C sort \
    | while read -r f; do
        rel="./${f#$context_dir/}"
        h1="$(awk 'NR==1{ sub(/^#[[:space:]]+/, "", $0); print; exit }' "$f" 2>/dev/null || true)"
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

echo "OK: updated context index in $index_file"
