#!/usr/bin/env bash
# inventory.sh — deterministic inventory of an agent instruction corpus.
#
# Enumerates the entry file of every item under one or more corpus roots and
# emits one JSON document on stdout: the roots that were searched (found or
# not), and one record per item carrying its path, frontmatter name and
# description, UTC mtime, and line count.
#
# Usage:
#   inventory.sh [-e ENTRY] [-r ROLE] [-H] DIR [DIR ...]
#
#   -e ENTRY  Filename or glob identifying one item's entry file.
#             Default: SKILL.md. Use -e '*.md' for a flat corpus in which
#             every file is itself an item (a standing-rule directory).
#   -r ROLE   Label recorded in the output. Default: item.
#   -H        Also index each item's level-2 (##) headings, so a proposal can
#             name a target section rather than only a file.
#   -h        Print this usage text and exit 0.
#
# Required: bash, jq, find, awk, sort, wc, and either GNU or BSD stat/date.
# No bash-4-only construct is used; only bash 5.2 has actually been exercised.
#
# Exit status: 1 on a usage error or a missing dependency. A root that does not
# exist is NOT an error — it is reported as "found": false with zero items and
# exit 0, because an absent corpus is a real state the caller must be able to
# act on rather than a failure to recover from.
#
# Verify the output:
#   inventory.sh DIR | jq '.roots, (.items | length)'
#   find DIR -name SKILL.md -type f | wc -l      # must equal the item count
#   inventory.sh DIR | jq -e '.items[] | select(.mtime == "")' ; echo $?
#   # exit 4 from the last command means every item carries an mtime.

set -euo pipefail

ENTRY="SKILL.md"
ROLE="item"
WANT_HEADINGS=0

# Print the header comment block, so usage text cannot drift from the header.
usage() {
  awk 'NR == 1 { next } /^#/ { sub(/^# ?/, ""); print; next } { exit }' "$0"
}

while getopts ":e:r:Hh" opt; do
  case "$opt" in
    e) ENTRY="$OPTARG" ;;
    r) ROLE="$OPTARG" ;;
    H) WANT_HEADINGS=1 ;;
    h) usage; exit 0 ;;
    :) echo "inventory.sh: -$OPTARG requires an argument" >&2; exit 1 ;;
    *) echo "inventory.sh: unknown option -$OPTARG" >&2; exit 1 ;;
  esac
done
shift $((OPTIND - 1))

if [ "$#" -eq 0 ]; then
  echo "inventory.sh: at least one corpus root is required" >&2
  usage >&2
  exit 1
fi

for dep in jq find awk sort wc; do
  command -v "$dep" >/dev/null 2>&1 || {
    echo "inventory.sh: required command not found: $dep" >&2
    exit 1
  }
done

tmpdir=$(mktemp -d)
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

# Read one single-line frontmatter field. Quoted and unquoted values both work,
# and the surrounding quotes are stripped. This is a line reader, not a YAML
# parser: multi-line blocks (| or >) and nested keys report as empty rather
# than as wrong, and escape sequences inside a quoted value are passed through
# verbatim rather than decoded.
extract_field() {
  awk -v f="$2" '
    BEGIN { fm = 0 }
    /^---[[:space:]]*$/ { fm++; if (fm >= 2) exit; next }
    fm == 1 {
      n = length(f) + 2
      if (substr($0, 1, n) == f ": ") {
        val = substr($0, n + 1)
        sub(/[[:space:]]+$/, "", val)
        sub(/^["'"'"']/, "", val)
        sub(/["'"'"']$/, "", val)
        print val
        exit
      }
    }
  ' "$1"
}

# UTC ISO-8601 mtime. GNU stat/date first, BSD second; empty if neither works.
get_mtime() {
  local secs
  secs=$(stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null) || return 0
  date -u -d "@$secs" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null ||
    date -u -r "$secs" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null ||
    true
}

item_count=0
root_count=0

for root in "$@"; do
  found=false
  count=0
  if [ -d "$root" ]; then
    found=true
    while IFS= read -r file; do
      [ -n "$file" ] || continue
      name=$(extract_field "$file" name)
      desc=$(extract_field "$file" description)
      mtime=$(get_mtime "$file")
      lines=$(wc -l < "$file" | tr -d '[:space:]')
      if [ "$WANT_HEADINGS" -eq 1 ]; then
        headings=$(awk '/^## /{ sub(/^## /, ""); print }' "$file" | jq -R . | jq -s '.')
      else
        headings='null'
      fi
      jq -n \
        --arg root "$root" \
        --arg path "$file" \
        --arg name "$name" \
        --arg description "$desc" \
        --arg mtime "$mtime" \
        --argjson lines "${lines:-0}" \
        --argjson headings "$headings" \
        '{root: $root, path: $path, name: $name, description: $description,
          mtime: $mtime, lines: $lines}
         + (if $headings == null then {} else {headings: $headings} end)' \
        > "$tmpdir/item-$item_count.json"
      item_count=$((item_count + 1))
      count=$((count + 1))
    done < <(find "$root" -name "$ENTRY" -type f 2>/dev/null | LC_ALL=C sort)
  fi
  jq -n --arg path "$root" --argjson found "$found" --argjson count "$count" \
    '{path: $path, found: $found, count: $count}' \
    > "$tmpdir/root-$root_count.json"
  root_count=$((root_count + 1))
done

roots_json=$(jq -s '.' "$tmpdir"/root-*.json)
if [ "$item_count" -eq 0 ]; then
  items_json='[]'
else
  items_json=$(jq -s '.' "$tmpdir"/item-*.json)
fi

jq -n \
  --arg role "$ROLE" \
  --arg entry "$ENTRY" \
  --arg generated_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson roots "$roots_json" \
  --argjson items "$items_json" \
  '{role: $role, entry: $entry, generated_at: $generated_at,
    roots: $roots, total: ($items | length), items: $items}'
