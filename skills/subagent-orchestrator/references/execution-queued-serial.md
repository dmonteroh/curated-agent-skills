# Execution Mode: Queued Serial

## Use This Mode When

- There are multiple task domains.
- Tasks may be independent, but runtime concurrency is not trusted.
- Deterministic execution is preferred over maximum throughput.

## Steps

### 1) Build Multi-Task Board

Define `T1..Tn` with explicit claim sets, execution surfaces, and verification commands.

Output: task board with queued tasks.

### 2) Sequence Tasks

Choose execution order by dependency/risk:

- dependency-first (read `depends_on` from the board; a task runs after everything it depends on)
- high-risk-first
- low-conflict-first

Output: ordered execution queue.

### 3) Execute One Task Per Session

For each task in order:

1. Dispatch worker.
2. Wait for worker exit, and for any process it started to stop or be waited on.
3. Run controller verification for that task.
4. Update task status.

Never start the next worker until verification step for current task is complete.

Output: per-task verified status.

### 4) Integration Gate

- Before a task integrates: review convergence (`SKILL.md` step 6) for every task that wrote code.
- Recheck overlap/conflicts across all changed files.
- Run full quality bar after all queued tasks complete.
- Re-dispatch only the smallest failing task scope.

Output: integration result.

## Decision Points

- If two tasks repeatedly conflict, collapse them into a single task.
- If a task keeps failing verification, shrink claim set and acceptance criteria before retrying.
- If packet quality is low, pause and rewrite packets before execution.
- If later tasks depend on earlier outputs, update remaining packets before dispatch.
