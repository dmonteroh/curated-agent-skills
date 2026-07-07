# Runtime Adapter: Claude

Use this reference when the host runtime is Claude Code/Claude-compatible.

## Model and Effort Policy

- Available orchestration profiles (aliases are stable; full IDs shown for pinning):
  - `haiku` (`claude-haiku-4-5`): low-thinking, lowest-cost passes and simple/mechanical worker tasks.
  - `sonnet` (`claude-sonnet-5`): balanced default for most orchestration passes.
  - `opus` (`claude-opus-4-8`): most capable; use for the hardest reasoning/agentic passes.
- Keep runs CLI-only for this skill.
- `effort` is the primary token/latency control (Opus/Sonnet 4.7+ support the full ladder):
  - `low`: fastest and lowest cost; good for subagents and simple tasks.
  - `medium`: balanced depth/cost.
  - `high`: deeper reasoning; the recommended minimum for intelligence-sensitive passes.
  - `xhigh`: best for most coding/agentic work (the default in Claude Code); between `high` and `max`.
  - `max`: only when correctness matters more than cost.

Recommended commands:

```sh
# Lowest-cost pass
(cd <task_workdir> && claude --print --model haiku --effort low --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")

# Default orchestration pass
(cd <task_workdir> && claude --print --model sonnet --effort high --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")

# High-depth coding/agentic pass
(cd <task_workdir> && claude --print --model sonnet --effort xhigh --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")

# Deep pass (hardest reasoning)
(cd <task_workdir> && claude --print --model opus --effort xhigh --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")
```

Validation note:

- Confirm local CLI support for `--effort` and model IDs; aliases (`haiku`/`sonnet`/`opus`) resolve to the current release for the build.
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

## Dispatch Surface: In-Session Subagents vs CLI Subshells

Recent Claude Code exposes native subagents through the `Task`/`Agent` tool, runnable from an interactive session — background by default, with optional git-worktree isolation for concurrent file-mutating work. Prefer this when the controller is itself a Claude Code session: the harness tracks completion and re-invokes the controller when a worker finishes, so no manual `wait`/polling barrier is needed.

Use the `claude --print` subshell pattern below when the controller is a plain script/CI step (no interactive session), when targeting a non-Claude host, or when you need explicit shell-level control of concurrency and working directories. The two are interchangeable for this skill's workflow; the invariants (disjoint claims, controller-owned verification barrier) apply to both.

## Mode Notes

- `single-worker`: one subagent, or one `claude --print` invocation.
- `queued-serial`: dispatch in controller order; barrier + verification after each task.
- `true-parallel`: one worker per task/worktree concurrently only when isolation and disjoint claims are confirmed (native subagents with `worktree` isolation, or one `claude --print` per worktree).
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
(cd <task_workdir> && claude --print --model sonnet --permission-mode bypassPermissions -- "<packet>")
```

4. Record the bypass decision and reason in the worker report.
