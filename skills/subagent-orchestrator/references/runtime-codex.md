# Runtime Adapter: Codex

Use this reference when the host runtime is Codex CLI/Codex-compatible.

## Model and Reasoning Policy

- Default model: the runtime's current stable Codex model ID.
- Default reasoning effort: `medium`.
- Use `high` or `xhigh` only after explicit user input/approval for increased cost.

Recommended commands:

```sh
# Default (required baseline)
codex exec -m <codex_model_id> -c model_reasoning_effort="medium" -s workspace-write -C <task_workdir> "<packet>"

# Low-cost pass (triage/simple checks)
codex exec -m <codex_model_id> -c model_reasoning_effort="low" -s workspace-write -C <task_workdir> "<packet>"

# High-depth pass (ONLY with explicit user input)
codex exec -m <codex_model_id> -c model_reasoning_effort="high" -s workspace-write -C <task_workdir> "<packet>"

# Extra-high pass (ONLY with explicit user input)
codex exec -m <codex_model_id> -c model_reasoning_effort="xhigh" -s workspace-write -C <task_workdir> "<packet>"
```

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

## Permission-Error Recovery

If worker runs fail with permission errors (for example `Permission denied` while listing/reading workspace files):

1. Retry with explicit working root: include `-C <repo_root_or_worktree>`.
2. If still blocked, use skip-permissions mode with explicit user approval:

```sh
codex exec --dangerously-bypass-approvals-and-sandbox -m <codex_model_id> -c model_reasoning_effort="medium" -C <task_workdir> "<packet>"
```

3. Record in the worker report that permissions were bypassed and why.
