#!/usr/bin/env sh
set -eu

# Safe-by-default code review helper.
#
# Commands:
#   diff   - print a diff summary (best-effort, prefers git)
#   scan   - scan changed files (or whole repo) for common risky patterns
#   report - generate docs/_docgen/code-review/REPORT.md from scan outputs
#
# Env:
#   REVIEW_ROOT=.
#   REVIEW_OUT_DIR=docs/_docgen/code-review
#   REVIEW_BASE= (git base ref, optional; defaults to merge-base with HEAD if possible)
#   REVIEW_HEAD=HEAD

cmd="${1:-}"
shift || true

root="${REVIEW_ROOT:-.}"
out_dir="${REVIEW_OUT_DIR:-$root/docs/_docgen/code-review}"
raw_dir="$out_dir/raw"

mkdir -p "$raw_dir"

have() { command -v "$1" >/dev/null 2>&1; }

git_changed_files() {
  # Try to compute changed files vs a base ref.
  base="${REVIEW_BASE:-}"
  head="${REVIEW_HEAD:-HEAD}"

  if ! have git || [ ! -d "$root/.git" ]; then
    return 1
  fi

  if [ -z "$base" ]; then
    # Prefer upstream branch if available; fallback to HEAD~1.
    base="$(git -C "$root" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
    if [ -n "$base" ]; then
      mb="$(git -C "$root" merge-base "$base" "$head" 2>/dev/null || true)"
      [ -n "$mb" ] && base="$mb"
    else
      base="$(git -C "$root" rev-parse "$head~1" 2>/dev/null || true)"
    fi
  fi

  [ -n "$base" ] || return 1
  git -C "$root" diff --name-only "$base" "$head"
}

diff_cmd() {
  if have git && [ -d "$root/.git" ]; then
    base="${REVIEW_BASE:-}"
    head="${REVIEW_HEAD:-HEAD}"
    if [ -z "$base" ]; then
      base="$(git -C "$root" rev-parse "$head~1" 2>/dev/null || true)"
    fi
    echo "== git diffstat =="
    git -C "$root" diff --stat "${base:-$head~1}" "$head" || true
    echo
    echo "== changed files =="
    git_changed_files || true
  else
    echo "git not detected; set REVIEW_ROOT and provide your diff context manually." >&2
    exit 2
  fi
}

scan_cmd() {
  echo "== code-review scan =="
  echo "root=$root"
  echo "out_dir=$out_dir"

  files="$raw_dir/changed_files.txt"
  : >"$files"

  if git_changed_files >"$files" 2>/dev/null; then
    echo "detected changed files via git"
  else
    # Fallback: scan the whole repo.
    echo "no git diff context; scanning all files (fallback)" >&2
    if have rg; then
      rg --files "$root" >"$files"
    else
      find "$root" -type f ! -path '*/.git/*' >"$files"
    fi
  fi

  # Patterns are heuristics: they are "review pointers", not definitive findings.
  patterns="$raw_dir/pattern_hits.txt"
  : >"$patterns"

  if have rg; then
    rg -n --no-heading \
      -e "TODO|FIXME|HACK|XXX" \
      -e "\\beval\\(" \
      -e "\\bexec\\(" \
      -e "dangerouslySetInnerHTML" \
      -e "\\binnerHTML\\b" \
      -e "subprocess\\..*shell=True" \
      -e "\\bos\\.system\\(" \
      -e "child_process\\.exec\\(" \
      -e "yaml\\.load\\(" \
      -e "pickle\\.loads\\(" \
      -e "(AKIA[0-9A-Z]{16})" \
      -e "(xox[baprs]-[0-9A-Za-z-]{10,})" \
      -S --files-from "$files" "$root" >"$patterns" 2>/dev/null || true
  else
    # Minimal fallback: only TODO/FIXME.
    while read -r f; do
      [ -f "$f" ] || continue
      grep -nE "TODO|FIXME|HACK|XXX" "$f" 2>/dev/null | sed "s|^|$f:|" >>"$patterns" || true
    done <"$files"
  fi

  echo "OK: wrote $files"
  echo "OK: wrote $patterns"
}

report_cmd() {
  scan_cmd >/dev/null 2>&1 || true

  report="$out_dir/REPORT.md"
  files="$raw_dir/changed_files.txt"
  hits="$raw_dir/pattern_hits.txt"

  {
    echo "# Code Review Scan Report"
    echo
    echo "Generated: $(date -u +%F) (UTC)"
    echo
    echo "## Changed files"
    echo
    if [ -s "$files" ]; then
      sed 's/^/- /' "$files" | head -n 200
      if [ "$(wc -l <"$files" | tr -d ' ')" -gt 200 ]; then
        echo "- (truncated)"
      fi
    else
      echo "- (none detected)"
    fi
    echo
    echo "## Pattern hits (review pointers)"
    echo
    echo "These are heuristics to guide review focus, not definitive vulnerabilities."
    echo
    if [ -s "$hits" ]; then
      echo '```'
      head -n 200 "$hits"
      if [ "$(wc -l <"$hits" | tr -d ' ')" -gt 200 ]; then
        echo "(truncated)"
      fi
      echo '```'
    else
      echo "- (no hits)"
    fi
    echo
    echo "## Next steps"
    echo
    echo "- Do a manual review using the mode checklists in code-review/references/checklists.md."
    echo "- Write findings using code-review/references/output-format.md."
  } >"$report"

  echo "OK: wrote $report"
}

case "$cmd" in
  diff) diff_cmd ;;
  scan) scan_cmd ;;
  report) report_cmd ;;
  ""|-h|--help|help)
    cat <<'EOF'
code-review (review.sh)

Commands:
  diff
  scan
  report

Env:
  REVIEW_ROOT, REVIEW_OUT_DIR, REVIEW_BASE, REVIEW_HEAD
EOF
    ;;
  *)
    echo "unknown command: $cmd" >&2
    echo "run: $0 --help" >&2
    exit 2
    ;;
esac

