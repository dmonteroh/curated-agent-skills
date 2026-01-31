#!/usr/bin/env sh
set -eu

# Scaffold minimal CDD context artifacts.
# Safe-by-default: creates files only if missing.

context_dir="${CONTEXT_DIR:-docs/context}"
index_file="${CONTEXT_INDEX:-$context_dir/README.md}"

mkdir -p "$context_dir"

if [ ! -f "$context_dir/product.md" ]; then
  cat >"$context_dir/product.md" <<'EOF'
# Product

## One-liner

<what are we building?>

## Users

<who is this for?>

## Problem

<what pain are we solving?>

## Goals / Success metrics

- ...

## Non-goals

- ...

## Open questions

- ...
EOF
fi

if [ ! -f "$context_dir/tech-stack.md" ]; then
  cat >"$context_dir/tech-stack.md" <<'EOF'
# Tech Stack

## Overview

<languages, frameworks, infra targets>

## Data stores

- ...

## Architecture notes

- ...

## Constraints

- ...

## Open questions

- ...
EOF
fi

if [ ! -f "$context_dir/workflow.md" ]; then
  cat >"$context_dir/workflow.md" <<'EOF'
# Workflow

## How we work

- ...

## Quality gates

- code review
- testing
- security checks (as appropriate)

## Release / deploy (if applicable)

- ...

## Open questions

- ...
EOF
fi

start="<!-- CONTEXT-INDEX:START -->"
end="<!-- CONTEXT-INDEX:END -->"

if [ ! -f "$index_file" ]; then
  cat >"$index_file" <<EOF
# Context

$start
| File | Purpose |
| --- | --- |
$end
EOF
else
  if ! grep -qF "$start" "$index_file" || ! grep -qF "$end" "$index_file"; then
    cat >>"$index_file" <<EOF

$start
| File | Purpose |
| --- | --- |
$end
EOF
  fi
fi

echo "OK: initialized $context_dir"
