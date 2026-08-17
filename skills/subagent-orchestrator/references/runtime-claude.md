# Runtime Adapter: Claude

Use this reference when the host runtime is Claude Code/Claude-compatible.

## Model and Effort Policy

Aliases (`fable`, `opus`, `sonnet`, `haiku`) resolve to the provider's current recommended model and **change over time**; resolution also differs by provider and by CLI version. Treat an alias as a tier, never as a fixed model. Pin a full model ID (for example `claude-opus-5`) whenever a run must be reproducible or cost-bounded.

Tiers, with the models they resolved to as of 2026-08 (examples, not a contract):

| Alias | Tier | Resolved as of 2026-08 |
|---|---|---|
| `haiku` | Cheapest; simple or mechanical worker tasks | Haiku 4.5 |
| `sonnet` | Balanced default for most orchestration passes | Sonnet 5 |
| `opus` | Frontier agentic coding and the hardest reasoning passes | Opus 5 |
| `fable` | Most capable widely released model | Fable 5 |

Other aliases exist (`best`, `default`, `opusplan`, `sonnet[1m]`, `opus[1m]`). Confirm what the local build actually resolves before relying on a tier for cost or capability:

```sh
(cd /tmp && claude --print --model opus --output-format json -- "Reply with exactly: OK") | jq '.modelUsage | keys'
```

`effort` is the primary token/latency control:

- `low`: fastest and lowest cost; good for simple worker tasks.
- `medium`: balanced depth/cost.
- `high`: **the default** on the Claude API and in Claude Code. Passing `high` is identical to omitting the flag.
- `xhigh`: deeper than `high`; the usual choice for hard coding/agentic passes.
- `max`: only when correctness matters more than cost.

Effort is not universal, and an unsupported level fails **silently**: Haiku 4.5 does not support `effort` at all, and the CLI accepts `--effort` on it with exit 0, no warning, and no behavior change. Do not spend a policy decision on an effort level the target model ignores. As of 2026-08, `xhigh` is available on Fable 5, Opus 5, Opus 4.8, Opus 4.7, and Sonnet 5.

Keep runs CLI-only for this skill.

Recommended commands:

```sh
# Lowest-cost pass (no --effort: Haiku ignores it)
(cd <task_workdir> && claude --print --model haiku --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")

# Default orchestration pass
(cd <task_workdir> && claude --print --model sonnet --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")

# High-depth coding/agentic pass
(cd <task_workdir> && claude --print --model sonnet --effort xhigh --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")

# Deep pass (hardest reasoning)
(cd <task_workdir> && claude --print --model opus --effort xhigh --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "<packet>")
```

The bare `--` before the packet is required, not cosmetic: `--allowedTools` and `--disallowedTools` are variadic, and without the separator they swallow the prompt and the run fails for missing input.

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

## Tool Access and What It Guarantees

| Intent | Flag |
|---|---|
| Skip permission prompts for a known-safe set | `--allowedTools "Read,Write,Edit,Bash,Glob,Grep"` |
| Actually remove tools from the worker's context | `--disallowedTools "Edit,Write,NotebookEdit"`, or `--tools` to set the whole available set |
| Full access | `--permission-mode bypassPermissions` |

`--allowedTools` is an allowlist for **skipping prompts**, not a capability grant and not a restriction. A worker launched with `--allowedTools "Read,Glob,Grep"` still holds `Write`, `Edit`, `NotebookEdit`, and `Bash` in its context and will attempt them.

A read-only reviewer is therefore read-only **because of the permission mode**, not because of the tool flag. Under the default mode a `-p` worker's writes are refused, but the run still exits 0 with `is_error` false and empty stderr — a dispatcher checking only the exit code cannot distinguish a completed review from a worker denied every write it tried. Branch on `.permission_denials` in the JSON envelope instead; it was accurate in every measured run, while the model's prose explanation of the refusal was invented in one.

Two consequences for the controller:

- The guarantee is the caller's to keep. `--permission-mode acceptEdits` with a writable target defeats it: the same read-only allowlist then writes the file. Adding `--disallowedTools "Edit,Write,NotebookEdit"` does not restore it — the worker meets "No such tool available: Write" and reroutes through `Bash`. Closing that path needs an explicit `Bash` denial or a narrowly scoped `Bash(<script>:*)` grant (untested here).
- `--disallowedTools` is still worth using to keep write tools out of context, but it costs turns (the worker spends them attempting workarounds) and it removes the `Write` entry from `.permission_denials`, since a disallowed tool produces a tool_use_error rather than a denial. Choose it for context hygiene, not for a stronger guarantee.

## Working Directory

Claude CLI does not provide a `-C` flag. Run from a subshell:

```sh
(cd <task_workdir> && claude --print --allowedTools "Read,Write,Edit,Bash,Glob,Grep" -- "...")
```

`--add-dir` is not an alternative: it widens which directories a session may read and edit, without relocating the session.

## Dispatch Surface: In-Session Subagents vs CLI Subshells

Recent Claude Code exposes native subagents through the `Agent` tool (renamed from `Task` in v2.1.63; `Task` still works as an alias), runnable from an interactive session, with optional git-worktree isolation for concurrent file-mutating work. Prefer this when the controller is itself a Claude Code session: the harness tracks completion and re-invokes the controller when a worker finishes, so no manual `wait`/polling barrier is needed.

Whether a subagent runs in the background is a precedence chain, not a flat default — an environment variable can force the foreground, and fork mode (which forces the background) is **off** by default in `-p` and in the SDK. A controller that needs one or the other should set it explicitly rather than assume.

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

`wait` covers only the jobs this shell started. A server, watcher, or build a worker launched detached survives it, so the barrier is not clear until those are stopped or waited on as well.

A `claude --print` run also applies its own lifecycle rules inside that barrier: a background shell the worker started is terminated a few seconds after the worker returns its result, while background subagents are waited on under a ten-minute default cap. Long-running worker-spawned work needs its own supervision, not the barrier's.

## Capturing Worker Output

```sh
claude --print --output-format json --allowedTools "..." -- "..." | jq -r '.result'
```

The same envelope carries `.permission_denials`, `.session_id`, `.total_cost_usd`, and `.is_error` — prefer these over parsing the worker's prose.

## Permission-Error Recovery

If worker runs fail with permission errors:

1. Retry from the intended repo/worktree with `(cd <task_workdir> && claude ...)`.
2. Check `.permission_denials` to confirm what was actually refused; the worker's own explanation of a refusal is unreliable.
3. If still blocked, use the runtime's permissions-bypass mode only with explicit user approval:

   ```sh
   (cd <task_workdir> && claude --print --model sonnet --permission-mode bypassPermissions -- "<packet>")
   ```

   `--dangerously-skip-permissions` is equivalent. Note that bypass mode has an interactive acceptance gate: a session that has never accepted it interactively may be refused.

4. Record the bypass decision and reason in the worker report.
