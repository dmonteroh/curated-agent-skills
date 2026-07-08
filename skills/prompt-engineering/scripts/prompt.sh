#!/usr/bin/env sh
set -eu

# prompt-engineering wrapper.
#
# Commands:
#   scaffold  - create a prompt file under prompts/ (safe-by-default)
#   lint      - lightweight prompt lint (checks for basic structure)
#   assets    - list bundled assets/references
#   optimize  - run optimize-prompt.py (stdlib-only; demo flow by default)
#
# Intended usage: run inside a real project repo OR inside this skill folder.
#
# Env:
#   PROMPT_DIR=prompts

cmd="${1:-}"
shift || true

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
skill_root="$(CDPATH= cd -- "$script_dir/.." && pwd)"

prompt_dir="${PROMPT_DIR:-prompts}"

slugify() {
  printf "%s" "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | tr ' _' '--' \
    | sed -E 's/[^a-z0-9-]+/-/g; s/-+/-/g; s/^-//; s/-$//'
}

scaffold() {
  title="${1:-}"
  if [ -z "$title" ]; then
    echo "usage: $0 scaffold \"Prompt title\"" >&2
    exit 2
  fi

  mkdir -p "$prompt_dir"
  slug="$(slugify "$title")"
  file="$prompt_dir/$slug.md"
  if [ -e "$file" ]; then
    echo "refusing to overwrite: $file" >&2
    exit 1
  fi

  cat >"$file" <<EOF
# $title

## Purpose

<what is this prompt for?>

## Target model(s)

<model + generation; reasoning/effort setting if applicable>

## Prompt (copy/paste)

\`\`\`
You are <role>.

## Task
<what the model must do>

## Constraints
- <rule>

## Output format
<omit if enforced by a schema / structured outputs>
\`\`\`

## Evaluation

- Success criteria:
  - ...
- Known failure modes:
  - ...
EOF

  echo "OK: created $file"
}

lint() {
  file="${1:-}"
  if [ -z "$file" ] || [ ! -f "$file" ]; then
    echo "usage: $0 lint path/to/prompt.md" >&2
    exit 2
  fi

  # Minimal lint: ensure a copy/paste block exists and required headings exist.
  missing=0
  for h in "## Purpose" "## Prompt (copy/paste)" "## Evaluation"; do
    grep -qF -- "$h" "$file" || { echo "missing heading: $h" >&2; missing=1; }
  done

  # Require at least one fenced code block.
  grep -qE '^[`]{3}' "$file" || { echo "missing fenced code block for prompt text" >&2; missing=1; }

  # Non-fatal: emphasis inflation (MUST/NEVER/CRITICAL/ALWAYS on routine guidance
  # overtriggers on current literal-following models; reserve for true invariants).
  emphasis_count="$(grep -oE '\b(CRITICAL|MUST|NEVER|ALWAYS)\b' "$file" | wc -l | tr -d ' ')"
  if [ "$emphasis_count" -gt 3 ]; then
    echo "warning: $emphasis_count uses of CRITICAL/MUST/NEVER/ALWAYS — reserve emphasis for true invariants" >&2
  fi

  if [ "$missing" -ne 0 ]; then
    echo "FAILED: lint issues in $file" >&2
    exit 1
  fi

  echo "OK: lint passed ($file)"
}

assets() {
  echo "== assets =="
  find "$skill_root/assets" -type f 2>/dev/null || echo "(none)"
  echo
  echo "== references =="
  find "$skill_root/references" -type f 2>/dev/null || echo "(none)"
  echo
  echo "== scripts =="
  find "$skill_root/scripts" -type f 2>/dev/null || true
}

optimize() {
  if [ ! -f "$skill_root/scripts/optimize-prompt.py" ]; then
    echo "missing optimizer: $skill_root/scripts/optimize-prompt.py" >&2
    exit 2
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found; cannot run optimize-prompt.py" >&2
    exit 2
  fi
  echo "Running optimizer (stdlib-only demo; wire a real LLM client for actual use)..."
  python3 "$skill_root/scripts/optimize-prompt.py" "$@"
}

case "$cmd" in
  scaffold) scaffold "$@" ;;
  lint) lint "$@" ;;
  assets) assets ;;
  optimize) optimize "$@" ;;
  ""|-h|--help|help)
    cat <<'EOF'
prompt-engineering (prompt.sh)

Commands:
  scaffold "Prompt title"
  lint path/to/prompt.md
  assets
  optimize [args...]

Env:
  PROMPT_DIR=prompts
EOF
    ;;
  *)
    echo "unknown command: $cmd" >&2
    echo "run: $0 --help" >&2
    exit 2
    ;;
esac

