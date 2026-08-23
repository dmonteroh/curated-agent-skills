#!/usr/bin/env sh
set -eu

# deps-audit wrapper.
#
# Commands:
#   scan   - detect manifests and run best-effort local scans; store raw outputs
#   report - generate a deterministic markdown summary report from detected signals
#
# Safe-by-default:
# - Writes only under docs/_docgen/deps-audit/
# - Never installs tools or modifies dependencies
#
# Expected usage: run inside a real code repo.

cmd="${1:-}"
shift || true

repo_root="${DEPS_REPO_ROOT:-.}"
out_root="${DEPS_OUT_DIR:-$repo_root/docs/_docgen/deps-audit}"
raw_dir="$out_root/raw"

mkdir -p "$raw_dir"

have() { command -v "$1" >/dev/null 2>&1; }

detect() {
  # Print a list of detected ecosystems to stdout and to raw/detected.txt
  detected="$raw_dir/detected.txt"
  : >"$detected"

  add() { echo "$1" | tee -a "$detected" >/dev/null; }

  # Node
  if [ -f "$repo_root/package.json" ] || [ -f "$repo_root/pnpm-lock.yaml" ] || [ -f "$repo_root/yarn.lock" ] || [ -f "$repo_root/package-lock.json" ]; then
    add "node"
  fi

  # Python
  if [ -f "$repo_root/pyproject.toml" ] || [ -f "$repo_root/poetry.lock" ] || [ -f "$repo_root/requirements.txt" ] || [ -f "$repo_root/Pipfile.lock" ]; then
    add "python"
  fi

  # Go
  if [ -f "$repo_root/go.mod" ]; then
    add "go"
  fi

  # Rust
  if [ -f "$repo_root/Cargo.toml" ] || [ -f "$repo_root/Cargo.lock" ]; then
    add "rust"
  fi

  # Java
  if [ -f "$repo_root/pom.xml" ] || ls "$repo_root"/*.gradle >/dev/null 2>&1 || [ -f "$repo_root/build.gradle" ] || [ -f "$repo_root/build.gradle.kts" ]; then
    add "java"
  fi

  # Ruby
  if [ -f "$repo_root/Gemfile" ] || [ -f "$repo_root/Gemfile.lock" ]; then
    add "ruby"
  fi

  cat "$detected"
}

# Record a scan's real exit code to "$raw_dir/$1.exit" so report() can tell
# "tool missing" (no .exit file) apart from "ran, exit 0" and "ran, exit N"
# instead of absorbing every outcome into the same "no output captured" line.
record_exit() {
  echo "$1" >"$raw_dir/$2.exit"
}

run_node() {
  # Prefer lockfile-aware tools if present.
  if have npm && [ -f "$repo_root/package.json" ]; then
    ec=0
    (cd "$repo_root" && npm audit --json) >"$raw_dir/npm-audit.json" 2>"$raw_dir/npm-audit.stderr" || ec=$?
    record_exit "$ec" npm-audit
    (cd "$repo_root" && npm ls --all) >"$raw_dir/npm-ls.txt" 2>"$raw_dir/npm-ls.stderr" || true
  fi

  if have pnpm && [ -f "$repo_root/pnpm-lock.yaml" ]; then
    ec=0
    (cd "$repo_root" && pnpm audit --json) >"$raw_dir/pnpm-audit.json" 2>"$raw_dir/pnpm-audit.stderr" || ec=$?
    record_exit "$ec" pnpm-audit
  fi

  if have yarn && [ -f "$repo_root/yarn.lock" ]; then
    # yarn classic supports "yarn audit --json"; berry has "yarn npm audit".
    ec=0
    (cd "$repo_root" && yarn audit --json) >"$raw_dir/yarn-audit.json" 2>"$raw_dir/yarn-audit.stderr" || ec=$?
    record_exit "$ec" yarn-audit
    ec=0
    (cd "$repo_root" && yarn npm audit --all --json) >"$raw_dir/yarn-npm-audit.json" 2>"$raw_dir/yarn-npm-audit.stderr" || ec=$?
    record_exit "$ec" yarn-npm-audit
  fi
}

run_python() {
  # Best-effort only: pip-audit may not be installed.
  if have pip-audit; then
    ec=0
    (cd "$repo_root" && pip-audit -f json) >"$raw_dir/pip-audit.json" 2>"$raw_dir/pip-audit.stderr" || ec=$?
    record_exit "$ec" pip-audit
  fi
}

run_go() {
  if have govulncheck && [ -f "$repo_root/go.mod" ]; then
    ec=0
    (cd "$repo_root" && govulncheck ./...) >"$raw_dir/govulncheck.txt" 2>"$raw_dir/govulncheck.stderr" || ec=$?
    record_exit "$ec" govulncheck
  fi
}

run_rust() {
  # cargo-audit is a separate tool; run only if available.
  if have cargo-audit && [ -f "$repo_root/Cargo.toml" ]; then
    ec=0
    (cd "$repo_root" && cargo audit -q --json) >"$raw_dir/cargo-audit.json" 2>"$raw_dir/cargo-audit.stderr" || ec=$?
    record_exit "$ec" cargo-audit
  fi
}

scan() {
  echo "== deps-audit scan =="
  echo "repo_root=$repo_root"
  echo "out_root=$out_root"

  detected="$(detect || true)"
  echo "detected: $(echo "$detected" | tr '\n' ' ' | sed 's/[[:space:]]\\+/ /g')"

  echo "$detected" | grep -q "^node$" && run_node || true
  echo "$detected" | grep -q "^python$" && run_python || true
  echo "$detected" | grep -q "^go$" && run_go || true
  echo "$detected" | grep -q "^rust$" && run_rust || true

  echo "OK: wrote raw outputs under $raw_dir"
}

# Emit one status line for a captured scan: ran (exit 0), ran (exit N -
# nonzero can mean findings were reported or the scan failed; the raw
# output and stderr file are the falsifiable check), or not run at all.
scan_status_line() {
  scan_name="$1"
  out_ext="$2"
  suggested="$3"
  exit_file="$raw_dir/$scan_name.exit"
  if [ -f "$exit_file" ]; then
    scan_ec="$(cat "$exit_file")"
    if [ "$scan_ec" = "0" ]; then
      echo "- \`$scan_name\`: ran, exit 0. Raw output: \`docs/_docgen/deps-audit/raw/$scan_name.$out_ext\`"
    else
      echo "- \`$scan_name\`: ran, exit $scan_ec (nonzero can mean findings were reported or the scan failed) - inspect \`docs/_docgen/deps-audit/raw/$scan_name.$out_ext\` and \`$scan_name.stderr\`"
    fi
  else
    echo "- \`$scan_name\` not run (tool missing or no matching lockfile)."
    echo "  - Suggested: \`$suggested\`"
  fi
}

report() {
  scan >/dev/null 2>&1 || true

  report_file="$out_root/REPORT.md"
  detected_file="$raw_dir/detected.txt"

  {
    echo "# Dependency Audit Report"
    echo
    echo "Generated: $(date -u +%F) (UTC)"
    echo
    echo "## Detected ecosystems"
    echo
    if [ -f "$detected_file" ] && [ -s "$detected_file" ]; then
      sed 's/^/- /' "$detected_file"
    else
      echo "- (none detected)"
    fi
    echo
    echo "## Results (best-effort)"
    echo
    echo "This report is generated from local tooling if available. Missing tools are listed below."
    echo

    if grep -q "^node$" "$detected_file" 2>/dev/null; then
      echo "### Node"
      scan_status_line npm-audit json "npm audit --json"
      scan_status_line pnpm-audit json "pnpm audit --json"
      scan_status_line yarn-audit json "yarn audit --json"
      scan_status_line yarn-npm-audit json "yarn npm audit --all --json"
      echo
    fi

    if grep -q "^python$" "$detected_file" 2>/dev/null; then
      echo "### Python"
      scan_status_line pip-audit json "pip-audit -f json"
      echo
    fi

    if grep -q "^go$" "$detected_file" 2>/dev/null; then
      echo "### Go"
      scan_status_line govulncheck txt "govulncheck ./..."
      echo
    fi

    if grep -q "^rust$" "$detected_file" 2>/dev/null; then
      echo "### Rust"
      scan_status_line cargo-audit json "cargo audit --json"
      echo
    fi

    if grep -q "^java$" "$detected_file" 2>/dev/null; then
      echo "### Java"
      echo "- Detected via manifest; no local scanner is wired up for this ecosystem in this skill."
      echo "  - Inspect \`pom.xml\`/\`build.gradle\` manually, or run vendor tooling (for example OWASP Dependency-Check) yourself."
      echo
    fi

    if grep -q "^ruby$" "$detected_file" 2>/dev/null; then
      echo "### Ruby"
      echo "- Detected via manifest; no local scanner is wired up for this ecosystem in this skill."
      echo "  - Inspect \`Gemfile.lock\` manually, or run vendor tooling (for example \`bundler-audit\`) yourself."
      echo
    fi

    echo "## Remediation planning"
    echo
    echo "- Prioritize by severity + exposure + reachability."
    echo "- Prefer minimal, compatible upgrades; avoid broad major bumps unless necessary."
    echo "- Capture remediation work as ordered tasks with effort notes."
    echo "- Flag items that require architectural or security review."
  } >"$report_file"

  echo "OK: wrote $report_file"
}

case "$cmd" in
  scan) scan ;;
  report) report ;;
  ""|-h|--help|help)
    cat <<'EOF'
deps-audit (deps.sh)

Commands:
  scan   - detect manifests and run best-effort local scans; store raw outputs
  report - generate docs/_docgen/deps-audit/REPORT.md

Env overrides:
  DEPS_REPO_ROOT, DEPS_OUT_DIR
EOF
    ;;
  *)
    echo "unknown command: $cmd" >&2
    echo "run: $0 --help" >&2
    exit 2
    ;;
esac
