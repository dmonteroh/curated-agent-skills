# Execution Modes

This reference applies to all runtimes (Claude, Codex, or any agent host). For runtime-specific dispatch syntax see `runtime-claude.md` or `runtime-codex.md`.

## Mode Summary

- `single-worker`: one delegated task, or root cause is still uncertain/shared.
- `queued-serial`: multiple tasks with one worker session at a time.
- `true-parallel`: concurrent workers only when isolation and disjoint claims are confirmed.
- `prompt-parallel`: plan all packets up front, then execute sequentially.

If unsure, choose `single-worker` or `queued-serial`.

## Decision Table

| Condition | Recommended mode |
|---|---|
| Single outcome or shared root cause uncertainty | `single-worker` |
| Multiple tasks but no trusted concurrent isolation | `queued-serial` |
| Confirmed concurrent isolation + disjoint claims | `true-parallel` |
| Need parallel planning only, sequential execution | `prompt-parallel` |

## Workflow (All Modes)

1) Partition domains
- Identify domains that do not share files/state.
- Collapse domains if shared root causes or overlapping claims are detected.

Output: domain map with scope, constraints, and success criteria.

2) Select mode
- Use the decision table above.
- Confirm runtime capabilities before selecting `true-parallel`.

Output: mode decision with rationale.

3) Build packets
- Use `packet-templates.md`.
- Include allowed/forbidden paths, claim set, acceptance criteria, and stop rules.

Output: one approved packet per task.

4) Execute by mode
- `single-worker`: dispatch one packet.
- `queued-serial`: dispatch one packet at a time, verify after each.
- `true-parallel`: dispatch concurrent packets only with worktree-per-task and disjoint claims.
- `prompt-parallel`: dispatch sequentially from prebuilt packets.

Output: per-task worker reports.

5) Barrier + verification
- Ensure all active worker sessions are exited before controller verification.
- Run task-level verification and re-dispatch only narrowed failing scope.

Output: verified task statuses.

6) Integration gate
- Reconcile overlap/conflicts.
- Run full project quality bar.

Output: final integration status.

## Common Mistakes

- Choosing `true-parallel` without confirming session isolation.
- Overlapping claim sets across tasks.
- Running controller verification before a full worker-session barrier.
- Re-dispatching broad scope instead of the smallest failing slice.
