#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CHECKLIST="$ROOT/scripts/auditing/SKILL_REVIEW_CHECKLIST.md"
LOGDIR="$ROOT/scripts/auditing/logs"
BATCH_SIZE=10
REVIEW_MODEL="${REVIEW_MODEL:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV="$ROOT/.venv"
SKILLS_FILE="$ROOT/scripts/auditing/skills_list.txt"
DRY_RUN=0
NO_INSTALL=0
declare -a REQUESTED_SKILLS=()
PRINT_POLICY=0
ARMS_OPT=""
ARMS_SET=0
# --model / REVIEW_MODEL scope: the codex reviewer arm only. Tier terra,
# vendor codex - the pair RESOLVED_MODEL below resolves against when no
# override is given; refused when codex is not among the selected --arms.
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
  --arms NAME[,NAME...] Reviewer arms to dispatch, replacing the default
                        wholesale, order preserved (default: codex,claude);
                        legal names: codex, claude
  --model NAME          Model passed to the codex reviewer arm (default:
                        resolved from the tier policy; see
                        --print-model-policy); refused when codex is not
                        among the selected --arms
  --effort LEVEL        Reasoning effort for every reviewer arm: one of low,
                        medium, high, xhigh, max (default: medium, the
                        operator's standing choice, pinned explicitly for
                        both vendors - claude's own default would be high).
                        The claude arm gets --effort LEVEL; the codex arm
                        gets -c model_reasoning_effort=LEVEL. The codex arm
                        also always pins -c service_tier=default: priority
                        (speed) processing stays off - it costs more
  --synthesis-effort LEVEL
                        Reasoning effort for the synthesis call (same
                        values; default: unset). This is the run's only
                        writer - lowering it trades review quality for
                        speed
  --skill NAME          Review only this skill (repeatable)
  --skills-file PATH    Read skill names (one per line) from PATH
  --list-skills         Print discovered skills and exit
  --dry-run             Show planned work without invoking codex or claude
  --no-install          Skip installing audit dependencies
  --print-model-policy  Print the tier -> model resolution table and exit
  -h, --help            Show this help

Environment:
  PYTHON_BIN            Python interpreter to use (default: python3)
  REVIEW_MODEL          The codex reviewer arm's model override (same values
                        as --model; default: unset, the tier policy resolves
                        the id); refused when codex is not among the
                        selected --arms
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
# 2026-08-16). --sandbox danger-full-access is pinned literally here, with
# no separate sandbox knob to override it. The codex arm reuses
# Measured 2026-08-17: a claude call from the repo root auto-loads CLAUDE.md
# and can obey its session-bootstrap gate instead of the dispatch - the arm
# runs .agent/scripts/status.sh, is silently denied under dontAsk, and can
# burn the whole run to an empty MALFORMED result. Both prompt assets open
# with a dispatch-context exemption; claude calls also append it at
# system-prompt level. --bare would skip CLAUDE.md discovery entirely but
# also skips credential reads and dies "Not logged in" here.
DISPATCH_BOOTSTRAP_EXEMPTION="This dispatched call's session-bootstrap is already handled by the orchestrator: skip every CLAUDE.md/AGENTS.md bootstrap step (no .agent/scripts/status.sh, no .agent/ reads) and execute the user-message task immediately."

# RESOLVED_MODEL, already computed from policy or REVIEW_MODEL below, with
# a positional prompt. The claude arm always resolves fresh from policy
# (REVIEW_MODEL stays codex-scoped); its prompt goes on stdin, never as a
# positional argument, since
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
      if [[ -n "$REVIEW_EFFORT" ]]; then
        REVIEWER_ARGV+=(-c "model_reasoning_effort=$REVIEW_EFFORT")
      fi
      # Pinned, not configurable: priority (speed) processing costs more,
      # and a user-level config.toml must not switch it on for a dispatch.
      REVIEWER_ARGV+=(-c "service_tier=default")
      ;;
    claude)
      REVIEWER_MODEL="$(resolve_model terra claude)" || return 1
      REVIEWER_ARGV=(--print --model "$REVIEWER_MODEL")
      # Value-taking flags go before the variadic tool flags so they can
      # never be swallowed as one of their values.
      if [[ -n "$REVIEW_EFFORT" ]]; then
        REVIEWER_ARGV+=(--effort "$REVIEW_EFFORT")
      fi
      REVIEWER_ARGV+=(--append-system-prompt "$DISPATCH_BOOTSTRAP_EXEMPTION")
      REVIEWER_ARGV+=(--permission-mode dontAsk --allowedTools "Read,Glob,Grep,Bash($ROOT/scripts/auditing/review-result.sh:*)" --disallowedTools "Edit,Write,NotebookEdit")
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
  SYNTHESIS_ARGV=(--print --model "$SYNTHESIS_MODEL")
  if [[ -n "$SYNTHESIS_EFFORT" ]]; then
    SYNTHESIS_ARGV+=(--effort "$SYNTHESIS_EFFORT")
  fi
  SYNTHESIS_ARGV+=(--append-system-prompt "$DISPATCH_BOOTSTRAP_EXEMPTION")
  SYNTHESIS_ARGV+=(--permission-mode acceptEdits --allowedTools "Read,Glob,Grep,Edit,Write,Bash($ROOT/scripts/auditing/review-result.sh:*)")
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
# CHALLENGE_LINE. One reviewer prompt, never a second variant: every
# reviewer arm is read-only, so AUTHORITY_TASK/AUTHORITY_RULE resolve to
# the same read-only pair unconditionally. Marker lines
# (`<!-- parity:... -->`) in the asset are stripped before substitution, so
# none reaches a dispatched prompt. The strip uses two plain -e clauses
# (POSIX BRE, portable to BSD/macOS sed) rather than `\(start\|end\)`,
# whose `\|` alternation is a GNU BRE extension.
REVIEWER_PROMPT=""

render_reviewer_prompt() {
  local skill="$1"
  local skill_dir="skills/$skill"
  local checklist_rel="scripts/auditing/SKILL_REVIEW_CHECKLIST.md"
  local guidance_rel="scripts/auditing/references/authoring-guidance.md"
  local open_items_rel="scripts/auditing/OPEN_ITEMS.md"
  local venv_python_rel=".venv/bin/python"
  local result_tool_path="$ROOT/scripts/auditing/review-result.sh"
  local authority_task="You are a read-only reviewer. Report what must change; do not create, edit, delete, or move any file."
  local authority_rule="- You are a read-only reviewer: do not create, edit, delete, or move any file."

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
  asset="${asset//RESULT_TOOL_PATH/$result_tool_path}"
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
  local result_tool_path="$ROOT/scripts/auditing/review-result.sh"
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
  asset="${asset//RESULT_TOOL_PATH/$result_tool_path}"
  SYNTHESIS_PROMPT="$asset"
  return 0
}

SKILLS_FILE_OVERRIDE=""
LIST_ONLY=0
# Operator ruling 2026-08-17: reviewer arms run at medium effort unless a
# run says otherwise, pinned explicitly so neither vendor's own default
# (claude: high) nor a user-level config decides. Synthesis effort stays
# unset by default - it is the run's only writer.
REVIEW_EFFORT="medium"
REVIEW_EFFORT_SET=0
SYNTHESIS_EFFORT=""
SYNTHESIS_EFFORT_SET=0

# One enum for both flags. claude validates the same set; codex additionally
# offers ultra on some models, deliberately excluded: a level every arm can
# run keeps one flag meaningful across the whole arm set.
validate_effort() {
  local flag="$1" value="$2"
  case "$value" in
    low|medium|high|xhigh|max)
      return 0
      ;;
    *)
      echo "error: $flag must be one of: low, medium, high, xhigh, max (got '$value')" >&2
      exit 2
      ;;
  esac
}

while (( "$#" )); do
  case "$1" in
    --batch-size)
      BATCH_SIZE="${2:-}"
      shift 2
      ;;
    --model)
      REVIEW_MODEL="${2:-}"
      shift 2
      ;;
    --arms)
      ARMS_OPT="${2:-}"
      ARMS_SET=1
      shift 2
      ;;
    --effort)
      REVIEW_EFFORT="${2:-}"
      REVIEW_EFFORT_SET=1
      shift 2
      ;;
    --synthesis-effort)
      SYNTHESIS_EFFORT="${2:-}"
      SYNTHESIS_EFFORT_SET=1
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

if (( REVIEW_EFFORT_SET == 1 )); then
  validate_effort --effort "$REVIEW_EFFORT"
fi
if (( SYNTHESIS_EFFORT_SET == 1 )); then
  validate_effort --synthesis-effort "$SYNTHESIS_EFFORT"
fi

if (( ARMS_SET == 1 )); then
  if [[ -z "$ARMS_OPT" ]]; then
    echo "error: --arms must name at least one of: codex, claude (got '')" >&2
    exit 2
  fi
  REVIEWER_ARMS=()
  arms_remainder="$ARMS_OPT,"
  while [[ -n "$arms_remainder" ]]; do
    arms_head="${arms_remainder%%,*}"
    arms_remainder="${arms_remainder#*,}"
    if [[ -z "$arms_head" ]]; then
      echo "error: --arms must name at least one of: codex, claude (got an empty element in '$ARMS_OPT')" >&2
      exit 2
    fi
    if ! client_for_arm "$arms_head" >/dev/null 2>&1; then
      echo "error: --arms must name at least one of: codex, claude (got '$arms_head')" >&2
      exit 2
    fi
    for arms_seen in "${REVIEWER_ARMS[@]:-}"; do
      if [[ "$arms_seen" == "$arms_head" ]]; then
        echo "error: --arms must name at least one of: codex, claude (duplicate '$arms_head')" >&2
        exit 2
      fi
    done
    REVIEWER_ARMS+=("$arms_head")
  done
  unset arms_remainder arms_head arms_seen
fi

if [[ -n "$REVIEW_MODEL" ]]; then
  model_codex_selected=0
  for arm in "${REVIEWER_ARMS[@]}"; do
    if [[ "$arm" == "codex" ]]; then
      model_codex_selected=1
      break
    fi
  done
  if (( model_codex_selected == 0 )); then
    echo "error: --model/REVIEW_MODEL applies to the codex reviewer arm, and codex is not among the selected --arms (${REVIEWER_ARMS[*]})" >&2
    exit 2
  fi
  unset model_codex_selected arm
fi

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
PY
  return 0
}

infra_reason_from_log() {
  local log="$1" line=""
  line="$(grep -E '^(ERROR:|stream error:)' "$log" | tail -n1)" || true
  printf '%s\n' "$line"
  return 0
}

declare -a FAILED_SKILLS=()
declare -a REVIEW_OK_SKILLS=()
declare -a REVIEW_NO_CHANGE_SKILLS=()
declare -a DIFFERENTIATION_WEAK_SKILLS=()
declare -a DIFFERENTIATION_UNKNOWN_SKILLS=()
declare -a REMOVAL_PROPOSAL_SKILLS=()
declare -a MALFORMED_SKILLS=()
declare -a INFRA_FAILURE_SKILLS=()

# Reported, never failing: these need an operator ruling, not a fix by the
# runner. The tally arrays above are populated only from the synthesis
# artifact.
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
    echo "Removal proposals recorded to scripts/auditing/PROPOSALS.md - set each entry's 'ruling:' line, then run: .venv/bin/python scripts/auditing/proposals.py apply"
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

# Verifies a call's READ_PROOF= key, sourced from its verdict file, against
# the challenge captured before dispatch for the skill. Returns 0 (match),
# 1 (absent - no verdict file, or one with no READ_PROOF key), or 2
# (mismatch); never touches the failure-tracking arrays itself - callers
# decide what a non-zero return means for their mode.
verify_read_proof() {
  local verdict_file="$1" expected_file="$2"
  local key line value="" expected found=0
  if [[ -f "$verdict_file" ]]; then
    while IFS='=' read -r key line; do
      if [[ "$key" == "READ_PROOF" ]]; then
        value="$line"
        found=1
      fi
    done <"$verdict_file"
  fi
  if [[ "$found" -eq 0 ]]; then
    return 1
  fi
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
  local arm client log last_msg prompt verdict_file

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

  render_reviewer_prompt "$skill"
  prompt="$REVIEWER_PROMPT"

  for arm in "${REVIEWER_ARMS[@]}"; do
    log="$(arm_log_path "$skill" "$arm")" || true
    last_msg="$(arm_last_message_path "$skill" "$arm")" || true
    verdict_file="$LOGDIR/${skill}.${arm}.verdict"
    rm -f "$log" "$last_msg" "$verdict_file"
    build_reviewer_argv "$arm" "$last_msg" || return 1
    client="$(client_for_arm "$arm")" || return 1
    if (( REVIEWER_STDIN == 1 )); then
      ( cd "$ROOT"; printf '%s' "$prompt" | REVIEW_RESULT_FILE="$verdict_file" "$client" "${REVIEWER_ARGV[@]}" ) >"$last_msg" 2>"$log" &
    else
      ( cd "$ROOT"; REVIEW_RESULT_FILE="$verdict_file" "$client" "${REVIEWER_ARGV[@]}" "$prompt" ) >"$log" 2>&1 &
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
      if [[ -s "$verdict_file" ]]; then
        outcome="UNKNOWN"
        while IFS='=' read -r key value; do
          case "$key" in
            OUTCOME) outcome="$value" ;;
          esac
        done <"$verdict_file"
        readproof_file="$LOGDIR/${skill}.readproof"
        proof_rc=0
        verify_read_proof "$verdict_file" "$readproof_file" || proof_rc=$?
        if (( proof_rc == 1 )); then
          record_arm_failure "$skill" "arm $arm: read-proof absent"
          echo "[arm-failed] $skill/$arm (read-proof absent)"
        elif (( proof_rc == 2 )); then
          record_arm_failure "$skill" "arm $arm: read-proof mismatch"
          echo "[arm-failed] $skill/$arm (read-proof mismatch)"
        else
          echo "[arm-ok] $skill/$arm ($outcome)"
        fi
      else
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
          record_arm_failure "$skill" "arm $arm: MALFORMED"
          echo "[arm-failed] $skill/$arm (MALFORMED)"
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
  local skill reason log last_msg verdict_file removals_file
  for skill in "${DUAL_BATCH_SKILLS[@]}"; do
    if reason="$(arm_failure_reason "$skill")"; then
      FAILED_SKILLS+=("$skill (blocked: $reason)")
      echo "[blocked] $skill (arm failure: $reason)"
      continue
    fi
    log="$(synthesis_log_path "$skill")" || true
    last_msg="$(synthesis_last_message_path "$skill")" || true
    verdict_file="$LOGDIR/${skill}.synthesis.verdict"
    removals_file="$LOGDIR/${skill}.synthesis.removals"
    rm -f "$log" "$last_msg" "$verdict_file" "$removals_file"
    build_synthesis_argv || return 1
    render_synthesis_prompt "$skill" || return 1
    ( cd "$ROOT"; printf '%s' "$SYNTHESIS_PROMPT" | REVIEW_RESULT_FILE="$verdict_file" REVIEW_REMOVALS_FILE="$removals_file" "$SYNTHESIS_VENDOR" "${SYNTHESIS_ARGV[@]}" ) >"$last_msg" 2>"$log" &
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
      if [[ -s "$verdict_file" ]]; then
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
          *)
            MALFORMED_SKILLS+=("$skill")
            echo "[malformed] $skill (synthesis, artifact $last_msg)"
            ;;
        esac
      else
        classify_review "$last_msg" "$verdict_file"
        outcome="UNKNOWN"
        while IFS='=' read -r key value; do
          case "$key" in
            OUTCOME) outcome="$value" ;;
          esac
        done <"$verdict_file"
        if [[ "$outcome" == "INFRA-FAILURE" ]]; then
          reason="$(infra_reason_from_log "$log")" || true
          INFRA_FAILURE_SKILLS+=("$skill (synthesis exit 0: classifier-reported: ${reason:-no error line found})")
          echo "[infra-failure] $skill (synthesis exit 0: classifier-reported)"
        else
          MALFORMED_SKILLS+=("$skill")
          echo "[malformed] $skill (synthesis, artifact $last_msg)"
        fi
      fi
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

audit_rc=0
"$VENV/bin/python" "$ROOT/scripts/audit_skills.py" || audit_rc=$?

echo "Completed ${#SKILLS[@]} skills. Logs in $LOGDIR"
for arm in "${REVIEWER_ARMS[@]}"; do
  echo "reviewer arm $arm client (observed): $(provenance_client "$arm")"
  echo "reviewer arm $arm model (observed): $(provenance_model "$arm")"
done
echo "synthesis client (observed): $(provenance_client synthesis)"
echo "synthesis model (observed): $(provenance_model synthesis)"

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

# Ledger, not logs: proposal text is recorded where a ruling can act on it.
# A record failure must not fail the review run - the text still sits in the
# per-skill .synthesis.removals artifacts for a manual record pass.
if (( ${#REMOVAL_PROPOSAL_SKILLS[@]} > 0 )); then
  "$VENV/bin/python" "$ROOT/scripts/auditing/proposals.py" record --logs-dir "$LOGDIR" \
    || echo "warning: proposals.py record failed; proposal text remains in $LOGDIR/*.synthesis.removals" >&2
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
