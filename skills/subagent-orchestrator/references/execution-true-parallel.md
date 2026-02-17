# Execution Mode: True Parallel

## Use This Mode When

- Runtime supports isolated concurrent worker sessions.
- Task claim sets are disjoint.
- Repository workflow supports parallel branches/worktrees.

If any prerequisite fails, fall back to `execution-queued-serial.md`.

## Mandatory Preconditions

- Isolation confirmed for concurrent workers.
- No overlapping claim sets across concurrent tasks.
- Worktree strategy prepared (`task -> worktree path -> branch`).
- Integration order and cleanup plan defined before dispatch.

## Steps

### 1) Prepare Parallel Task Set

Select only tasks with disjoint claims and no hard dependencies.

Output: parallel-ready task subset.

### 2) Assign Worktrees

Use one worktree per parallel task when working in the same repository.

Each packet must include:

- worktree path
- branch name
- task claim set

Output: task-to-worktree mapping.

### 3) Dispatch Concurrent Workers

- Dispatch one worker per task/worktree.
- Keep packets strict and non-interactive.
- Worker scope must remain claim-bounded.

Output: per-task worker reports.

### 4) Global Barrier

Before any verification:

- confirm all concurrent workers exited
- confirm no remaining active worker sessions

Output: barrier clearance.

### 5) Verification + Integration

- Run task-level verification as needed.
- Integrate in planned order.
- Run full project quality bar.

Output: integration result.

### 6) Cleanup

- Remove temporary worktrees/branches only after successful integration.

Output: cleanup summary.

## Decision Points

- If overlap is detected at any point, stop concurrency and continue in queued-serial mode.
- If integration conflicts exceed expected scope, collapse domains and re-run as a single coordinated task.
