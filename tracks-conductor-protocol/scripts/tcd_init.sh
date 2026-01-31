#!/usr/bin/env sh
set -eu

# Initialize SDD/CDD work-management structure (directories + index blocks).
#
# Defaults match existing protocol skills in this repo but can be overridden.

project_dir="${TCD_PROJECT_DIR:-docs/project}"
todo_dir="${TCD_TODO_DIR:-$project_dir/to-do}"
tasks_dir="${TCD_TASKS_DIR:-$project_dir/tasks}"
tracks_dir="${TCD_TRACKS_DIR:-$project_dir/tracks}"
futures_dir="${TCD_FUTURES_DIR:-$project_dir/futures}"

work_index="${TCD_WORK_INDEX:-$project_dir/work_index.md}"
task_status="${TCD_TASK_STATUS:-$project_dir/task_status.md}"
tracks_registry="${TCD_TRACKS_REGISTRY:-$project_dir/tracks.md}"

context_dir="${TCD_CONTEXT_DIR:-docs/context}"

mkdir -p "$todo_dir" "$tasks_dir" "$tracks_dir" "$futures_dir" "$context_dir"

# Seed task_status.md if missing (kept intentionally minimal; teams can expand).
if [ ! -f "$task_status" ]; then
  cat >"$task_status" <<'EOF'
# Task Status

Source of truth for task lifecycle.

## Draft

## Approved

## In Progress

## Review

## Blocked

## Done (most recent)
EOF
fi

# Seed tracks registry if missing.
if [ ! -f "$tracks_registry" ]; then
  cat >"$tracks_registry" <<'EOF'
# Tracks

Registry of active tracks.

<!-- TCD:TRACK-REGISTRY:START -->
| Track | Title | Status | Links |
| --- | --- | --- | --- |
<!-- TCD:TRACK-REGISTRY:END -->
EOF
fi

# Seed work index with managed blocks if missing.
if [ ! -f "$work_index" ]; then
  cat >"$work_index" <<'EOF'
# Work Index

Deterministic index for intake, tasks, tracks, and futures.
Only rewrite inside the managed blocks.

<!-- TCD:INTAKE:START -->
| ID | Title | Status | Date | Owner | Links | Track | Tags |
| --- | --- | --- | --- | --- | --- | --- | --- |
<!-- TCD:INTAKE:END -->

<!-- TCD:TASKS:START -->
| ID | Title | Status | Seq | Date | Links | Track | ADRs | Futures |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- TCD:TASKS:END -->

<!-- TCD:TRACKS:START -->
| Track | Title | Status | Owner | Links | ADRs | Futures |
| --- | --- | --- | --- | --- | --- | --- |
<!-- TCD:TRACKS:END -->

<!-- TCD:FUTURES:START -->
| ID | Topic | Status | Strategy | Trigger | Links |
| --- | --- | --- | --- | --- | --- |
<!-- TCD:FUTURES:END -->
EOF
fi

# Seed CDD stubs if missing.
if [ ! -f "$context_dir/product.md" ]; then
  cat >"$context_dir/product.md" <<'EOF'
# Product

## One-liner

<what are we building?>

## Users

<who is this for?>

## Goals / Success metrics

<what does success look like?>
EOF
fi

if [ ! -f "$context_dir/tech-stack.md" ]; then
  cat >"$context_dir/tech-stack.md" <<'EOF'
# Tech Stack

## Languages / frameworks

...

## Data stores

...

## Deployment

...
EOF
fi

if [ ! -f "$context_dir/workflow.md" ]; then
  cat >"$context_dir/workflow.md" <<'EOF'
# Workflow

## How we work (CDD + SDD)

- Context -> Spec & Plan -> Implement -> Verify

## Quality gates

- Tests, review, verification protocol, indexing updates
EOF
fi

echo "OK: initialized work structure under $project_dir"
