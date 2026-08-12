#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CHECKLIST="$ROOT/scripts/auditing/SKILL_REVIEW_CHECKLIST.md"
PDFTXT="$ROOT/scripts/auditing/resources/agent_skills_pdf.txt"
LOGDIR="$ROOT/scripts/auditing/logs"
BATCH_SIZE=10
SUBAGENT_SANDBOX="${SUBAGENT_SANDBOX:-danger-full-access}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV="$ROOT/.venv"
SKILLS_FILE="$ROOT/scripts/auditing/skills_list.txt"
DRY_RUN=0
NO_INSTALL=0
declare -a REQUESTED_SKILLS=()

mkdir -p "$LOGDIR"

usage() {
  cat <<USAGE
Usage: scripts/auditing/run_parallel_skill_reviews.sh [options]

Options:
  --batch-size N        Number of concurrent skill reviews (default: 10)
  --subagent-sandbox M  Sandbox passed to nested codex exec calls:
                        workspace-write | danger-full-access (default: danger-full-access)
  --skill NAME          Review only this skill (repeatable)
  --skills-file PATH    Read skill names (one per line) from PATH
  --list-skills         Print discovered skills and exit
  --dry-run             Show planned work without invoking codex
  --no-install          Skip installing audit dependencies
  -h, --help            Show this help

Environment:
  PYTHON_BIN            Python interpreter to use (default: python3)
  SUBAGENT_SANDBOX      Nested codex exec sandbox override (same values as --subagent-sandbox)
USAGE
}

SKILLS_FILE_OVERRIDE=""
LIST_ONLY=0
while (( "$#" )); do
  case "$1" in
    --batch-size)
      BATCH_SIZE="${2:-}"
      shift 2
      ;;
    --subagent-sandbox)
      SUBAGENT_SANDBOX="${2:-}"
      shift 2
      ;;
    --skill)
      REQUESTED_SKILLS+=("${2:-}")
      shift 2
      ;;
    --skills-file)
      SKILLS_FILE_OVERRIDE="${2:-}"
      shift 2
      ;;
    --list-skills)
      LIST_ONLY=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-install)
      NO_INSTALL=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! [[ "$BATCH_SIZE" =~ ^[1-9][0-9]*$ ]]; then
  echo "error: --batch-size must be a positive integer (got '$BATCH_SIZE')" >&2
  exit 2
fi

case "$SUBAGENT_SANDBOX" in
  workspace-write|danger-full-access) ;;
  *)
    echo "error: --subagent-sandbox must be one of: workspace-write, danger-full-access (got '$SUBAGENT_SANDBOX')" >&2
    exit 2
    ;;
esac

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "error: $PYTHON_BIN not found" >&2
  exit 1
fi

if [[ ! -d "$VENV" ]]; then
  "$PYTHON_BIN" -m venv "$VENV"
fi

if (( NO_INSTALL == 0 )); then
  "$VENV/bin/python" -m pip install -r "$ROOT/scripts/requirements-audit.txt" >/dev/null
fi

if (( DRY_RUN == 0 )) && ! command -v codex >/dev/null 2>&1; then
  echo "error: codex command not found in PATH" >&2
  exit 1
fi

"$VENV/bin/python" - <<PY >"$SKILLS_FILE"
from pathlib import Path
root = Path("${ROOT}") / "skills"
skills = []
if root.is_dir():
    for p in sorted(root.iterdir()):
        if not p.is_dir():
            continue
        if p.name.startswith('.'):
            continue
        if (p/'SKILL.md').is_file():
            skills.append(p.name)
print('\n'.join(skills))
PY

if [[ -n "$SKILLS_FILE_OVERRIDE" ]]; then
  if [[ ! -f "$SKILLS_FILE_OVERRIDE" ]]; then
    echo "error: --skills-file path not found: $SKILLS_FILE_OVERRIDE" >&2
    exit 1
  fi
  SKILLS_FILE="$SKILLS_FILE_OVERRIDE"
fi

read_skills_file() {
  local file="$1"
  local out=()
  while IFS= read -r line; do
    line="${line%%#*}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -n "$line" ]] && out+=("$line")
  done < "$file"
  printf '%s\n' "${out[@]:-}"
}

declare -a SKILLS=()
if (( ${#REQUESTED_SKILLS[@]} > 0 )); then
  SKILLS=("${REQUESTED_SKILLS[@]}")
else
  mapfile -t SKILLS < <(read_skills_file "$SKILLS_FILE")
fi

if (( LIST_ONLY == 1 )); then
  printf '%s\n' "${SKILLS[@]:-}"
  exit 0
fi

if (( ${#SKILLS[@]} == 0 )); then
  echo "error: no skills selected for review" >&2
  exit 1
fi

for skill in "${SKILLS[@]}"; do
  if [[ ! -f "$ROOT/skills/$skill/SKILL.md" ]]; then
    echo "error: skill not found or missing SKILL.md: $skill" >&2
    exit 1
  fi
done

run_skill() {
  local skill="$1"
  local skill_dir="skills/$skill"
  local log="$LOGDIR/${skill}.log"
  local checklist_rel="scripts/auditing/SKILL_REVIEW_CHECKLIST.md"
  local guidance_rel="scripts/auditing/references/authoring-guidance.md"
  local open_items_rel="scripts/auditing/OPEN_ITEMS.md"
  local pdf_rel="scripts/auditing/resources/agent_skills_pdf.txt"
  local venv_python_rel=".venv/bin/python"
  local prompt

  if (( DRY_RUN == 1 )); then
    echo "[dry-run] would review: $skill"
    return 0
  fi

  # read -d '' rather than "$(cat <<EOF ...)": bash 3.2 (macOS system bash)
  # mis-parses an apostrophe inside a heredoc nested in command substitution.
  IFS= read -r -d '' prompt <<EOF || true
Task: Review ${skill_dir}/SKILL.md against the binding quality bar and bring it to that bar. Apply changes directly.

Read first, in this order:
- ${checklist_rel} - the binding bar. It outranks every other input, including the vendored resource below.
- ${open_items_rel} - calls already settled. Arguing against one of these is wrong, not thorough.
- ${guidance_rel} - depth behind the bar. Read the section you need when a judgment call is not obvious.
- ${skill_dir}/SKILL.md and everything else under ${skill_dir}/.
- ${pdf_rel} - background only, optional.

Scope: only files under ${skill_dir}. Do not edit anything outside it.

This review may subtract. Removing text is a first-class outcome, not a failure to add value.
- Delete without asking: a sentence that restates its own heading; a restatement of the frontmatter description; a second statement of a rule already made elsewhere in the same file; a vacuous heading qualifier such as (Deterministic), (Always), (best results); a workflow step whose only output is "report per the output contract".
- Propose, never execute: removing a whole ## section, a file under references/ or scripts/, or the skill itself. Give the evidence and what would be lost. The operator rules on it.
- A review that deletes forty lines and adds none is successful. So is one that changes nothing.

Differentiation - report it, never act on it:
- Judge whether this skill changes what a frontier model would do unprompted. It earns its cost only with an opinionated house convention, a non-obvious process with real decision points, embedded tooling that makes behavior deterministic, or a correction for something models reliably get wrong.
- Report STRONG or WEAK with one line of evidence. A WEAK verdict is a flag for the operator. Do not delete or rewrite the skill because of it.

Rules:
- Keep the skill independent: it must never require another skill to be installed, and never check for one.
- Do not add brainstorming-gate or multi-agent dependencies.
- Do not modify package manifests or add dependencies (no package.json, lockfiles, pip installs).
- Keep activation cues and trigger tests out of SKILL.md.
- Avoid time-sensitive facts and external network assumptions.
- Structure follows the skill's job. Mandatory: the frontmatter contract, "Use this skill when", "Do not use this skill when". Every other section is earned - do not add one because other skills have it.
- Voice: third person for the frontmatter description and the opening framing; imperative for procedure steps. No personas.
- Write script paths skill-relative (scripts/x.sh), never repo-root style (skills/${skill}/scripts/x.sh), which does not resolve once the skill is installed.
- If splitting references, add references/README.md as an index. Split when a reader does not need the material in line, not because a token count was crossed.
- Measure reference file size with tiktoken (cl100k_base) using ${venv_python_rel}.
- If anything is ambiguous, STOP and output QUESTIONS on a line of its own. Do not guess.

Output, in this order:
- Files changed (or "none")
- Summary of edits, separating what was removed from what was added, with line counts
- REMOVAL PROPOSALS: numbered, each naming the file and section, the evidence, and what would be lost. Write "none" if there are none.
- DIFFERENTIATION: STRONG or DIFFERENTIATION: WEAK, followed by one line of evidence
- Verification run (if any)
- Exactly one final status line, either:
REVIEW_STATUS: NO-CHANGE
or
REVIEW_STATUS: CHANGED
EOF

  (
    cd "$ROOT"
    codex exec --sandbox "$SUBAGENT_SANDBOX" "$prompt"
  ) >"$log" 2>&1 &
  echo "[queued] $skill -> $log"
}

review_status_from_log() {
  local log="$1"
  local verdict
  verdict="$(grep -E '^REVIEW_STATUS: (NO-CHANGE|CHANGED)$' "$log" | tail -n1 | awk -F': ' '{print $2}')" || true
  if [[ "$verdict" == "NO-CHANGE" || "$verdict" == "CHANGED" ]]; then
    printf '%s\n' "$verdict"
    return 0
  fi
  printf 'UNKNOWN\n'
  return 0
}

differentiation_from_log() {
  local log="$1"
  local verdict
  verdict="$(grep -Eo '^DIFFERENTIATION: (STRONG|WEAK)' "$log" | tail -n1 | awk '{print $2}')" || true
  if [[ "$verdict" == "STRONG" || "$verdict" == "WEAK" ]]; then
    printf '%s\n' "$verdict"
    return 0
  fi
  printf 'UNKNOWN\n'
  return 0
}

# Exit 0 when the log carries removal proposals the operator must rule on.
has_removal_proposals() {
  local log="$1"
  awk '
    /^REMOVAL PROPOSALS:/ {
      collecting = 1
      rest = $0
      sub(/^REMOVAL PROPOSALS:[ \t]*/, "", rest)
      if (rest != "") buf = buf " " rest
      next
    }
    collecting && /^(DIFFERENTIATION:|REVIEW_STATUS:|QUESTIONS|Verification run)/ { collecting = 0; next }
    collecting { buf = buf " " $0 }
    END {
      gsub(/[ \t.\-]+/, " ", buf)
      gsub(/^ +| +$/, "", buf)
      if (buf == "" || tolower(buf) == "none") exit 1
      exit 0
    }
  ' "$log"
}

declare -a BATCH_PIDS=()
declare -a BATCH_SKILLS=()
declare -a FAILED_SKILLS=()
declare -a REVIEW_OK_SKILLS=()
declare -a REVIEW_NO_CHANGE_SKILLS=()
declare -a DIFFERENTIATION_WEAK_SKILLS=()
declare -a DIFFERENTIATION_UNKNOWN_SKILLS=()
declare -a REMOVAL_PROPOSAL_SKILLS=()

reap_batch() {
  local i pid rc skill
  for i in "${!BATCH_PIDS[@]}"; do
    pid="${BATCH_PIDS[$i]}"
    skill="${BATCH_SKILLS[$i]}"
    local review_log="$LOGDIR/${skill}.log"
    local review_status differentiation
    rc=0
    if wait "$pid"; then
      if grep -Eq '^QUESTIONS$' "$review_log"; then
        FAILED_SKILLS+=("$skill (blocked: QUESTIONS)")
        echo "[failed] $skill (blocked: QUESTIONS)"
      else
        review_status="$(review_status_from_log "$review_log")"
        differentiation="$(differentiation_from_log "$review_log")"
        if [[ "$review_status" == "NO-CHANGE" ]]; then
          REVIEW_NO_CHANGE_SKILLS+=("$skill")
        fi
        case "$differentiation" in
          WEAK) DIFFERENTIATION_WEAK_SKILLS+=("$skill") ;;
          STRONG) ;;
          *) DIFFERENTIATION_UNKNOWN_SKILLS+=("$skill") ;;
        esac
        if has_removal_proposals "$review_log"; then
          REMOVAL_PROPOSAL_SKILLS+=("$skill")
        fi
        echo "[ok] $skill (status $review_status, differentiation $differentiation)"
        REVIEW_OK_SKILLS+=("$skill")
      fi
    else
      rc=$?
      FAILED_SKILLS+=("$skill (exit $rc)")
      echo "[failed] $skill (exit $rc)"
    fi
  done
  BATCH_PIDS=()
  BATCH_SKILLS=()
}

count=0
for skill in "${SKILLS[@]}"; do
  run_skill "$skill"
  if (( DRY_RUN == 0 )); then
    BATCH_PIDS+=("$!")
    BATCH_SKILLS+=("$skill")
    count=$((count+1))
    if (( count % BATCH_SIZE == 0 )); then
      reap_batch
    fi
  else
    REVIEW_OK_SKILLS+=("$skill")
  fi
done

if (( DRY_RUN == 0 )) && (( ${#BATCH_PIDS[@]} > 0 )); then
  reap_batch
fi

if (( DRY_RUN == 1 )); then
  echo "Dry run complete. Planned ${#SKILLS[@]} skills with batch size ${BATCH_SIZE}."
  exit 0
fi

audit_rc=0
"$VENV/bin/python" "$ROOT/scripts/audit_skills.py" || audit_rc=$?

echo "Completed ${#SKILLS[@]} skills. Logs in $LOGDIR"

# Reported, never failing: these need an operator ruling, not a fix by the runner.
print_operator_decisions() {
  local any=0
  echo
  echo "=== Operator decisions required ==="
  if (( ${#DIFFERENTIATION_WEAK_SKILLS[@]} > 0 )); then
    any=1
    echo "Differentiation flagged WEAK (evidence in each log; nothing was removed):"
    printf '  - %s\n' "${DIFFERENTIATION_WEAK_SKILLS[@]}"
  fi
  if (( ${#REMOVAL_PROPOSAL_SKILLS[@]} > 0 )); then
    any=1
    echo "Removal proposals awaiting a ruling (see REMOVAL PROPOSALS in each log):"
    printf '  - %s\n' "${REMOVAL_PROPOSAL_SKILLS[@]}"
  fi
  if (( ${#DIFFERENTIATION_UNKNOWN_SKILLS[@]} > 0 )); then
    any=1
    echo "No differentiation verdict reported (reviewer did not follow the output contract):"
    printf '  - %s\n' "${DIFFERENTIATION_UNKNOWN_SKILLS[@]}"
  fi
  if (( any == 0 )); then
    echo "None."
  fi
  if (( ${#REVIEW_NO_CHANGE_SKILLS[@]} > 0 )); then
    echo "Already at the bar, unchanged: ${#REVIEW_NO_CHANGE_SKILLS[@]}"
  fi
}
print_operator_decisions

if (( ${#FAILED_SKILLS[@]} > 0 )); then
  echo "Failed skills:"
  printf '  - %s\n' "${FAILED_SKILLS[@]}"
  exit 1
fi

if (( audit_rc != 0 )); then
  exit "$audit_rc"
fi
