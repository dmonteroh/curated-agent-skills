#!/usr/bin/env bash
set -euo pipefail

die() {
  printf 'review-result.sh: %s\n' "$1" >&2
  exit 1
}

status=""
read_proof=""
differentiation=""
removals=""
have_differentiation=0
have_removals=0
have_read_proof=0

while [ $# -gt 0 ]; do
  case "$1" in
    --status)
      status="$2"
      shift 2
      ;;
    --read-proof)
      case "$2" in
        *$'\n'*)
          die "--read-proof must not contain a newline"
          ;;
      esac
      read_proof="$2"
      have_read_proof=1
      shift 2
      ;;
    --differentiation)
      differentiation="$2"
      have_differentiation=1
      shift 2
      ;;
    --removals)
      removals="$2"
      have_removals=1
      shift 2
      ;;
    --questions)
      shift 2
      ;;
    *)
      die "unknown flag: $1"
      ;;
  esac
done

if [ -z "${REVIEW_RESULT_FILE:-}" ]; then
  die "REVIEW_RESULT_FILE is required"
fi

case "$status" in
  no-change|changed|questions)
    ;;
  *)
    die "--status must be one of: no-change, changed, questions (got: $status)"
    ;;
esac

if [ "$status" = "questions" ]; then
  if [ "$have_differentiation" -eq 1 ]; then
    die "--differentiation is not allowed for --status questions"
  fi
  if [ "$have_removals" -eq 1 ]; then
    die "--removals is not allowed for --status questions"
  fi
else
  if [ "$have_differentiation" -ne 1 ]; then
    die "--differentiation is required for --status $status (accepted values: strong, weak)"
  fi
  if [ "$have_removals" -ne 1 ]; then
    die "--removals is required for --status $status"
  fi
  case "$differentiation" in
    strong|weak)
      ;;
    *)
      die "--differentiation must be one of: strong, weak (got: $differentiation)"
      ;;
  esac
fi

outcome="$(printf '%s' "$status" | tr '[:lower:]' '[:upper:]')"

if [ "$status" = "questions" ]; then
  diff_out="None"
  removal_out="0"
else
  diff_out="$(printf '%s' "$differentiation" | tr '[:lower:]' '[:upper:]')"
  trimmed_removals="$(printf '%s' "$removals" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  lower_removals="$(printf '%s' "$trimmed_removals" | tr '[:upper:]' '[:lower:]')"
  if [ "$lower_removals" = "none" ]; then
    removal_out="0"
  else
    removal_out="1"
  fi
fi

tmp="${REVIEW_RESULT_FILE}.tmp.$$"
{
  printf '%s\n' "OUTCOME=$outcome"
  printf '%s\n' "DIFFERENTIATION=$diff_out"
  printf '%s\n' "REMOVAL_PROPOSALS=$removal_out"
  if [ "$have_read_proof" -eq 1 ]; then
    printf '%s\n' "READ_PROOF=$read_proof"
  fi
} >"$tmp"
mv -f "$tmp" "$REVIEW_RESULT_FILE"
