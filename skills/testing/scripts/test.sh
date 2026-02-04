#!/usr/bin/env sh
set -eu

# testing wrapper.
#
# Commands:
#   plan   - write a minimal testing plan skeleton to docs/_docgen/testing/PLAN.md
#   report - write a deterministic testing report to docs/_docgen/testing/REPORT.md
#
# Safe-by-default:
# - does not run tests
# - writes only under docs/_docgen/testing/
#
# Env:
#   TEST_ROOT=.
#   TEST_OUT_DIR=docs/_docgen/testing

cmd="${1:-}"
shift || true

root="${TEST_ROOT:-.}"
out_dir="${TEST_OUT_DIR:-$root/docs/_docgen/testing}"
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

plan_cmd() {
  plan="$out_dir/PLAN.md"
  {
    echo "# Testing Plan"
    echo
    echo "Generated: $(date -u +%F) (UTC)"
    echo
    echo "## Goals"
    echo
    echo "- ..."
    echo
    echo "## Risks / Critical journeys"
    echo
    echo "- ..."
    echo
    echo "## Proposed test pyramid"
    echo
    echo "- Unit:"
    echo "- Integration/contract:"
    echo "- E2E:"
    echo
    echo "## CI plan"
    echo
    echo "- Smoke suite:"
    echo "- Full suite:"
    echo "- Reporting/artifacts:"
  } >"$plan"
  echo "OK: wrote $plan"
}

report_cmd() {
  report="$out_dir/REPORT.md"
  {
    echo "# Testing Report"
    echo
    echo "Generated: $(date -u +%F) (UTC)"
    echo
    echo "## Repo signals"
    echo
    echo "| Category | Glob | Count |"
    echo "| --- | --- | --- |"
    printf '| %s | %s | %s |\n' "Tests (common)" "*test*.*" "$(count_files '*test*.*')"
    printf '| %s | %s | %s |\n' "Jest" "jest.config.*" "$(count_files 'jest.config.*')"
    printf '| %s | %s | %s |\n' "Pytest" "pytest.ini" "$(count_files 'pytest.ini')"
    printf '| %s | %s | %s |\n' "Go tests" "*_test.go" "$(count_files '*_test.go')"
    echo
    echo "## Next steps"
    echo
    echo "- Choose mode: unit vs automation."
    echo "- Add/adjust tests for the changed behavior."
    echo "- If flakiness exists, quarantine and fix root causes."
    echo "- Convert the plan into tasks in your tracker if needed."
  } >"$report"
  echo "OK: wrote $report"
}

case "$cmd" in
  plan) plan_cmd ;;
  report) report_cmd ;;
  ""|-h|--help|help)
    cat <<'EOF'
testing (test.sh)

Commands:
  plan
  report

Env:
  TEST_ROOT, TEST_OUT_DIR
EOF
    ;;
  *)
    echo "unknown command: $cmd" >&2
    echo "run: $0 --help" >&2
    exit 2
    ;;
esac
