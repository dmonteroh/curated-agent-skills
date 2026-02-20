#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CHECKLIST="$ROOT/scripts/auditing/SKILL_REVIEW_CHECKLIST.md"
PDFTXT="$ROOT/scripts/auditing/resources/agent_skills_pdf.txt"
TRIGGER_CASES_DIR="$ROOT/scripts/auditing/trigger-cases"
LOGDIR="$ROOT/scripts/auditing/logs"
BATCH_SIZE=10
SUBAGENT_SANDBOX="${SUBAGENT_SANDBOX:-danger-full-access}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV="$ROOT/.venv"
SKILLS_FILE="$ROOT/scripts/auditing/skills_list.txt"
DRY_RUN=0
NO_INSTALL=0
AUDIT_AFTER=0
RUN_TRIGGER_TESTS=1
FAIL_ON_MISSING_TRIGGER_CASES=1
AUTO_GENERATE_TRIGGER_CASES=1
declare -a REQUESTED_SKILLS=()

mkdir -p "$LOGDIR"
mkdir -p "$TRIGGER_CASES_DIR"

usage() {
  cat <<USAGE
Usage: scripts/auditing/run_parallel_skill_reviews.sh [options]

Options:
  --batch-size N        Number of concurrent skill reviews (default: 10)
  --subagent-sandbox M  Sandbox passed to nested codex exec calls:
                        workspace-write | danger-full-access (default: danger-full-access)
  --skill NAME          Review only this skill (repeatable)
  --skills-file PATH    Read skill names (one per line) from PATH
  --trigger-cases-dir PATH
                        Directory containing per-skill trigger files (<skill>.md)
  --list-skills         Print discovered skills and exit
  --dry-run             Show planned work without invoking codex
  --no-install          Skip installing audit dependencies
  --audit-after         Run scripts/audit_skills.py after all subagent runs
  --no-trigger-tests    Skip trigger test subagent phase
  --no-generate-trigger-cases
                        Do not auto-create missing trigger-cases files
  --fail-on-missing-trigger-cases
                        Fail run if a skill has no trigger-cases file
  --allow-missing-trigger-cases
                        Allow missing trigger-cases files without failing
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
    --trigger-cases-dir)
      TRIGGER_CASES_DIR="${2:-}"
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
    --audit-after)
      AUDIT_AFTER=1
      shift
      ;;
    --no-trigger-tests)
      RUN_TRIGGER_TESTS=0
      shift
      ;;
    --no-generate-trigger-cases)
      AUTO_GENERATE_TRIGGER_CASES=0
      shift
      ;;
    --fail-on-missing-trigger-cases)
      FAIL_ON_MISSING_TRIGGER_CASES=1
      shift
      ;;
    --allow-missing-trigger-cases)
      FAIL_ON_MISSING_TRIGGER_CASES=0
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

mkdir -p "$TRIGGER_CASES_DIR"

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
  local pdf_rel="scripts/auditing/resources/agent_skills_pdf.txt"
  local venv_python_rel=".venv/bin/python"

  if (( DRY_RUN == 1 )); then
    echo "[dry-run] would review: $skill"
    return 0
  fi

  (
    cd "$ROOT"
    codex exec --sandbox "$SUBAGENT_SANDBOX" "Task: Evaluate ${skill_dir}/SKILL.md against ${checklist_rel} and update it (and any files under ${skill_dir}/ if needed) to fully comply. Apply changes directly.\nScope: Only touch files under ${skill_dir}. You may read ${checklist_rel} and ${pdf_rel}. Do not edit files outside ${skill_dir}.\nRules:\n- Keep the skill independent; do not require other skills to be installed.\n- Do not add brainstorming-gate or multi-agent dependencies.\n- Do not modify package manifests or add dependencies (no package.json, lockfiles, pip installs).\n- Do not delete or prune reference files. Splitting oversized references is required; removal is not allowed.\n- Keep activation examples out of SKILL.md: do not add Trigger phrases or Trigger test sections to the skill file.\n- If anything is ambiguous, STOP and output QUESTIONS (do not guess).\n- Avoid time-sensitive facts or external network assumptions.\n- If splitting references, create references/README.md as an index.\n- Measure reference file size using tiktoken (cl100k_base). Use the existing venv: ${venv_python_rel}. If a single reference exceeds ~1200 tokens or is clearly multi-topic, split it and add/update references/README.md.\nOutput:\n- Files changed\n- Summary of edits\n- Verification run (if any)"
  ) >"$log" 2>&1 &
  echo "[queued] $skill -> $log"
}

run_trigger_test() {
  local skill="$1"
  local trigger_file="${TRIGGER_CASES_DIR}/${skill}.md"
  local log="$LOGDIR/${skill}.trigger-test.log"
  local skill_file="$ROOT/skills/$skill/SKILL.md"
  local skill_file_rel="skills/$skill/SKILL.md"
  local trigger_file_rel
  local skill_text trigger_text prompt
  trigger_file_rel="${trigger_file#"$ROOT"/}"

  if (( DRY_RUN == 1 )); then
    if [[ -f "$trigger_file" ]]; then
      echo "[dry-run] would trigger-test: $skill using $trigger_file"
    else
      echo "[dry-run] would trigger-test: $skill (after trigger-cases generation)"
    fi
    return 0
  fi

  if [[ ! -f "$trigger_file" ]]; then
    if (( FAIL_ON_MISSING_TRIGGER_CASES == 1 )); then
      echo "[failed] $skill trigger test: missing $trigger_file"
      TRIGGER_TEST_FAILED_SKILLS+=("$skill (missing trigger cases)")
    else
      echo "[skipped] $skill trigger test: missing $trigger_file"
      TRIGGER_TEST_SKIPPED_SKILLS+=("$skill")
    fi
    return 0
  fi

  skill_text="$(cat "$skill_file")"
  trigger_text="$(cat "$trigger_file")"
  prompt="$(cat <<EOF
Task: Run activation tests for skill '${skill}' after its review update.
Inputs are embedded below.

Skill definition (source: ${skill_file_rel}):
<skill_md>
${skill_text}
</skill_md>

Trigger cases (source: ${trigger_file_rel}):
<trigger_cases_md>
${trigger_text}
</trigger_cases_md>

Instructions:
- Parse trigger cases from <trigger_cases_md>. Each case contains a prompt and expected activation (yes/no).
- For each case, decide if the skill should activate and whether that matches expectation.
- Provide a short rationale per case.
- Provide one concise sample opening response for each case.
- At the end, output exactly one status line:
TRIGGER_TEST_STATUS: PASS
or
TRIGGER_TEST_STATUS: FAIL
- Mark FAIL if any case mismatches expected activation or if inputs are ambiguous.
Output:
- Case-by-case results
- Final status line
EOF
)"
  (
    cd "$ROOT"
    codex exec --sandbox "$SUBAGENT_SANDBOX" "$prompt"
  ) >"$log" 2>&1 &
  echo "[queued] $skill trigger test -> $log"
}

trigger_test_status_from_log() {
  local log="$1"
  local status
  status="$(grep -E '^TRIGGER_TEST_STATUS: (PASS|FAIL)$' "$log" | tail -n1 | awk -F': ' '{print $2}')"
  if [[ "$status" == "PASS" || "$status" == "FAIL" ]]; then
    printf '%s\n' "$status"
    return 0
  fi
  printf 'UNKNOWN\n'
  return 1
}

run_trigger_case_generation() {
  local skill="$1"
  local trigger_file="${TRIGGER_CASES_DIR}/${skill}.md"
  local log="$LOGDIR/${skill}.trigger-cases.log"
  local skill_file="$ROOT/skills/$skill/SKILL.md"
  local rc=0

  if [[ -f "$trigger_file" ]]; then
    return 0
  fi

  if (( DRY_RUN == 1 )); then
    echo "[dry-run] would generate trigger-cases: $skill -> $trigger_file"
    return 0
  fi

  "$VENV/bin/python" - "$skill" "$skill_file" "$trigger_file" >"$log" 2>&1 <<'PY' || rc=$?
from __future__ import annotations
import re
import sys
from pathlib import Path

skill = sys.argv[1]
skill_file = Path(sys.argv[2])
out_file = Path(sys.argv[3])
text = skill_file.read_text(encoding="utf-8")
lines = text.splitlines()

def section_bullets(title: str) -> list[str]:
    bullets: list[str] = []
    heading = f"## {title}".strip().lower()
    in_sec = False
    for line in lines:
        s = line.strip()
        if s.lower().startswith("## "):
            in_sec = (s.lower() == heading)
            continue
        if not in_sec:
            continue
        if s.startswith("- "):
            bullets.append(s[2:].strip())
    return bullets

def to_prompt(s: str, positive: bool) -> str:
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s).strip().rstrip(".")
    if not s:
        return "I need help deciding an approach for an ambiguous task." if positive else "Implement this exact task now with no upfront planning."
    if positive:
        return f"I need help with this: {s}. Can you guide me?"
    return f"Please do this exactly now: {s}. No planning, just implementation."

positive = section_bullets("Use this skill when")
negative = section_bullets("Do not use this skill when")

pos_prompts = [to_prompt(p, True) for p in positive[:2]]
while len(pos_prompts) < 2:
    pos_prompts.append("Requirements are unclear and we need help comparing options before implementation.")

neg_prompts = [to_prompt(n, False) for n in negative[:1]]
if not neg_prompts:
    neg_prompts = ["Implement this exact feature now; requirements are final and no design/exploration is needed."]

content = [
    f"# Trigger Cases: {skill}",
    "",
    "## Positive (should activate)",
]
for p in pos_prompts:
    content.append(f'- prompt: "{p.replace(chr(34), chr(39))}"')
    content.append("  expect_activate: yes")
    content.append("")
content.append("## Negative (should not activate)")
for p in neg_prompts:
    content.append(f'- prompt: "{p.replace(chr(34), chr(39))}"')
    content.append("  expect_activate: no")

out_file.parent.mkdir(parents=True, exist_ok=True)
out_file.write_text("\n".join(content).rstrip() + "\n", encoding="utf-8")
print(f"created: {out_file}")
print(f"positive_cases: {len(pos_prompts)}")
print(f"negative_cases: {len(neg_prompts)}")
PY
  if (( rc != 0 )) || [[ ! -f "$trigger_file" ]]; then
    TRIGGER_CASE_GEN_FAILED_SKILLS+=("$skill (generation failed)")
    echo "[failed] $skill trigger-cases generation"
    return 1
  fi
  echo "[ok] $skill trigger-cases generation"
  return 0
}

sanitize_skill_activation_sections() {
  local skill="$1"
  local skill_file="$ROOT/skills/$skill/SKILL.md"
  local log="$LOGDIR/${skill}.sanitize.log"
  local rc=0

  if (( DRY_RUN == 1 )); then
    echo "[dry-run] would sanitize activation sections in $skill_file"
    return 0
  fi

  "$VENV/bin/python" - "$skill_file" >"$log" 2>&1 <<'PY' || rc=$?
from __future__ import annotations
import re
import sys
from pathlib import Path

skill_file = Path(sys.argv[1])
lines = skill_file.read_text(encoding="utf-8").splitlines()
out: list[str] = []
i = 0
changed = False

while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    # Remove heading sections like:
    # ## Trigger test
    # ### Trigger phrases
    if re.match(r"^#{1,6}\s+Trigger (phrases|tests?|test prompts?)\b", stripped, re.IGNORECASE):
        changed = True
        i += 1
        while i < len(lines) and not re.match(r"^#{1,6}\s+", lines[i].strip()):
            i += 1
        continue

    # Remove bold marker blocks like:
    # **Trigger phrases**
    # **Trigger test prompts**
    if re.match(r"^\*\*Trigger (phrases|tests?|test prompts?)\*\*\s*$", stripped, re.IGNORECASE):
        changed = True
        i += 1
        while i < len(lines):
            s = lines[i].strip()
            if re.match(r"^#{1,6}\s+", s):
                break
            if s == "" or s.startswith("- "):
                i += 1
                continue
            break
        continue

    # Remove inline label blocks like:
    # Trigger tests:
    # Trigger test prompts:
    # - Trigger phrases: "..."
    if re.match(r"^(?:-\s*)?Trigger (phrases|tests?|test prompts?)\s*:\s*(.*)$", stripped, re.IGNORECASE):
        changed = True
        # If cue text is on the same line, removing this single line is enough.
        # If it's a label-only line, also remove the following list block.
        label_only = re.match(r"^(?:-\s*)?Trigger (phrases|tests?|test prompts?)\s*:\s*$", stripped, re.IGNORECASE) is not None
        i += 1
        if label_only:
            while i < len(lines):
                s = lines[i].strip()
                if re.match(r"^#{1,6}\s+", s):
                    break
                if s == "" or s.startswith("- "):
                    i += 1
                    continue
                break
        continue

    out.append(line)
    i += 1

text = "\n".join(out).rstrip() + "\n"
if changed:
    text = re.sub(r"\n{3,}", "\n\n", text)
skill_file.write_text(text, encoding="utf-8")
print(f"changed: {changed}")
PY
  if (( rc != 0 )); then
    echo "[failed] $skill sanitize"
    SANITIZE_FAILED_SKILLS+=("$skill (sanitize failed)")
    return 1
  fi
  echo "[ok] $skill sanitize"
  return 0
}

declare -a BATCH_PIDS=()
declare -a BATCH_SKILLS=()
declare -a FAILED_SKILLS=()
declare -a REVIEW_OK_SKILLS=()
declare -a TRIGGER_TEST_FAILED_SKILLS=()
declare -a TRIGGER_TEST_SKIPPED_SKILLS=()
declare -a TRIGGER_CASE_GEN_FAILED_SKILLS=()
declare -a SANITIZE_FAILED_SKILLS=()

reap_batch() {
  local i pid rc skill
  for i in "${!BATCH_PIDS[@]}"; do
    pid="${BATCH_PIDS[$i]}"
    skill="${BATCH_SKILLS[$i]}"
    local review_log="$LOGDIR/${skill}.log"
    rc=0
    if wait "$pid"; then
      if grep -Eq '^QUESTIONS$' "$review_log"; then
        FAILED_SKILLS+=("$skill (blocked: QUESTIONS)")
        echo "[failed] $skill (blocked: QUESTIONS)"
      else
        echo "[ok] $skill"
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

if (( RUN_TRIGGER_TESTS == 1 )); then
  for skill in "${REVIEW_OK_SKILLS[@]}"; do
    sanitize_skill_activation_sections "$skill"
  done

  if (( AUTO_GENERATE_TRIGGER_CASES == 1 )); then
    for skill in "${REVIEW_OK_SKILLS[@]}"; do
      run_trigger_case_generation "$skill"
    done
  fi

  BATCH_PIDS=()
  BATCH_SKILLS=()
  count=0
  for skill in "${REVIEW_OK_SKILLS[@]}"; do
    run_trigger_test "$skill"
    if [[ -f "${TRIGGER_CASES_DIR}/${skill}.md" ]] && (( DRY_RUN == 0 )); then
      BATCH_PIDS+=("$!")
      BATCH_SKILLS+=("$skill")
      count=$((count+1))
      if (( count % BATCH_SIZE == 0 )); then
        for i in "${!BATCH_PIDS[@]}"; do
          pid="${BATCH_PIDS[$i]}"
          skill_name="${BATCH_SKILLS[$i]}"
          if wait "$pid"; then
            log="$LOGDIR/${skill_name}.trigger-test.log"
            status="$(trigger_test_status_from_log "$log")"
            if [[ "$status" != "PASS" ]]; then
              TRIGGER_TEST_FAILED_SKILLS+=("$skill_name (status $status)")
              echo "[failed] $skill_name trigger test (status $status)"
            else
              echo "[ok] $skill_name trigger test"
            fi
          else
            rc=$?
            TRIGGER_TEST_FAILED_SKILLS+=("$skill_name (exit $rc)")
            echo "[failed] $skill_name trigger test (exit $rc)"
          fi
        done
        BATCH_PIDS=()
        BATCH_SKILLS=()
      fi
    fi
  done

  if (( DRY_RUN == 0 )) && (( ${#BATCH_PIDS[@]} > 0 )); then
    for i in "${!BATCH_PIDS[@]}"; do
      pid="${BATCH_PIDS[$i]}"
      skill_name="${BATCH_SKILLS[$i]}"
      if wait "$pid"; then
        log="$LOGDIR/${skill_name}.trigger-test.log"
        status="$(trigger_test_status_from_log "$log")"
        if [[ "$status" != "PASS" ]]; then
          TRIGGER_TEST_FAILED_SKILLS+=("$skill_name (status $status)")
          echo "[failed] $skill_name trigger test (status $status)"
        else
          echo "[ok] $skill_name trigger test"
        fi
      else
        rc=$?
        TRIGGER_TEST_FAILED_SKILLS+=("$skill_name (exit $rc)")
        echo "[failed] $skill_name trigger test (exit $rc)"
      fi
    done
  fi
fi

if (( DRY_RUN == 1 )); then
  echo "Dry run complete. Planned ${#SKILLS[@]} skills with batch size ${BATCH_SIZE}."
  exit 0
fi

if (( AUDIT_AFTER == 1 )); then
  "$VENV/bin/python" "$ROOT/scripts/audit_skills.py"
fi

echo "Completed ${#SKILLS[@]} skills. Logs in $LOGDIR"
if (( ${#FAILED_SKILLS[@]} > 0 )); then
  echo "Failed skills:"
  printf '  - %s\n' "${FAILED_SKILLS[@]}"
  exit 1
fi

if (( RUN_TRIGGER_TESTS == 1 )); then
  if (( ${#SANITIZE_FAILED_SKILLS[@]} > 0 )); then
    echo "Sanitization failures:"
    printf '  - %s\n' "${SANITIZE_FAILED_SKILLS[@]}"
    exit 1
  fi
  if (( ${#TRIGGER_TEST_SKIPPED_SKILLS[@]} > 0 )); then
    echo "Trigger tests skipped (missing trigger-cases file):"
    printf '  - %s\n' "${TRIGGER_TEST_SKIPPED_SKILLS[@]}"
  fi
  if (( ${#TRIGGER_CASE_GEN_FAILED_SKILLS[@]} > 0 )); then
    echo "Trigger-cases generation failures:"
    printf '  - %s\n' "${TRIGGER_CASE_GEN_FAILED_SKILLS[@]}"
    exit 1
  fi
  if (( ${#TRIGGER_TEST_FAILED_SKILLS[@]} > 0 )); then
    echo "Trigger test failures:"
    printf '  - %s\n' "${TRIGGER_TEST_FAILED_SKILLS[@]}"
    exit 1
  fi
fi
