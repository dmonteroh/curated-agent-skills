#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CHECKLIST="$ROOT/scripts/auditing/SKILL_REVIEW_CHECKLIST.md"
LOGDIR="$ROOT/scripts/auditing/logs"
BATCH_SIZE=10
SUBAGENT_SANDBOX="${SUBAGENT_SANDBOX:-danger-full-access}"
REVIEW_MODEL="${REVIEW_MODEL:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV="$ROOT/.venv"
SKILLS_FILE="$ROOT/scripts/auditing/skills_list.txt"
DRY_RUN=0
NO_INSTALL=0
declare -a REQUESTED_SKILLS=()
PRINT_POLICY=0
SINGLE_MODEL="${SINGLE_MODEL:-0}"
# Single-model review dispatch (--single-model / SINGLE_MODEL=1 only). Tier
# terra: it judges SKILL.md against the binding bar, edits files under
# skills/<name>/, and emits a verdict plus removal proposals. Vendor codex:
# the one reviewer this path dispatches.
REVIEW_TIER="terra"
REVIEW_VENDOR="codex"
RESOLVED_MODEL=""
MODEL_SOURCE=""
# Reviewer arms (dual mode, the default): one read-only dispatch per
# declared arm, each a different LLM. Add a third arm by adding one entry
# here plus one case arm in each of build_reviewer_argv and client_for_arm
# below; no loop anywhere in this file needs to change.
declare -a REVIEWER_ARMS=(codex claude)
# Synthesis is a single fixed call site, not a declared/iterated arm: its
# vendor is permanently claude, and it is the run's only writer.
SYNTHESIS_VENDOR="claude"

mkdir -p "$LOGDIR"

usage() {
  cat <<USAGE
Usage: scripts/auditing/run_parallel_skill_reviews.sh [options]

Default: dual mode. Per skill, dispatch one read-only reviewer per declared
arm (REVIEWER_ARMS, currently codex and claude), then one synthesis call
over every arm's review, and report the synthesis outcome as the skill's
verdict: N+1 calls per skill.

Options:
  --batch-size N        Number of concurrent skills reviewed at once (default:
                        10); a batch of B skills runs up to B times the arm
                        count concurrent reviewer processes, then up to B
                        synthesis processes
  --subagent-sandbox M  Sandbox passed to nested codex exec calls (single-model
                        mode only): workspace-write | danger-full-access
                        (default: danger-full-access). workspace-write routes
                        through bubblewrap and silently no-ops wherever bwrap
                        cannot create a user namespace: the call exits 0
                        having written nothing.
  --model NAME          Model passed to nested codex exec calls in single-model
                        mode (default: resolved from the tier policy; see
                        --print-model-policy)
  --single-model        Opt out of the dual default: dispatch one codex
                        reviewer per skill, as before dual mode existed
  --skill NAME          Review only this skill (repeatable)
  --skills-file PATH    Read skill names (one per line) from PATH
  --list-skills         Print discovered skills and exit
  --dry-run             Show planned work without invoking codex or claude
  --no-install          Skip installing audit dependencies
  --print-model-policy  Print the tier -> model resolution table and exit
  -h, --help            Show this help

Environment:
  PYTHON_BIN            Python interpreter to use (default: python3)
  SUBAGENT_SANDBOX      Nested codex exec sandbox override (same values as --subagent-sandbox)
  REVIEW_MODEL          Single-model mode's codex override (same values as
                        --model; default: unset, the tier policy resolves the
                        id); dual mode's claude arms always resolve from policy
  SINGLE_MODEL          Same as --single-model when set to 1
USAGE
}

# Model tier policy (operator, 2026-08-12): sol/opus is never used in this
# pipeline; terra is reserved for dispatches that need reasoning; everything
# else is luna. Tier equivalence: haiku=luna, sonnet=terra, opus=sol.
# Vendor default is claude; a call site passing codex states why.
# This function is the only home for a model id or alias literal in this file.
resolve_model() {
  local tier="$1" vendor="${2:-claude}"
  case "$tier:$vendor" in
    terra:codex)  printf '%s\n' 'gpt-5.6-terra' ;;
    terra:claude) printf '%s\n' 'sonnet' ;;
    luna:claude)  printf '%s\n' 'haiku' ;;
    luna:codex)   echo "error: no luna model id is pinned for codex; verify one against the installed client and pin it here before adding a luna codex dispatch" >&2; return 1 ;;
    sol:*|opus:*) echo "error: the sol/opus tier is not used in this pipeline (operator policy, 2026-08-12)" >&2; return 1 ;;
    *)            echo "error: unknown tier '$tier' for vendor '$vendor' (tiers: luna, terra)" >&2; return 1 ;;
  esac
}

resolve_provenance() {
  case "$1:$2" in
    terra:codex)              printf '%s\n' 'codex-exec-banner@2026-08-15' ;;
    terra:claude|luna:claude) printf '%s\n' 'claude-cli-tier-alias@2026-08-12' ;;
    luna:codex)               printf '%s\n' 'no-verified-id-and-no-consumer' ;;
    sol:*|opus:*)             printf '%s\n' 'operator-policy@2026-08-12' ;;
    *)                        printf '%s\n' 'unknown' ;;
  esac
  return 0
}

refuse_forbidden_model() {
  local model="$1"
  if [[ "${model,,}" =~ (^|[-_.])(sol|opus)([-_.]|$) ]]; then
    echo "error: model '$model' is in the sol/opus tier, which this pipeline does not use (operator policy, 2026-08-12)" >&2
    exit 1
  fi
  return 0
}

print_model_policy() {
  local tier vendor value
  printf '%s\n' 'model-policy: operator policy 2026-08-12 - sol/opus unused in this pipeline; terra for dispatches that need reasoning; luna otherwise'
  printf '%s\n' 'model-policy: tier equivalence haiku=luna sonnet=terra opus=sol'
  for tier in luna terra; do
    for vendor in claude codex; do
      value="$(resolve_model "$tier" "$vendor" 2>/dev/null)" || value='<unpinned>'
      printf 'tier=%s vendor=%s resolved=%s provenance=%s\n' "$tier" "$vendor" "$value" "$(resolve_provenance "$tier" "$vendor")"
    done
  done
  for tier in sol opus; do
    printf 'tier=%s vendor=any resolved=<forbidden> provenance=%s\n' "$tier" "$(resolve_provenance "$tier" any)"
  done
  local arm
  for arm in "${REVIEWER_ARMS[@]}"; do
    value="$(resolve_model terra "$arm")" || return 1
    printf 'site=reviewer-arm-%s tier=terra vendor=%s resolved=%s source=policy\n' "$arm" "$arm" "$value"
  done
  value="$(resolve_model terra "$SYNTHESIS_VENDOR")" || return 1
  printf 'site=synthesis tier=terra vendor=%s resolved=%s source=policy\n' "$SYNTHESIS_VENDOR" "$value"
  printf 'model-policy: call-site count %s\n' "$(( ${#REVIEWER_ARMS[@]} + 1 ))"
  return 0
}

# Dual-mode dispatch helpers. Model ids and aliases stay inside
# resolve_model; everything below refers to a tier and to an arm (which is
# also the vendor name, by design). Adding a third arm is one entry in
# REVIEWER_ARMS above plus one case arm in each of build_reviewer_argv and
# client_for_arm; no loop in this file changes.

arm_log_path() {
  printf '%s\n' "$LOGDIR/$1.$2.log"
}

arm_last_message_path() {
  printf '%s\n' "$LOGDIR/$1.$2.last-message.txt"
}

synthesis_log_path() {
  printf '%s\n' "$LOGDIR/$1.synthesis.log"
}

synthesis_last_message_path() {
  printf '%s\n' "$LOGDIR/$1.synthesis.last-message.txt"
}

client_for_arm() {
  case "$1" in
    codex)  printf '%s\n' 'codex' ;;
    claude) printf '%s\n' 'claude' ;;
    *)
      echo "error: no client mapped for reviewer arm '$1'" >&2
      return 1
      ;;
  esac
}

declare -a REVIEWER_ARGV=()
REVIEWER_MODEL=""
REVIEWER_STDIN=0

# Every arm runs at tier terra; only the synthesis call writes. Write
# prevention for the codex arm lives in the prompt now (the authority
# parameter threaded into render_reviewer_prompt below), not in the
# sandbox: bubblewrap cannot create a user namespace in this container, so
# every sandbox mode codex offers routes through it and no-ops silently -
# the call exits 0 having read nothing (devcontainer ruling, operator,
# 2026-08-16). --sandbox danger-full-access is pinned literally here, not
# routed through $SUBAGENT_SANDBOX, which stays single-mode's write-capable
# dispatch knob only. The codex arm reuses RESOLVED_MODEL, already computed
# from policy or REVIEW_MODEL below, with a positional prompt. The claude
# arm always resolves fresh from policy (REVIEW_MODEL stays codex-scoped);
# its prompt goes on stdin, never as a positional argument, since
# --allowedTools/--disallowedTools are variadic and would silently swallow
# a positional prompt that follows them. --permission-mode dontAsk is
# retained as a defence, not cosmetic: a denied tool call (Edit, barred by
# --disallowedTools) would otherwise block waiting for an interactive
# response that never arrives in --print mode, hanging past any reasonable
# timeout with zero output on both streams.
build_reviewer_argv() {
  local arm="$1" last_msg="$2"
  REVIEWER_ARGV=()
  REVIEWER_MODEL=""
  REVIEWER_STDIN=0
  case "$arm" in
    codex)
      REVIEWER_MODEL="$RESOLVED_MODEL"
      REVIEWER_ARGV=(exec --sandbox danger-full-access --output-last-message "$last_msg" --model "$REVIEWER_MODEL")
      ;;
    claude)
      REVIEWER_MODEL="$(resolve_model terra claude)" || return 1
      REVIEWER_ARGV=(--print --model "$REVIEWER_MODEL" --permission-mode dontAsk --allowedTools "Read,Glob,Grep" --disallowedTools "Edit,Write,NotebookEdit,Bash")
      REVIEWER_STDIN=1
      ;;
    *)
      echo "error: no argv builder for reviewer arm '$arm'" >&2
      return 1
      ;;
  esac
  return 0
}

# tier terra, vendor $SYNTHESIS_VENDOR: the run's only writer, given every
# arm's review in full.
declare -a SYNTHESIS_ARGV=()
SYNTHESIS_MODEL=""

build_synthesis_argv() {
  SYNTHESIS_MODEL="$(resolve_model terra "$SYNTHESIS_VENDOR")" || return 1
  SYNTHESIS_ARGV=(--print --model "$SYNTHESIS_MODEL" --permission-mode acceptEdits --allowedTools "Read,Glob,Grep,Edit,Write")
  return 0
}

# Run-level provenance, generalized across N+1 call sites: captured once per
# label (a reviewer arm name, or "synthesis"), from the first reaped call's
# log, mirroring the single-mode capture_provenance below. Bash 3.2 has no
# associative arrays; a label is arbitrary text (an arm name may contain a
# hyphen, which is not a legal part of a bash identifier), so lookup is a
# linear scan over parallel arrays rather than a dynamically named variable.
declare -a PROV_LABELS=()
declare -a PROV_CLIENTS=()
declare -a PROV_MODELS=()

capture_call_provenance() {
  local label="$1" log="$2" i banner model
  for i in "${!PROV_LABELS[@]}"; do
    if [[ "${PROV_LABELS[$i]}" == "$label" ]]; then return 0; fi
  done
  if [[ ! -f "$log" ]]; then return 0; fi
  banner="$(head -n1 "$log")" || true
  model="$(grep -m1 -E '^model: ' "$log" | cut -d' ' -f2-)" || true
  if [[ -z "$banner" && -z "$model" ]]; then return 0; fi
  PROV_LABELS+=("$label")
  PROV_CLIENTS+=("$banner")
  PROV_MODELS+=("$model")
  return 0
}

provenance_client() {
  local label="$1" i
  for i in "${!PROV_LABELS[@]}"; do
    if [[ "${PROV_LABELS[$i]}" == "$label" ]]; then
      printf '%s\n' "${PROV_CLIENTS[$i]}"
      return 0
    fi
  done
  printf '%s\n' unknown
  return 0
}

provenance_model() {
  local label="$1" i
  for i in "${!PROV_LABELS[@]}"; do
    if [[ "${PROV_LABELS[$i]}" == "$label" ]]; then
      printf '%s\n' "${PROV_MODELS[$i]}"
      return 0
    fi
  done
  printf '%s\n' unknown
  return 0
}

# Selects one challenge line, deterministically, from a SKILL.md: eligible
# lines are non-blank, not a fence delimiter, not inside a fence, and >= 30
# characters after trimming; the eligible line nearest the file's midpoint
# wins, ties to the lower number. Bash 3.2-clean (no associative arrays, no
# mapfile): the selection itself is awk, called through command
# substitution.
select_challenge_line() {
  local file="$1"
  awk '
    { ln[NR]=$0 }
    /^[ \t]*```/{f[NR]=1; inf=!inf; next}
    { if(inf) f[NR]=1 }
    END{
      mid=int(NR/2); best=0; bd=1e9
      for(i=1;i<=NR;i++){
        if(f[i]) continue
        l=ln[i]; gsub(/^[ \t]+|[ \t]+$/,"",l)
        if(length(l)<30) continue
        d=(i>mid?i-mid:mid-i)
        if(d<bd){bd=d; best=i}
      }
      print best
    }
  ' "$file"
}

# Renders scripts/auditing/reviewer-prompt.md (read from disk and
# interpolated - never inlined, paraphrased, or converted to a heredoc) with
# its named placeholders: SKILL_DIRECTORY, CHECKLIST_PATH, GUIDANCE_PATH,
# OPEN_ITEMS_PATH, VENV_PYTHON_PATH, AUTHORITY_TASK, AUTHORITY_RULE,
# CHALLENGE_LINE. Shared with the single-model dispatch below: one reviewer
# prompt, never a second variant. mode is "single" or "dual"; it selects
# the AUTHORITY_TASK/AUTHORITY_RULE values interpolated into the Task line
# and the first Rules bullet - the only two places single and dual mode's
# renderings differ, besides the read-proof line number. Marker lines
# (`<!-- parity:... -->`) in the asset are stripped before substitution, so
# none reaches a dispatched prompt. The strip uses two plain -e clauses
# (POSIX BRE, portable to BSD/macOS sed) rather than `\(start\|end\)`,
# whose `\|` alternation is a GNU BRE extension.
REVIEWER_PROMPT=""

render_reviewer_prompt() {
  local skill="$1"
  local mode="$2"
  local skill_dir="skills/$skill"
  local checklist_rel="scripts/auditing/SKILL_REVIEW_CHECKLIST.md"
  local guidance_rel="scripts/auditing/references/authoring-guidance.md"
  local open_items_rel="scripts/auditing/OPEN_ITEMS.md"
  local venv_python_rel=".venv/bin/python"
  local authority_task authority_rule
  case "$mode" in
    single)
      authority_task="Apply changes directly."
      authority_rule="- Apply changes directly to files under ${skill_dir}."
      ;;
    dual)
      authority_task="You are a read-only reviewer. Report what must change; do not create, edit, delete, or move any file."
      authority_rule="- You are a read-only reviewer: do not create, edit, delete, or move any file."
      ;;
    *)
      echo "error: render_reviewer_prompt: unknown mode '$mode' (single, dual)" >&2
      return 1
      ;;
  esac

  local skill_md="$ROOT/skills/$skill/SKILL.md"
  local challenge_k challenge_line
  challenge_k="$(select_challenge_line "$skill_md")"
  challenge_line="$(sed -n "${challenge_k}p" "$skill_md")"
  {
    printf '%s\n' "$challenge_k"
    printf '%s\n' "$challenge_line"
  } >"$LOGDIR/${skill}.readproof"

  local reviewer_prompt_asset="$ROOT/scripts/auditing/reviewer-prompt.md"
  if [[ ! -r "$reviewer_prompt_asset" ]]; then
    echo "error: render_reviewer_prompt: cannot read asset '$reviewer_prompt_asset'" >&2
    return 1
  fi

  local asset
  asset="$(sed -e '/^<!-- parity:[a-z][a-z-]*:start -->$/d' -e '/^<!-- parity:[a-z][a-z-]*:end -->$/d' "$reviewer_prompt_asset"; printf x)"
  asset="${asset%x}"
  if [[ -z "$asset" ]]; then
    echo "error: render_reviewer_prompt: asset '$reviewer_prompt_asset' is empty after marker-strip" >&2
    return 1
  fi
  asset="${asset//SKILL_DIRECTORY/$skill_dir}"
  asset="${asset//CHECKLIST_PATH/$checklist_rel}"
  asset="${asset//GUIDANCE_PATH/$guidance_rel}"
  asset="${asset//OPEN_ITEMS_PATH/$open_items_rel}"
  asset="${asset//VENV_PYTHON_PATH/$venv_python_rel}"
  asset="${asset//AUTHORITY_TASK/$authority_task}"
  asset="${asset//AUTHORITY_RULE/$authority_rule}"
  asset="${asset//CHALLENGE_LINE/$challenge_k}"
  REVIEWER_PROMPT="$asset"
  return 0
}

# Renders scripts/auditing/synthesis-prompt.md (read from disk and
# interpolated - never inlined, paraphrased, or converted to a heredoc)
# with its named placeholders: SKILL_DIRECTORY, SKILL_NAME, CHECKLIST_PATH,
# OPEN_ITEMS_PATH, REVIEW_ARTIFACTS. Reviews are supplied in full and
# unmodified, in the order REVIEWER_ARMS declares them, referred to only by
# position (Review 1 ... Review N) plus the arm that produced each one.
SYNTHESIS_PROMPT=""

render_synthesis_prompt() {
  local skill="$1"
  local skill_dir="skills/$1"
  local checklist_path="scripts/auditing/SKILL_REVIEW_CHECKLIST.md"
  local open_items_path="scripts/auditing/OPEN_ITEMS.md"
  local asset arm n msg artifacts last_msg

  IFS= read -r -d '' asset <"$ROOT/scripts/auditing/synthesis-prompt.md" || true

  artifacts=""
  n=0
  for arm in "${REVIEWER_ARMS[@]}"; do
    n=$((n + 1))
    last_msg="$(arm_last_message_path "$skill" "$arm")" || true
    msg="$(cat "$last_msg")" || true
    artifacts="${artifacts}Review ${n} (arm: ${arm}):
${msg}

"
  done

  asset="${asset//SKILL_DIRECTORY/$skill_dir}"
  asset="${asset//SKILL_NAME/$skill}"
  asset="${asset//CHECKLIST_PATH/$checklist_path}"
  asset="${asset//OPEN_ITEMS_PATH/$open_items_path}"
  asset="${asset//REVIEW_ARTIFACTS/$artifacts}"
  SYNTHESIS_PROMPT="$asset"
  return 0
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
    --model)
      REVIEW_MODEL="${2:-}"
      shift 2
      ;;
    --single-model)
      SINGLE_MODEL=1
      shift
      ;;
    --skill)
      REQUESTED_SKILLS+=("${2:-}")
      shift 2
      ;;
    --skills-file)
      SKILLS_FILE_OVERRIDE="${2:-}"
      shift 2
      ;;
    --print-model-policy)
      PRINT_POLICY=1
      shift
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

if (( PRINT_POLICY == 1 )); then
  print_model_policy
  exit 0
fi

if [[ -n "$REVIEW_MODEL" ]]; then
  RESOLVED_MODEL="$REVIEW_MODEL"
  MODEL_SOURCE="REVIEW_MODEL"
else
  RESOLVED_MODEL="$(resolve_model "$REVIEW_TIER" "$REVIEW_VENDOR")" || exit 1
  MODEL_SOURCE="policy"
fi
refuse_forbidden_model "$RESOLVED_MODEL"

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

if (( SINGLE_MODEL == 1 )); then
  if (( DRY_RUN == 0 )) && ! command -v codex >/dev/null 2>&1; then
    echo "error: codex command not found in PATH" >&2
    exit 1
  fi

  echo "codex client: $(codex --version 2>/dev/null || echo unknown)"
  echo "model requested: $RESOLVED_MODEL (tier=$REVIEW_TIER vendor=$REVIEW_VENDOR source=$MODEL_SOURCE)"
else
  echo "reviewer arms: ${REVIEWER_ARMS[*]} (count ${#REVIEWER_ARMS[@]})"
  for arm in "${REVIEWER_ARMS[@]}"; do
    client="$(client_for_arm "$arm")" || exit 1
    if (( DRY_RUN == 0 )) && ! command -v "$client" >/dev/null 2>&1; then
      echo "error: $client command not found in PATH (required by reviewer arm $arm)" >&2
      exit 1
    fi
    echo "reviewer arm $arm client: $("$client" --version 2>/dev/null || echo unknown)"
    build_reviewer_argv "$arm" "" || exit 1
    if [[ "$arm" == "$REVIEW_VENDOR" ]]; then
      arm_source="$MODEL_SOURCE"
    else
      arm_source="policy"
    fi
    echo "reviewer arm $arm model requested: $REVIEWER_MODEL (tier=terra vendor=$arm source=$arm_source)"
  done

  if (( DRY_RUN == 0 )) && ! command -v "$SYNTHESIS_VENDOR" >/dev/null 2>&1; then
    echo "error: $SYNTHESIS_VENDOR command not found in PATH (required by synthesis)" >&2
    exit 1
  fi
  echo "synthesis client: $("$SYNTHESIS_VENDOR" --version 2>/dev/null || echo unknown)"
  build_synthesis_argv || exit 1
  echo "synthesis model requested: $SYNTHESIS_MODEL (tier=terra vendor=$SYNTHESIS_VENDOR source=policy)"
fi

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
  local log="$LOGDIR/${skill}.log"
  local last_msg="$LOGDIR/${skill}.last-message.txt"
  local prompt
  local -a codex_args=(exec --sandbox "$SUBAGENT_SANDBOX" --output-last-message "$last_msg" --model "$RESOLVED_MODEL")

  if (( DRY_RUN == 1 )); then
    echo "[dry-run] would review: $skill"
    printf '[dry-run] codex'
    printf ' %q' "${codex_args[@]}"
    printf ' <dispatch-prompt>\n'
    return 0
  fi

  rm -f "$last_msg"

  render_reviewer_prompt "$skill" single
  prompt="$REVIEWER_PROMPT"

  (
    cd "$ROOT"
    codex "${codex_args[@]}" "$prompt"
  ) >"$log" 2>&1 &
  echo "[queued] $skill -> $log"
}

# Classification bridge: writes KEY=VALUE lines to out_file, always returns 0.
classify_review() {
  local msg_file="$1" out_file="$2"
  : >"$out_file"
  "$VENV/bin/python" - "$ROOT/scripts/auditing" "$msg_file" >"$out_file" 2>/dev/null <<'PY' || true
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import review_log
result = review_log.classify(Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace"))
print("OUTCOME=%s" % result.outcome.value)
print("DIFFERENTIATION=%s" % result.differentiation)
print("REMOVAL_PROPOSALS=%s" % ("1" if result.removal_proposals else "0"))
PY
  return 0
}

infra_reason_from_log() {
  local log="$1" line=""
  line="$(grep -E '^(ERROR:|stream error:)' "$log" | tail -n1)" || true
  printf '%s\n' "$line"
  return 0
}

# Run-level provenance: captured once, from the first reaped skill's log.
capture_provenance() {
  local log="$1"
  if [[ -n "$CODEX_CLIENT_BANNER" ]]; then return 0; fi
  if [[ ! -f "$log" ]]; then return 0; fi
  CODEX_CLIENT_BANNER="$(head -n1 "$log")" || true
  CODEX_MODEL_BANNER="$(grep -m1 -E '^model: ' "$log" | cut -d' ' -f2-)" || true
  return 0
}

declare -a BATCH_PIDS=()
declare -a BATCH_SKILLS=()
declare -a FAILED_SKILLS=()
declare -a REVIEW_OK_SKILLS=()
declare -a REVIEW_NO_CHANGE_SKILLS=()
declare -a DIFFERENTIATION_WEAK_SKILLS=()
declare -a DIFFERENTIATION_UNKNOWN_SKILLS=()
declare -a REMOVAL_PROPOSAL_SKILLS=()
declare -a MALFORMED_SKILLS=()
declare -a INFRA_FAILURE_SKILLS=()
CODEX_CLIENT_BANNER=""
CODEX_MODEL_BANNER=""

# Reported, never failing: these need an operator ruling, not a fix by the
# runner. Shared by single mode and dual mode: both populate the same tally
# arrays above, dual mode only ever from the synthesis artifact.
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
  if (( ${#MALFORMED_SKILLS[@]} > 0 )); then
    any=1
    echo "MALFORMED (last-message file empty or contract violation; see log for detail):"
    printf '  - %s\n' "${MALFORMED_SKILLS[@]}"
  fi
  if (( any == 0 )); then
    echo "None."
  fi
  if (( ${#REVIEW_NO_CHANGE_SKILLS[@]} > 0 )); then
    echo "Already at the bar, unchanged: ${#REVIEW_NO_CHANGE_SKILLS[@]}"
  fi
}

# Verifies a call's READ_PROOF line against the challenge captured before
# dispatch for the skill. Returns 0 (match), 1 (absent), or 2 (mismatch);
# never touches the failure-tracking arrays itself - callers decide what a
# non-zero return means for their mode.
verify_read_proof() {
  local artifact="$1" expected_file="$2"
  local line value expected
  line="$(grep -m1 -E '^[[:space:]]*READ_PROOF:' "$artifact")" || true
  if [[ -z "$line" ]]; then
    return 1
  fi
  value="${line#*READ_PROOF:}"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  if [[ "$value" == \`*\` && "${#value}" -ge 2 ]]; then
    value="${value:1:$((${#value} - 2))}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
  fi
  expected="$(sed -n '2p' "$expected_file")"
  expected="${expected#"${expected%%[![:space:]]*}"}"
  expected="${expected%"${expected##*[![:space:]]}"}"
  if [[ "$expected" == \`*\` && "${#expected}" -ge 2 ]]; then
    expected="${expected:1:$((${#expected} - 2))}"
    expected="${expected#"${expected%%[![:space:]]*}"}"
    expected="${expected%"${expected##*[![:space:]]}"}"
  fi
  if [[ "$value" == "$expected" ]]; then
    return 0
  fi
  return 2
}

reap_batch() {
  local i pid rc skill
  for i in "${!BATCH_PIDS[@]}"; do
    pid="${BATCH_PIDS[$i]}"
    skill="${BATCH_SKILLS[$i]}"
    local review_log="$LOGDIR/${skill}.log"
    local last_msg="$LOGDIR/${skill}.last-message.txt"
    local verdict_file="$LOGDIR/${skill}.verdict"
    local readproof_file="$LOGDIR/${skill}.readproof"
    local outcome differentiation removal_proposals reason key value proof_rc
    rc=0
    if wait "$pid"; then
      capture_provenance "$review_log"
      if [[ ! -s "$last_msg" ]]; then
        MALFORMED_SKILLS+=("$skill")
        echo "[malformed] $skill (empty last-message file)"
        continue
      fi
      classify_review "$last_msg" "$verdict_file"
      outcome="UNKNOWN"
      differentiation="UNKNOWN"
      removal_proposals="0"
      while IFS='=' read -r key value; do
        case "$key" in
          OUTCOME) outcome="$value" ;;
          DIFFERENTIATION) differentiation="$value" ;;
          REMOVAL_PROPOSALS) removal_proposals="$value" ;;
        esac
      done <"$verdict_file"
      if [[ "$outcome" == "INFRA-FAILURE" ]]; then
        reason="$(infra_reason_from_log "$review_log")" || true
        INFRA_FAILURE_SKILLS+=("$skill (exit 0: classifier-reported: ${reason:-no error line found})")
        echo "[infra-failure] $skill (exit 0: classifier-reported)"
        continue
      fi
      proof_rc=0
      verify_read_proof "$last_msg" "$readproof_file" || proof_rc=$?
      if (( proof_rc == 1 )); then
        FAILED_SKILLS+=("$skill (read-proof absent)")
        echo "[failed] $skill (read-proof absent)"
        continue
      elif (( proof_rc == 2 )); then
        FAILED_SKILLS+=("$skill (read-proof mismatch)")
        echo "[failed] $skill (read-proof mismatch)"
        continue
      fi
      case "$outcome" in
        NO-CHANGE|CHANGED)
          REVIEW_OK_SKILLS+=("$skill")
          if [[ "$outcome" == "NO-CHANGE" ]]; then
            REVIEW_NO_CHANGE_SKILLS+=("$skill")
          fi
          case "$differentiation" in
            WEAK) DIFFERENTIATION_WEAK_SKILLS+=("$skill") ;;
            STRONG) ;;
            *) DIFFERENTIATION_UNKNOWN_SKILLS+=("$skill") ;;
          esac
          if [[ "$removal_proposals" == "1" ]]; then
            REMOVAL_PROPOSAL_SKILLS+=("$skill")
          fi
          echo "[ok] $skill (status $outcome, differentiation $differentiation)"
          ;;
        QUESTIONS)
          FAILED_SKILLS+=("$skill (blocked: QUESTIONS)")
          echo "[failed] $skill (blocked: QUESTIONS)"
          ;;
        *)
          MALFORMED_SKILLS+=("$skill")
          echo "[malformed] $skill"
          ;;
      esac
    else
      rc=$?
      capture_provenance "$review_log"
      reason="$(infra_reason_from_log "$review_log")" || true
      INFRA_FAILURE_SKILLS+=("$skill (exit $rc: ${reason:-no error line found})")
      echo "[infra-failure] $skill (exit $rc)"
    fi
  done
  BATCH_PIDS=()
  BATCH_SKILLS=()
}

# Dual dispatch: one reviewer per declared arm, launched in the loop over
# REVIEWER_ARMS below - the file's only reviewer-dispatch statement in dual
# mode. codex keeps its positional-prompt shape; claude takes the prompt on
# stdin instead.
declare -a DUAL_ARM_PIDS=()
declare -a DUAL_ARM_ARMS=()
declare -a DUAL_ARM_SKILLS=()
declare -a DUAL_BATCH_SKILLS=()

run_skill_dual() {
  local skill="$1"
  local arm client log last_msg prompt

  if (( DRY_RUN == 1 )); then
    echo "[dry-run] would review: $skill (arms: ${REVIEWER_ARMS[*]})"
    for arm in "${REVIEWER_ARMS[@]}"; do
      last_msg="$(arm_last_message_path "$skill" "$arm")" || true
      build_reviewer_argv "$arm" "$last_msg" || return 1
      client="$(client_for_arm "$arm")" || return 1
      printf '[dry-run] reviewer arm %s: %s' "$arm" "$client"
      printf ' %q' "${REVIEWER_ARGV[@]}"
      printf ' <dispatch-prompt>\n'
    done
    build_synthesis_argv || return 1
    printf '[dry-run] synthesis: %s' "$SYNTHESIS_VENDOR"
    printf ' %q' "${SYNTHESIS_ARGV[@]}"
    printf ' <synthesis-prompt using reviews:'
    for arm in "${REVIEWER_ARMS[@]}"; do
      printf ' %s' "$(arm_last_message_path "$skill" "$arm")"
    done
    printf '; skill_dir=skills/%s; checklist=scripts/auditing/SKILL_REVIEW_CHECKLIST.md; open_items=scripts/auditing/OPEN_ITEMS.md>\n' "$skill"
    return 0
  fi

  render_reviewer_prompt "$skill" dual
  prompt="$REVIEWER_PROMPT"

  for arm in "${REVIEWER_ARMS[@]}"; do
    log="$(arm_log_path "$skill" "$arm")" || true
    last_msg="$(arm_last_message_path "$skill" "$arm")" || true
    rm -f "$log" "$last_msg"
    build_reviewer_argv "$arm" "$last_msg" || return 1
    client="$(client_for_arm "$arm")" || return 1
    if (( REVIEWER_STDIN == 1 )); then
      ( cd "$ROOT"; printf '%s' "$prompt" | "$client" "${REVIEWER_ARGV[@]}" ) >"$last_msg" 2>"$log" &
    else
      ( cd "$ROOT"; "$client" "${REVIEWER_ARGV[@]}" "$prompt" ) >"$log" 2>&1 &
    fi
    DUAL_ARM_PIDS+=("$!")
    DUAL_ARM_ARMS+=("$arm")
    DUAL_ARM_SKILLS+=("$skill")
    echo "[queued] $skill/$arm -> $log"
  done
  DUAL_BATCH_SKILLS+=("$skill")
}

# Per-skill arm-failure record for the phase-one/phase-two gate. A skill
# name is arbitrary text (commonly hyphenated), not a legal bash identifier
# fragment, so this is a linear scan over parallel arrays rather than a
# dynamically named variable - the same reason capture_call_provenance
# above uses one.
declare -a ARM_FAILED_SKILLS=()
declare -a ARM_FAILED_REASONS=()

arm_failure_reason() {
  local skill="$1" i
  for i in "${!ARM_FAILED_SKILLS[@]}"; do
    if [[ "${ARM_FAILED_SKILLS[$i]}" == "$skill" ]]; then
      printf '%s\n' "${ARM_FAILED_REASONS[$i]}"
      return 0
    fi
  done
  return 1
}

record_arm_failure() {
  local skill="$1" reason="$2"
  if arm_failure_reason "$skill" >/dev/null; then return 0; fi
  ARM_FAILED_SKILLS+=("$skill")
  ARM_FAILED_REASONS+=("$reason")
}

# Two-phase reap: phase one classifies every arm's final message for
# infra/empty detection only, never for a verdict; a skill with a failed arm
# never reaches phase two, so a synthesis over a subset of the arms never
# happens.
reap_phase_one() {
  local i pid arm skill rc log last_msg outcome key value verdict_file readproof_file proof_rc
  for i in "${!DUAL_ARM_PIDS[@]}"; do
    pid="${DUAL_ARM_PIDS[$i]}"
    arm="${DUAL_ARM_ARMS[$i]}"
    skill="${DUAL_ARM_SKILLS[$i]}"
    log="$(arm_log_path "$skill" "$arm")" || true
    last_msg="$(arm_last_message_path "$skill" "$arm")" || true
    rc=0
    if wait "$pid"; then
      capture_call_provenance "$arm" "$log"
      if [[ ! -s "$last_msg" ]]; then
        record_arm_failure "$skill" "arm $arm: empty final message"
        echo "[arm-failed] $skill/$arm (empty final message)"
        continue
      fi
      verdict_file="$LOGDIR/${skill}.${arm}.verdict"
      classify_review "$last_msg" "$verdict_file"
      outcome="UNKNOWN"
      while IFS='=' read -r key value; do
        case "$key" in
          OUTCOME) outcome="$value" ;;
        esac
      done <"$verdict_file"
      if [[ "$outcome" == "INFRA-FAILURE" ]]; then
        record_arm_failure "$skill" "arm $arm: INFRA-FAILURE"
        echo "[arm-failed] $skill/$arm (INFRA-FAILURE)"
      else
        readproof_file="$LOGDIR/${skill}.readproof"
        proof_rc=0
        verify_read_proof "$last_msg" "$readproof_file" || proof_rc=$?
        if (( proof_rc == 1 )); then
          record_arm_failure "$skill" "arm $arm: read-proof absent"
          echo "[arm-failed] $skill/$arm (read-proof absent)"
        elif (( proof_rc == 2 )); then
          record_arm_failure "$skill" "arm $arm: read-proof mismatch"
          echo "[arm-failed] $skill/$arm (read-proof mismatch)"
        else
          echo "[arm-ok] $skill/$arm ($outcome)"
        fi
      fi
    else
      rc=$?
      capture_call_provenance "$arm" "$log"
      record_arm_failure "$skill" "arm $arm: exit $rc"
      echo "[arm-failed] $skill/$arm (exit $rc)"
    fi
  done
  DUAL_ARM_PIDS=()
  DUAL_ARM_ARMS=()
  DUAL_ARM_SKILLS=()
}

declare -a SYNTH_PIDS=()
declare -a SYNTH_SKILLS=()

dispatch_phase_two() {
  local skill reason log last_msg
  for skill in "${DUAL_BATCH_SKILLS[@]}"; do
    if reason="$(arm_failure_reason "$skill")"; then
      FAILED_SKILLS+=("$skill (blocked: $reason)")
      echo "[blocked] $skill (arm failure: $reason)"
      continue
    fi
    log="$(synthesis_log_path "$skill")" || true
    last_msg="$(synthesis_last_message_path "$skill")" || true
    rm -f "$log" "$last_msg"
    build_synthesis_argv || return 1
    render_synthesis_prompt "$skill" || return 1
    ( cd "$ROOT"; printf '%s' "$SYNTHESIS_PROMPT" | "$SYNTHESIS_VENDOR" "${SYNTHESIS_ARGV[@]}" ) >"$last_msg" 2>"$log" &
    SYNTH_PIDS+=("$!")
    SYNTH_SKILLS+=("$skill")
    echo "[queued] $skill/synthesis -> $log"
  done
  DUAL_BATCH_SKILLS=()
}

# Reaps synthesis calls and sources the skill's verdict from the synthesis
# artifact only - no reviewer artifact is classified for a verdict or
# counted in these tallies.
reap_phase_two() {
  local i pid skill rc log last_msg outcome differentiation removal_proposals reason key value verdict_file
  for i in "${!SYNTH_PIDS[@]}"; do
    pid="${SYNTH_PIDS[$i]}"
    skill="${SYNTH_SKILLS[$i]}"
    log="$(synthesis_log_path "$skill")" || true
    last_msg="$(synthesis_last_message_path "$skill")" || true
    verdict_file="$LOGDIR/${skill}.synthesis.verdict"
    rc=0
    if wait "$pid"; then
      capture_call_provenance synthesis "$log"
      if [[ ! -s "$last_msg" ]]; then
        MALFORMED_SKILLS+=("$skill")
        echo "[malformed] $skill (synthesis: empty final message; artifact $last_msg)"
        continue
      fi
      classify_review "$last_msg" "$verdict_file"
      outcome="UNKNOWN"
      differentiation="UNKNOWN"
      removal_proposals="0"
      while IFS='=' read -r key value; do
        case "$key" in
          OUTCOME) outcome="$value" ;;
          DIFFERENTIATION) differentiation="$value" ;;
          REMOVAL_PROPOSALS) removal_proposals="$value" ;;
        esac
      done <"$verdict_file"
      case "$outcome" in
        NO-CHANGE|CHANGED)
          REVIEW_OK_SKILLS+=("$skill")
          if [[ "$outcome" == "NO-CHANGE" ]]; then
            REVIEW_NO_CHANGE_SKILLS+=("$skill")
          fi
          case "$differentiation" in
            WEAK) DIFFERENTIATION_WEAK_SKILLS+=("$skill") ;;
            STRONG) ;;
            *) DIFFERENTIATION_UNKNOWN_SKILLS+=("$skill") ;;
          esac
          if [[ "$removal_proposals" == "1" ]]; then
            REMOVAL_PROPOSAL_SKILLS+=("$skill")
          fi
          echo "[ok] $skill (status $outcome, differentiation $differentiation, synthesis $last_msg)"
          ;;
        QUESTIONS)
          FAILED_SKILLS+=("$skill (synthesis blocked: QUESTIONS; artifact $last_msg)")
          echo "[failed] $skill (synthesis blocked: QUESTIONS, synthesis $last_msg)"
          ;;
        INFRA-FAILURE)
          reason="$(infra_reason_from_log "$log")" || true
          INFRA_FAILURE_SKILLS+=("$skill (synthesis exit 0: classifier-reported: ${reason:-no error line found})")
          echo "[infra-failure] $skill (synthesis exit 0: classifier-reported)"
          ;;
        *)
          MALFORMED_SKILLS+=("$skill")
          echo "[malformed] $skill (synthesis, artifact $last_msg)"
          ;;
      esac
    else
      rc=$?
      capture_call_provenance synthesis "$log"
      reason="$(infra_reason_from_log "$log")" || true
      INFRA_FAILURE_SKILLS+=("$skill (synthesis exit $rc: ${reason:-no error line found})")
      echo "[infra-failure] $skill (synthesis exit $rc)"
    fi
  done
  SYNTH_PIDS=()
  SYNTH_SKILLS=()
}

count=0
if (( SINGLE_MODEL == 1 )); then
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
else
  for skill in "${SKILLS[@]}"; do
    run_skill_dual "$skill"
    if (( DRY_RUN == 0 )); then
      count=$((count+1))
      if (( count % BATCH_SIZE == 0 )); then
        reap_phase_one
        dispatch_phase_two
        reap_phase_two
      fi
    fi
  done

  if (( DRY_RUN == 0 )) && (( ${#DUAL_ARM_PIDS[@]} > 0 )); then
    reap_phase_one
    dispatch_phase_two
    reap_phase_two
  fi

  if (( DRY_RUN == 1 )); then
    echo "Dual dry run complete. Planned ${#SKILLS[@]} skills with batch size ${BATCH_SIZE}, ${#REVIEWER_ARMS[@]} reviewer arms plus synthesis (call count $(( (${#REVIEWER_ARMS[@]} + 1) * ${#SKILLS[@]} ))). "
    exit 0
  fi
fi

audit_rc=0
"$VENV/bin/python" "$ROOT/scripts/audit_skills.py" || audit_rc=$?

echo "Completed ${#SKILLS[@]} skills. Logs in $LOGDIR"
if (( SINGLE_MODEL == 1 )); then
  echo "codex client (observed): ${CODEX_CLIENT_BANNER:-unknown}"
  echo "model (observed): ${CODEX_MODEL_BANNER:-unknown}"
else
  for arm in "${REVIEWER_ARMS[@]}"; do
    echo "reviewer arm $arm client (observed): $(provenance_client "$arm")"
    echo "reviewer arm $arm model (observed): $(provenance_model "$arm")"
  done
  echo "synthesis client (observed): $(provenance_client synthesis)"
  echo "synthesis model (observed): $(provenance_model synthesis)"
fi

echo
echo "=== Review results ==="
echo "Real verdicts (NO-CHANGE/CHANGED): ${#REVIEW_OK_SKILLS[@]}"
if (( ${#MALFORMED_SKILLS[@]} > 0 )); then
  echo "MALFORMED:"
  printf '  - %s\n' "${MALFORMED_SKILLS[@]}"
else
  echo "MALFORMED: none"
fi
if (( ${#INFRA_FAILURE_SKILLS[@]} > 0 )); then
  echo "INFRA-FAILURE:"
  printf '  - %s\n' "${INFRA_FAILURE_SKILLS[@]}"
else
  echo "INFRA-FAILURE: none"
fi

print_operator_decisions

if (( ${#FAILED_SKILLS[@]} > 0 )); then
  echo "Failed skills:"
  printf '  - %s\n' "${FAILED_SKILLS[@]}"
fi

if (( ${#FAILED_SKILLS[@]} > 0 || ${#INFRA_FAILURE_SKILLS[@]} > 0 )); then
  exit 1
fi

if (( audit_rc != 0 )); then
  exit "$audit_rc"
fi
