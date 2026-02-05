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

## Evidence Inventory

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

## Accessibility (Visual)

- Focus visibility: <ok|concerns>
- Contrast concerns: <none|list>
- Text scaling/wrapping: <ok|concerns>

## Responsive + State Coverage

- Breakpoints: Mobile <ok|issues>, Tablet <ok|issues>, Desktop <ok|issues>
- States: default <ok|missing>, hover <ok|missing>, focus (keyboard) <ok|missing>, active/pressed <ok|missing>, disabled <ok|missing>, loading <ok|missing>, error <ok|missing>, empty/no-data <ok|missing>
- Coverage gaps: <list missing states/viewport/theme>

## Issues (With Severity)

- [ ] (<blocker|major|minor|nit>) <issue> - evidence: <where>

## Retest Plan

- Needed evidence: <state/viewport/theme>
- Steps to capture: <how>
EOF2

echo "Wrote: $OUT" >&2
