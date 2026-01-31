#!/usr/bin/env sh
set -eu

# Safe-by-default performance helper.
#
# Commands:
#   scan   - capture repo signals (languages, manifests, entrypoints) + best-effort hints
#   report - write docs/_docgen/performance/REPORT.md (deterministic)
#
# Intended usage: run inside a real code repo.
#
# Env:
#   PERF_ROOT=.
#   PERF_OUT_DIR=docs/_docgen/performance

cmd="${1:-}"
shift || true

root="${PERF_ROOT:-.}"
out_dir="${PERF_OUT_DIR:-$root/docs/_docgen/performance}"
raw_dir="$out_dir/raw"

mkdir -p "$raw_dir"

have_rg=0
if command -v rg >/dev/null 2>&1; then
  have_rg=1
fi

count_files() {
  pat="$1"
  if [ "$have_rg" -eq 1 ]; then
    rg --files -g "$pat" "$root" | wc -l | tr -d ' '
  else
    find "$root" -type f -name "$pat" 2>/dev/null | wc -l | tr -d ' '
  fi
}

scan_cmd() {
  inv="$raw_dir/inventory.md"
  {
    echo "# Performance Inventory"
    echo
    echo "Generated: $(date -u +%F) (UTC)"
    echo
    echo "## Repo signals"
    echo
    echo "| Category | Glob | Count |"
    echo "| --- | --- | --- |"
    printf '| %s | %s | %s |\n' "Markdown" "*.md" "$(count_files '*.md')"
    printf '| %s | %s | %s |\n' "TypeScript" "*.ts" "$(count_files '*.ts')"
    printf '| %s | %s | %s |\n' "JavaScript" "*.js" "$(count_files '*.js')"
    printf '| %s | %s | %s |\n' "Python" "*.py" "$(count_files '*.py')"
    printf '| %s | %s | %s |\n' "Go" "*.go" "$(count_files '*.go')"
    printf '| %s | %s | %s |\n' "Rust" "*.rs" "$(count_files '*.rs')"
    printf '| %s | %s | %s |\n' "Dockerfile" "Dockerfile" "$(count_files 'Dockerfile')"
    printf '| %s | %s | %s |\n' "Compose" "docker-compose.yml" "$(count_files 'docker-compose.yml')"
    printf '| %s | %s | %s |\n' "Compose" "compose.yml" "$(count_files 'compose.yml')"
    echo
    echo "## Likely entrypoints (if present)"
    echo
    for f in README.md package.json pyproject.toml requirements.txt go.mod Cargo.toml; do
      if [ -f "$root/$f" ]; then
        echo "- $f"
      fi
    done
    echo
    echo "## Suggested next actions"
    echo
    echo "- Define target user journeys/endpoints and SLIs (p95/p99, throughput)."
    echo "- Establish a baseline in a controlled environment."
    echo "- Add profiling/tracing to isolate bottlenecks."
    echo "- Optimize one layer at a time and measure after each change."
  } >"$inv"

  echo "OK: wrote $inv"
}

report_cmd() {
  scan_cmd >/dev/null 2>&1 || true

  report="$out_dir/REPORT.md"
  inv="$raw_dir/inventory.md"

  {
    echo "# Performance Report"
    echo
    echo "Generated: $(date -u +%F) (UTC)"
    echo
    echo "## Inventory"
    echo
    if [ -s "$inv" ]; then
      echo "_See raw inventory: \`docs/_docgen/performance/raw/inventory.md\`_"
    else
      echo "- (no inventory)"
    fi
    echo
    echo "## What to measure first"
    echo
    echo "- Latency: p50/p95/p99 for critical endpoints/journeys"
    echo "- Throughput at steady state"
    echo "- Error rate under load"
    echo "- Resource efficiency (CPU/mem) and cost drivers"
    echo
    echo "## Profiling plan (minimal)"
    echo
    echo "- Backend: CPU + memory profile + slow queries"
    echo "- DB: EXPLAIN plans + index review for top queries"
    echo "- Frontend: Core Web Vitals (LCP/CLS/INP) + bundle sizes"
    echo
    echo "## Guardrails"
    echo
    echo "- Add perf budgets and regression checks where feasible."
    echo "- Add dashboards/alerts for SLOs."
    echo
    echo "## Notes"
    echo
    echo "- This script does not run load tests or profiling automatically."
    echo "- Use it to accelerate planning and to keep a deterministic report artifact."
  } >"$report"

  echo "OK: wrote $report"
}

case "$cmd" in
  scan) scan_cmd ;;
  report) report_cmd ;;
  ""|-h|--help|help)
    cat <<'EOF'
performance (perf.sh)

Commands:
  scan
  report

Env:
  PERF_ROOT, PERF_OUT_DIR
EOF
    ;;
  *)
    echo "unknown command: $cmd" >&2
    echo "run: $0 --help" >&2
    exit 2
    ;;
esac

