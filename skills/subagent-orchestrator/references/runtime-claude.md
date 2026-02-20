# Runtime Adapter: Claude

Use this reference when the host runtime is Claude Code/Claude-compatible.

## Model and Effort Policy

- Available orchestration profiles:
  - `haiku-4.5`: low-thinking, lowest-cost passes.
  - `sonnet-4.6`: default profile for most orchestration tasks.
  - `opus`: use only with explicit user approval.
- Keep runs CLI-only for this skill.
- `effort` is the primary token/latency control:
  - `low`: fastest and lowest cost.
  - `medium`: balanced depth/cost (recommended default for orchestrator passes).
  - `high`: deeper reasoning with higher cost/latency.
  - `max`: only when supported by the selected model/build.

Recommended commands:

```sh
# Lowest-cost pass
(cd <task_workdir> && claude --print --model haiku-4.5 --effort low --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")

# Default orchestration pass
(cd <task_workdir> && claude --print --model sonnet-4.6 --effort medium --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")

# High-depth pass
(cd <task_workdir> && claude --print --model sonnet-4.6 --effort high --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")

# Deep pass (only with explicit user approval)
(cd <task_workdir> && claude --print --model opus --effort high --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")
```

Validation note:

- Confirm local CLI support for `--effort` and model IDs.
- If flags differ by build, keep the same policy intent.

## Dispatch Pattern

```sh
claude --print --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "
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

## Tool Access Profiles

| Intent | `--allowedTools` value |
|---|---|
| Read-only (reviewer) | `"Read,Glob,Grep"` |
| Workspace write (implementer) | `"Read,Write,Edit,Bash,Glob,Grep"` |
| Full access | omit `--allowedTools` |

## Working Directory

Claude CLI does not provide a `-C` flag. Run from a subshell:

```sh
(cd <task_workdir> && claude --print --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "...")
```

## Mode Notes

- `single-worker`: one `claude --print` invocation.
- `queued-serial`: dispatch in controller order; barrier + verification after each task.
- `true-parallel`: one `claude --print` per task/worktree concurrently only when isolation and disjoint claims are confirmed.
- `prompt-parallel`: prepare all packets first, then execute sequentially.

## True Parallel Barrier Example

```sh
(cd <worktree1> && claude --print --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet1>") &
(cd <worktree2> && claude --print --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet2>") &
wait  # global barrier: run verification only after all workers exit
```

## Capturing Worker Output

```sh
claude --print --output-format json --allowedTools "..." -- "..." | jq -r '.result'
```

## Permission-Error Recovery

If worker runs fail with permission errors:

1. Retry from the intended repo/worktree with `(cd <task_workdir> && claude ...)`.
2. If still blocked, use the runtime's permissions-bypass mode only with explicit user approval.
3. Example (flag name varies by build):

```sh
(cd <task_workdir> && claude --print --model sonnet-4.6 --permission-mode bypassPermissions -- "<packet>")
```

4. Record the bypass decision and reason in the worker report.
