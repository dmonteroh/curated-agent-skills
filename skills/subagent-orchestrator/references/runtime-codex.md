# Runtime Adapter: Codex

Use this reference when the host runtime is Codex CLI/Codex-compatible.

## Model and Reasoning Policy

- Model IDs move. Confirm what the local build offers with `codex debug models` before pinning one, and prefer that live catalog over any documentation table.
- As of 2026-08 the recommended lineup is `gpt-5.6-sol` (frontier agentic coding), `gpt-5.6-terra` (balanced everyday work), and `gpt-5.6-luna` (fast and affordable). The documented starting point is `gpt-5.6-sol` at `medium` reasoning. `gpt-5.4` and `gpt-5.4-mini` retire from Codex with ChatGPT sign-in on 2026-08-31.
- Reasoning effort is set per model, not per CLI: there is no `--effort` flag, only `-c model_reasoning_effort="<level>"`.
- Default effort is **per model**, not a constant. It is `medium` for the three recommended models, but `gpt-5.5` defaults to `xhigh` — read `default_reasoning_level` from the catalog rather than assuming.
- The ladder runs `low` → `medium` → `high` → `xhigh` → `max` → `ultra`, and the top rungs are model-gated: `max` on `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`; `ultra` on `gpt-5.6-sol` and `gpt-5.6-terra` only. Check `supported_reasoning_levels` before selecting one.
- Use anything above `medium` only after explicit user input/approval for increased cost.

Recommended commands:

```sh
# Default (required baseline)
codex exec -m <codex_model_id> -c model_reasoning_effort="medium" -s workspace-write -C <task_workdir> "<packet>"

# Low-cost pass (triage/simple checks)
codex exec -m <codex_model_id> -c model_reasoning_effort="low" -s workspace-write -C <task_workdir> "<packet>"

# High-depth pass (ONLY with explicit user input)
codex exec -m <codex_model_id> -c model_reasoning_effort="high" -s workspace-write -C <task_workdir> "<packet>"

# Extra-high pass (ONLY with explicit user input; max/ultra are costlier still and model-gated)
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

## Capturing Worker Output

`codex exec` streams progress to stderr and prints **only the final agent message** to stdout, so a redirect already captures the worker report:

```sh
codex exec -s workspace-write -C <task_workdir> "<packet>" > <report_path>
```

Three structured alternatives, when raw text is not enough:

- `-o <path>` / `--output-last-message <path>`: writes the final message to a file and still prints it to stdout — a durable artifact per worker.
- `--json`: turns stdout into a JSONL event stream, giving progress and tool-call visibility rather than just the final message.
- `--output-schema <path>`: constrains the final response to a JSON Schema, so the Deliverable contract is enforced mechanically instead of by prose.

Capture something for every dispatch. A fire-and-forget `codex exec` leaves the controller with no worker report to verify against the claim set.

## Mode Notes

- `single-worker`: one `codex exec` run.
- `queued-serial`: loop tasks in controller order; run barrier + verification after each.
- `true-parallel`: run one `codex exec` per task/worktree concurrently only if isolation is confirmed.
- `prompt-parallel`: prepare all packets first, then run sequentially.

Recent builds also ship an in-process multi-agent layer (spawned agents, bounded concurrency slots). It is a different trade: those agents **share one working directory**, so it provides no filesystem isolation and does not satisfy the disjoint-claims invariant that `true-parallel` depends on. Use one `codex exec` per worktree when isolation is the point.

## Sandbox Guidance

- Prefer least privilege (`read-only` -> `workspace-write` -> `danger-full-access`).
- `codex exec` defaults to `read-only`, so `-s workspace-write` is load-bearing for any worker expected to edit files.
- Use per-task working directories (`-C <worktree>`) in true-parallel mode.
- Avoid background side effects not captured in worker reports.

## Permission-Error Recovery

If worker runs fail with permission errors (for example `Permission denied` while listing/reading workspace files):

1. Retry with explicit working root: include `-C <repo_root_or_worktree>`.
2. If the worker legitimately needs a second writable root, add `--add-dir <dir>` rather than escalating the sandbox.
3. If the failure is that the working root is not a git repository, `--skip-git-repo-check` is the targeted fix — not a permission change.
4. If still blocked, use skip-permissions mode with explicit user approval:

   ```sh
   codex exec --dangerously-bypass-approvals-and-sandbox -m <codex_model_id> -c model_reasoning_effort="medium" -C <task_workdir> "<packet>"
   ```

5. Record in the worker report that permissions were bypassed and why.

Note that `codex exec` accepts no approval-policy flag: `-a`/`--ask-for-approval` applies to the interactive command only. Sandbox mode is the whole control surface for a non-interactive worker.
