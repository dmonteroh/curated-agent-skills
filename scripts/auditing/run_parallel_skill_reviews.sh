#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CHECKLIST="$ROOT/scripts/auditing/SKILL_REVIEW_CHECKLIST.md"
PDFTXT="$ROOT/scripts/auditing/agent_skills_pdf.txt"
LOGDIR="$ROOT/scripts/auditing/logs"
BATCH_SIZE=10
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV="$ROOT/.venv"

mkdir -p "$LOGDIR"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "error: $PYTHON_BIN not found" >&2
  exit 1
fi

if [[ ! -d "$VENV" ]]; then
  "$PYTHON_BIN" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install -r "$ROOT/scripts/requirements-audit.txt" >/dev/null

SKILLS_FILE="$ROOT/scripts/auditing/skills_list.txt"
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
SKILLS=()
while IFS= read -r line; do
  [[ -n "$line" ]] && SKILLS+=("$line")
done < "$SKILLS_FILE"

if (( ${#SKILLS[@]:-0} == 0 )); then
  echo "error: no skills found under $ROOT/skills" >&2
  exit 1
fi

run_skill() {
  local skill="$1"
  local skill_dir="$ROOT/skills/$skill"
  local log="$LOGDIR/${skill}.log"

  codex exec --sandbox workspace-write "Task: Evaluate skills/${skill}/SKILL.md against scripts/auditing/SKILL_REVIEW_CHECKLIST.md and update it (and any files under skills/${skill}/ if needed) to fully comply. Apply changes directly.\nScope: Only touch files under ${skill_dir}. You may read ${CHECKLIST} and ${PDFTXT}. Do not edit files outside ${skill_dir}.\nRules:\n- Keep the skill independent; do not require other skills to be installed.\n- Do not add brainstorming-gate or multi-agent dependencies.\n- Do not modify package manifests or add dependencies (no package.json, lockfiles, pip installs).\n- If anything is ambiguous, STOP and output QUESTIONS (do not guess).\n- Avoid time-sensitive facts or external network assumptions.\n- If splitting references, create references/README.md as an index.\n- Measure reference file size using tiktoken (cl100k_base). Use the existing venv: ${ROOT}/.venv/bin/python. If a single reference exceeds ~1200 tokens or is clearly multi-topic, split it and add/update references/README.md.\nOutput:\n- Files changed\n- Summary of edits\n- Verification run (if any)" >"$log" 2>&1 &
}

count=0
for skill in "${SKILLS[@]:-}"; do
  run_skill "$skill"
  count=$((count+1))
  if (( count % BATCH_SIZE == 0 )); then
    wait
  fi
done
wait

echo "Completed ${#SKILLS[@]} skills. Logs in $LOGDIR"
