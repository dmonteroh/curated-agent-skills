# References Index

Load the mode and runtime files that match the current pass. `claim-sets.md`, `packet-templates.md`, `review-convergence.md`, and `worker-surface.md` apply to every orchestration, whatever the mode.

- `execution-single-worker.md`: one worker task with strict scope and barriered verification.
- `execution-queued-serial.md`: multiple tasks, executed one worker session at a time.
- `execution-true-parallel.md`: isolated concurrent workers with disjoint claims and worktree planning.
- `runtime-codex.md`: Codex dispatch (`codex exec`) — model/reasoning policy, packet delivery and output capture (schema enforcement), sandbox guidance, worker skill-layer control, approval recovery.
- `runtime-claude.md`: Claude model/effort policy, dispatch surfaces (native in-session subagents vs CLI subshells), tool access and permission guarantees, packet delivery and output capture, worker skill-layer control, barrier examples, permission recovery.
- `claim-sets.md`: the write surfaces a claim set must enumerate, contract artifacts and aggregator files, worked contrasts, and the pre-dispatch claim-set check.
- `packet-templates.md`: task board, worker packet, reviewer packet, fix packet, and final report templates.
- `review-convergence.md`: why a fresh reviewer per round is load-bearing, how to scope a fix packet, the round cap and its escalation.
- `worker-surface.md`: the execution-surface rules — working directory, authority, tool grant, readiness — each against a worked contrast; the untrusted-context summary shape; the pre-dispatch checklist.
