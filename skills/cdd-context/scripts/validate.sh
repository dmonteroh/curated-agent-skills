#!/usr/bin/env sh
set -eu

# Validate minimal CDD context artifacts exist and have basic structure.

context_dir="${CONTEXT_DIR:-docs/context}"
index_file="${CONTEXT_INDEX:-$context_dir/README.md}"

require_file() {
  [ -f "$1" ] || { echo "missing required file: $1" >&2; exit 1; }
}

require_heading() {
  file="$1"
  heading="$2"
  grep -qF -- "$heading" "$file" || { echo "missing heading '$heading' in $file" >&2; exit 1; }
}

require_file "$context_dir/product.md"
require_file "$context_dir/tech-stack.md"
require_file "$context_dir/workflow.md"
require_file "$index_file"

require_heading "$context_dir/product.md" "## One-liner"
require_heading "$context_dir/tech-stack.md" "## Overview"
require_heading "$context_dir/workflow.md" "## How we work"

start="<!-- CONTEXT-INDEX:START -->"
end="<!-- CONTEXT-INDEX:END -->"
grep -qF "$start" "$index_file" || { echo "missing index marker in $index_file: $start" >&2; exit 1; }
grep -qF "$end" "$index_file" || { echo "missing index marker in $index_file: $end" >&2; exit 1; }

echo "OK: context validation passed ($context_dir)"

