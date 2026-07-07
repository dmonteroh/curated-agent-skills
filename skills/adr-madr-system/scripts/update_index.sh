#!/usr/bin/env sh
set -eu

# Rebuild the ADR index table inside a managed block:
# <!-- ADR-INDEX:START --> ... <!-- ADR-INDEX:END -->
#
# This keeps multi-agent changes deterministic and avoids hand-editing table rows.

adr_dir="${ADR_DIR:-docs/adr}"
index_file="${ADR_INDEX:-$adr_dir/README.md}"

if [ ! -d "$adr_dir" ]; then
  echo "adr dir not found: $adr_dir" >&2
  exit 2
fi

mkdir -p "$(dirname "$index_file")"
touch "$index_file"

start_marker="<!-- ADR-INDEX:START -->"
end_marker="<!-- ADR-INDEX:END -->"

tmp_rows="$(mktemp)"
tmp_out="$(mktemp)"
tmp_tags="$(mktemp)"

cleanup() {
  rm -f "$tmp_rows" "${tmp_rows}.sorted" "$tmp_out" "$tmp_tags"
}
trap cleanup EXIT

# Preserve hand-maintained Tags cells from the existing index (keyed by ADR id),
# so a rebuild does not wipe them.
if [ -f "$index_file" ]; then
  awk -F'|' '
    /^\| ADR-[0-9][0-9][0-9][0-9] \|/ {
      id=$2; tags=$(NF-1)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", id)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", tags)
      if (tags != "") print id "\t" tags
    }
  ' "$index_file" >"$tmp_tags"
fi

extract_field() {
  # $1 = file, $2 = heading (e.g. '## Status')
  # prints first non-empty line after heading, trimmed
  awk -v heading="$2" '
    $0 == heading {found=1; next}
    found {
      if ($0 ~ /^## /) { exit }
      if ($0 ~ /^[[:space:]]*$/) { next }
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
      print $0
      exit
    }
  ' "$1"
}

extract_deciders() {
  # prints "- @a\n- @b" as "@a @b"
  awk '
    $0 == "## Deciders" {found=1; next}
    found {
      if ($0 ~ /^## /) { exit }
      if ($0 ~ /^- /) {
        sub(/^- /, "", $0)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
        deciders = deciders (deciders ? " " : "") $0
      }
    }
    END { print deciders }
  ' "$1"
}

extract_supersedes() {
  # prints the first ADR id listed under "## Supersedes" (if any), e.g. "ADR-0002"
  awk '
    $0 == "## Supersedes" {found=1; next}
    found {
      if ($0 ~ /^## /) { exit }
      if ($0 ~ /^- ADR-[0-9][0-9][0-9][0-9]/) {
        sub(/^- /, "", $0)
        split($0, a, /[[:space:]]/)
        print a[1]
        exit
      }
    }
  ' "$1"
}

for f in "$adr_dir"/ADR-[0-9][0-9][0-9][0-9]-*.md "$adr_dir"/ADR-[0-9][0-9][0-9][0-9].md; do
  [ -f "$f" ] || continue

  # Expect a header like "# ADR-0001: Title" — usually line 1, but tolerate an
  # optional YAML frontmatter block above it (e.g. ADR-0017).
  header="$(awk '
    NR==1 && $0=="---" { in_fm=1; next }
    in_fm && $0=="---" { in_fm=0; next }
    in_fm { next }
    /^# ADR-[0-9][0-9][0-9][0-9]:/ { print; exit }
    /^#[[:space:]]/ { exit }
  ' "$f")"
  id="$(printf "%s" "$header" | sed -n 's/^# \(ADR-[0-9][0-9][0-9][0-9]\):.*/\1/p')"
  title="$(printf "%s" "$header" | sed -n 's/^# ADR-[0-9][0-9][0-9][0-9]:[[:space:]]*//p')"

  if [ -z "$id" ] || [ -z "$title" ]; then
    echo "skip (bad header): $f" >&2
    continue
  fi

  status="$(extract_field "$f" "## Status")"
  date="$(extract_field "$f" "## Date")"
  deciders="$(extract_deciders "$f")"
  supersedes="$(extract_supersedes "$f")"

  rel="./$(basename "$f")"
  tags="$(awk -F'\t' -v id="$id" '$1==id{print $2; exit}' "$tmp_tags")"

  printf '| %s | %s | %s | %s | %s | %s | %s | %s |\n' \
    "$id" "$title" "${status:-}" "${date:-}" "${deciders:-}" "$rel" "${supersedes:-}" "${tags:-}" >>"$tmp_rows"
done

# Sort by ADR number to keep stable ordering.
sort -t '|' -k2.6,2.9 "$tmp_rows" >"${tmp_rows}.sorted" 2>/dev/null || cp "$tmp_rows" "${tmp_rows}.sorted"

{
  echo "$start_marker"
  echo "| ID | Title | Status | Date | Deciders | Links | Supersedes | Tags |"
  echo "| --- | --- | --- | --- | --- | --- | --- | --- |"
  cat "${tmp_rows}.sorted"
  echo "$end_marker"
} >"$tmp_out"

# If the file already has a managed block, replace it. Otherwise, append a managed block at the end.
if grep -qF "$start_marker" "$index_file" && grep -qF "$end_marker" "$index_file"; then
  awk -v start="$start_marker" -v end="$end_marker" -v block="$tmp_out" '
    BEGIN {
      while ((getline line < block) > 0) { newblock = newblock line "\n" }
      close(block)
    }
    $0 == start { printing=1; printf "%s", newblock; next }
    printing && $0 == end { printing=0; next }
    !printing { print }
  ' "$index_file" >"${index_file}.tmp"
  mv "${index_file}.tmp" "$index_file"
else
  printf '\n%s\n' "$(cat "$tmp_out")" >>"$index_file"
fi

echo "OK: updated index block in $index_file"
