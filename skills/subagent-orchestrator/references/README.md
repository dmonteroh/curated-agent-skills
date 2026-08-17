# References Index

Load only what matches the current mode/runtime.

- `execution-modes.md`: concise comparison of all four modes (single-worker, queued-serial, true-parallel, prompt-parallel).
- `execution-single-worker.md`: one worker task with strict scope and barriered verification.
- `execution-queued-serial.md`: multiple tasks, executed one worker session at a time.
- `execution-true-parallel.md`: isolated concurrent workers with disjoint claims and worktree planning.
- `execution-prompt-parallel.md`: parallel planning with sequential execution.
- `runtime-codex.md`: Codex-specific dispatch pattern (`codex exec`).
- `runtime-claude.md`: Claude model/effort policy, dispatch packet, mode notes, and permission recovery.
- `claim-sets.md`: the write surfaces a claim set must enumerate, contract artifacts and aggregator files, worked contrasts, and the pre-dispatch claim-set check.
- `packet-templates.md`: task board, worker packet, reviewer packet, fix packet, and final report templates.
- `review-convergence.md`: why a fresh reviewer per round is load-bearing, how to scope a fix packet, the round cap and its escalation.
- `worker-surface.md`: the execution-surface rules — working directory, authority, tool grant, readiness — each against a worked contrast; the untrusted-context summary shape; the pre-dispatch checklist.
