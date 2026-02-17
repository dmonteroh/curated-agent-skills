# Runtime Adapter: Codex

Use this reference when the host runtime is Codex CLI/Codex-compatible.

## Dispatch Pattern

```sh
codex exec -s workspace-write -C <task_workdir> "
Task: <one sentence outcome>

Read-first:
- <paths>

Scope:
- Allowed: <paths>
- Forbidden: <paths>

Claim set (MUST NOT VIOLATE):
- You may only modify: <explicit files/dirs>

Constraints:
- Non-interactive: if blocked/ambiguous, STOP and output QUESTIONS.
- Do not expand scope or refactor unrelated code.
- Preserve public APIs unless explicitly instructed.
- Do not run verification commands; recommend them only.

Inputs/evidence:
- <errors/tests/logs/repro>

Acceptance criteria:
- [ ] <criterion>

Deliverable:
- Root cause
- Files changed (exact list)
- Patch summary
- Recommended verification commands
- Risks/follow-ups
- QUESTIONS if blocked
"
```

## Mode Notes

- `single-worker`: one `codex exec` run.
- `queued-serial`: loop tasks in controller order; run barrier + verification after each.
- `true-parallel`: run one `codex exec` per task/worktree concurrently only if isolation is confirmed.
- `prompt-parallel`: prepare all packets first, then run sequentially.

## Sandbox Guidance

- Prefer least privilege (`read-only` -> `workspace-write` -> `danger-full-access`).
- Use per-task working directories (`-C <worktree>`) in true-parallel mode.
- Avoid background side effects not captured in worker reports.
