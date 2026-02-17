# Runtime Adapter: Claude

Use this reference when the host runtime is Claude Code/Claude-compatible.

## Dispatch Pattern

The exact API varies by host. Keep packet content identical to the controller packet contract:

- read-first files
- allowed/forbidden paths
- claim set
- acceptance criteria
- no scope expansion
- non-interactive stop behavior (`QUESTIONS`)
- no controller-verification commands run by worker

## Example Shape

```text
Task: <one sentence outcome>
Scope:
- Allowed: <paths>
- Forbidden: <paths>
Claim set:
- <paths>
Inputs/evidence:
- <errors/tests/logs/repro>
Constraints:
- Stop on ambiguity and output QUESTIONS.
- Do not refactor unrelated code.
Deliverable:
- Root cause
- Files changed
- Patch summary
- Recommended verification commands
```

## Mode Notes

- `single-worker`: one worker task.
- `queued-serial`: one worker at a time with barrier + verification each cycle.
- `true-parallel`: concurrent workers only with confirmed isolation and disjoint claims.
- `prompt-parallel`: prebuild packets, execute sequentially.

## Reliability Guidance

- Keep reviewer passes read-only.
- Enforce controller-owned verification and integration gate.
- Use worktree-per-task when running true-parallel on shared repositories.
