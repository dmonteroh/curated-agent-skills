#!/usr/bin/env bash
set -euo pipefail

# Scaffold a visual validation report.
# Usage:
#   ./scripts/visual_report.sh "Login modal" docs/qa/visual/VR-YYYY-MM-DD-login-modal.md

SUBJECT="${1:-}"
OUT="${2:-}"

if [ -z "$SUBJECT" ] || [ -z "$OUT" ]; then
  echo "usage: $0 \"<subject>\" <output-path>" >&2
  exit 2
fi

DIR=$(dirname "$OUT")
mkdir -p "$DIR"

DATE=$(date +%F)

cat > "$OUT" <<EOF2
# Visual Validation Report: ${SUBJECT}

Date: ${DATE}
Scope: <pages/components>

## Verdict

<pass|fail|partial|needs-evidence>

## AI-Slop Screen

<clean|flagged (<n>)> - <pattern name>: <where it appears>

## Faked-Surface Check

- <region>: <live|suspect|not observable> - tell: <what raised it> - settles with: <capture>

## Surface Classification

<marketing|app|hybrid> - decided by: <observation>

## Evidence Inventory

Enumerated in scope: <n>; captured: <n>.

- <artifact> (<viewport>, <theme>, <state>, <environment>)

## Goals

- [ ] <goal 1>
- [ ] <goal 2>

## Observations (Objective)

-

## Intended Diffs Observed

-

## Regressions / Unintended Changes

-

## Design Criteria Findings

- <criterion>: <met|not met|not observable> - measured: <value>

## Trunk Test

- What site is this: <answered|not answered>
- What page am I on: <answered|not answered>
- Major sections: <answered|not answered>
- Options at this level: <answered|not answered>
- Position in the hierarchy: <answered|not answered>
- How to search: <answered|not answered>

## Accessibility (Visual)

- Focus visibility: <ok|concerns>
- Contrast concerns: <none|list>
- Text scaling/wrapping: <ok|concerns>

## Responsive + State Coverage

- Breakpoints: Mobile <ok|issues>, Tablet <ok|issues>, Desktop <ok|issues>
- States: default <ok|missing>, hover <ok|missing>, focus (keyboard) <ok|missing>, active/pressed <ok|missing>, disabled <ok|missing>, loading <ok|missing>, error <ok|missing>, empty/no-data <ok|missing>
- Coverage gaps: <list missing states/viewport/theme>

## Issues (With Severity)

- [ ] (<blocker|major|minor|nit>) [product|evidence] <issue> - evidence: <where>

## Retest Plan

- Needed evidence: <state/viewport/theme>
- Steps to capture: <how>

## Completion Gate

- Independent (non-authoring) review returned: <pass|blocking findings>
- Evidence set judged: <complete and current|gaps>
- <Satisfied|Remaining gaps and who accepted them>
EOF2

echo "Wrote: $OUT" >&2
