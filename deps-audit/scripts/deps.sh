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

run_node() {
  # Prefer lockfile-aware tools if present.
  if have npm && [ -f "$repo_root/package.json" ]; then
    (cd "$repo_root" && npm audit --json) >"$raw_dir/npm-audit.json" 2>"$raw_dir/npm-audit.stderr" || true
    (cd "$repo_root" && npm ls --all) >"$raw_dir/npm-ls.txt" 2>"$raw_dir/npm-ls.stderr" || true
  fi

  if have pnpm && [ -f "$repo_root/pnpm-lock.yaml" ]; then
    (cd "$repo_root" && pnpm audit --json) >"$raw_dir/pnpm-audit.json" 2>"$raw_dir/pnpm-audit.stderr" || true
  fi

  if have yarn && [ -f "$repo_root/yarn.lock" ]; then
    # yarn classic supports "yarn audit --json"; berry has "yarn npm audit".
    (cd "$repo_root" && yarn audit --json) >"$raw_dir/yarn-audit.json" 2>"$raw_dir/yarn-audit.stderr" || true
    (cd "$repo_root" && yarn npm audit --all --json) >"$raw_dir/yarn-npm-audit.json" 2>"$raw_dir/yarn-npm-audit.stderr" || true
  fi
}

run_python() {
  # Best-effort only: pip-audit may not be installed.
  if have pip-audit; then
    (cd "$repo_root" && pip-audit -f json) >"$raw_dir/pip-audit.json" 2>"$raw_dir/pip-audit.stderr" || true
  fi
}

run_go() {
  if have govulncheck && [ -f "$repo_root/go.mod" ]; then
    (cd "$repo_root" && govulncheck ./...) >"$raw_dir/govulncheck.txt" 2>"$raw_dir/govulncheck.stderr" || true
  fi
}

run_rust() {
  # cargo-audit is a separate tool; run only if available.
  if have cargo-audit && [ -f "$repo_root/Cargo.toml" ]; then
    (cd "$repo_root" && cargo audit -q --json) >"$raw_dir/cargo-audit.json" 2>"$raw_dir/cargo-audit.stderr" || true
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
      if [ -s "$raw_dir/npm-audit.json" ] || [ -s "$raw_dir/pnpm-audit.json" ] || [ -s "$raw_dir/yarn-audit.json" ] || [ -s "$raw_dir/yarn-npm-audit.json" ]; then
        echo "- Raw outputs: \`docs/_docgen/deps-audit/raw/*audit*.json\`"
      else
        echo "- No audit output captured. Ensure a package manager is installed and lockfiles exist."
        echo "  - Suggested: \`npm audit --json\` or \`pnpm audit --json\`"
      fi
      echo
    fi

    if grep -q "^python$" "$detected_file" 2>/dev/null; then
      echo "### Python"
      if [ -s "$raw_dir/pip-audit.json" ]; then
        echo "- Raw outputs: \`docs/_docgen/deps-audit/raw/pip-audit.json\`"
      else
        echo "- pip-audit not run (tool may be missing)."
        echo "  - Suggested: install \`pip-audit\`, then run \`pip-audit -f json\`."
      fi
      echo
    fi

    if grep -q "^go$" "$detected_file" 2>/dev/null; then
      echo "### Go"
      if [ -s "$raw_dir/govulncheck.txt" ]; then
        echo "- Raw outputs: \`docs/_docgen/deps-audit/raw/govulncheck.txt\`"
      else
        echo "- govulncheck not run (tool may be missing)."
        echo "  - Suggested: install \`govulncheck\`, then run \`govulncheck ./...\`."
      fi
      echo
    fi

    if grep -q "^rust$" "$detected_file" 2>/dev/null; then
      echo "### Rust"
      if [ -s "$raw_dir/cargo-audit.json" ]; then
        echo "- Raw outputs: \`docs/_docgen/deps-audit/raw/cargo-audit.json\`"
      else
        echo "- cargo-audit not run (tool may be missing)."
        echo "  - Suggested: install \`cargo-audit\`, then run \`cargo audit --json\`."
      fi
      echo
    fi

    echo "## Remediation planning"
    echo
    echo "- Prioritize by severity + exposure + reachability."
    echo "- Prefer minimal, compatible upgrades; avoid broad major bumps unless necessary."
    echo "- Convert work into tasks/tracks via \`tracks-conductor-protocol\` if this will be executed."
    echo "- If remediation requires major architectural changes, record an ADR via \`adr-madr-system\`."
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

