#!/usr/bin/env sh
set -eu

# Create/update a deterministic "rehydration snapshot" for agents:
# docs/context/brief.md
#
# Safe-by-default:
# - writes only under docs/context/
# - does not overwrite core context files

context_dir="${CONTEXT_DIR:-docs/context}"
brief_file="${CONTEXT_BRIEF_FILE:-$context_dir/brief.md}"

require_file() {
  [ -f "$1" ] || { echo "missing required file: $1" >&2; exit 1; }
}

mkdir -p "$context_dir"

require_file "$context_dir/product.md"
require_file "$context_dir/tech-stack.md"
require_file "$context_dir/workflow.md"

now_utc="$(date -u +%F)"

cat >"$brief_file" <<EOF
# Context Brief

Generated: $now_utc (UTC)

This file is a **rehydration snapshot** for humans/agents joining work mid-stream.
If anything here conflicts with source context, treat the source files as authoritative:
- $context_dir/product.md
- $context_dir/tech-stack.md
- $context_dir/workflow.md

## What are we building? (one-liner)

<fill from product.md>

## Goals / Non-goals

Goals:
- ...

Non-goals:
- ...

## Key constraints / invariants

- ...

## Current architecture (high level)

- ...

## How we work (workflow + quality gates)

- ...

## Active unknowns / needs confirmation

- ...

## Where to start reading

1) $context_dir/README.md
2) $context_dir/product.md
3) $context_dir/tech-stack.md
4) $context_dir/workflow.md
EOF

echo "OK: wrote $brief_file"

