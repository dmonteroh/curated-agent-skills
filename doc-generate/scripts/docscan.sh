#!/usr/bin/env sh
set -eu

# Lightweight repo scan to accelerate documentation planning.
# Produces docs/_docgen/inventory.md and prints a short summary to stdout.
#
# Safe-by-default: only reads the repo and writes under docs/_docgen/.

out_dir="${DOCSCAN_OUT_DIR:-docs/_docgen}"
out_file="$out_dir/inventory.md"

mkdir -p "$out_dir"

have_rg=0
if command -v rg >/dev/null 2>&1; then
  have_rg=1
fi

count_files() {
  pat="$1"
  if [ "$have_rg" -eq 1 ]; then
    rg --files -g "$pat" . | wc -l | tr -d ' '
  else
    find . -type f -name "$pat" 2>/dev/null | wc -l | tr -d ' '
  fi
}

detect() {
  label="$1"
  pat="$2"
  c="$(count_files "$pat")"
  printf '| %s | %s | %s |\n' "$label" "$pat" "$c"
}

{
  echo "# Documentation Inventory"
  echo
  echo "Generated: $(date -u +%F) (UTC)"
  echo
  echo "## Signals"
  echo
  echo "| Category | Glob | Count |"
  echo "| --- | --- | --- |"
  detect "Markdown" "*.md"
  detect "TypeScript" "*.ts"
  detect "JavaScript" "*.js"
  detect "Python" "*.py"
  detect "Go" "*.go"
  detect "Java" "*.java"
  detect "Kotlin" "*.kt"
  detect "Rust" "*.rs"
  detect "Terraform" "*.tf"
  detect "OpenAPI/Swagger" "*openapi*.yml"
  detect "OpenAPI/Swagger" "*openapi*.yaml"
  detect "Docker" "Dockerfile"
  detect "Compose" "docker-compose.yml"
  detect "Compose" "compose.yml"
  echo
  echo "## Likely doc entrypoints (if present)"
  echo
  for f in README.md docs/README.md docs/index.md docs/INDEX.md; do
    if [ -f "$f" ]; then
      echo "- $f"
    fi
  done
  echo
  echo "## Next steps (suggested)"
  echo
  echo "- Choose audiences + minimum doc set (start with docs/README.md + architecture overview)."
  echo "- Create a managed docs index block in docs/README.md and maintain it with update_docs_index.sh."
  echo "- Link docs to ADRs (decisions) and to work artifacts (specs/tracks/tasks) for traceability."
} >"$out_file"

echo "OK: wrote $out_file"
