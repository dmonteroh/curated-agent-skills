# Execution Mode: True Parallel

## Use This Mode When

- Runtime supports isolated concurrent worker sessions.
- Task claim sets are disjoint.
- Repository workflow supports parallel branches/worktrees.

If any prerequisite fails, fall back to `execution-queued-serial.md`.

## Mandatory Preconditions

- Isolation confirmed for concurrent workers.
- No overlapping claim sets across concurrent tasks, checked on every write surface rather than on file paths alone (`claim-sets.md`).
- Contract artifacts for every boundary two concurrent tasks meet at, written and owned by the controller before dispatch.
- Worktree strategy prepared (`task -> worktree path -> branch`).
- Integration order and cleanup plan defined before dispatch.

## Steps

### 1) Prepare Parallel Task Set

Select only tasks with disjoint claims and no hard dependencies. Tasks in the never-parallel class — destructive commands, migrations, writes to a shared table, customer-visible production changes — stay out of the subset and run alone behind their human gate.

Output: parallel-ready task subset, and the gated tasks held back with their ordering.

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

A task that ran in its own worktree with disjoint claims may take its task-level verification early, once its own session and authorised processes have stopped (Hard Invariant 3). The barrier below gates everything else: shared-surface verification and integration.

Before that:

- confirm all concurrent workers exited
- confirm no remaining active worker sessions
- confirm the processes those workers started — servers, builds, watchers, backfills, deploys — have stopped or been waited on, and their outcomes recorded

Output: barrier clearance.

### 5) Verification + Integration

- Run task-level verification as needed.
- Integrate in planned order, one task at a time: replay each onto the current integration head, then re-run the integration checks before the next one starts.
- Hold back any task whose dependency is failing.
- Run full project quality bar over the integrated result.

Output: integration result, with the check outcome recorded per merge.

### 6) Cleanup

- Remove temporary worktrees/branches only after successful integration.

Output: cleanup summary.

## Decision Points

- If overlap is detected at any point, stop concurrency and continue in queued-serial mode.
- If integration conflicts exceed expected scope, collapse domains and re-run as a single coordinated task.
