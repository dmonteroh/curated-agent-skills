---
name: subagent-orchestrator
description: "Decide whether and how to split work across subagents, then orchestrate execution safely with mode selection, claim-set control, barriered verification, and deterministic integration."
metadata:
  category: ai
---

# Subagent Orchestrator
Provides an end-to-end orchestration workflow: partitioning, safe dispatch, barriered verification, and deterministic integration.

## Use this skill when

- Work has 2+ independent tasks that can be partitioned by subsystem/module.
- Disjoint claims (paths/files) can be assigned per task before dispatch.
- Controller-owned verification barriers are required between worker executions.
- Deterministic merge/integration is required across multiple worker outputs.
- Per-task and final quality gates can be defined up front.

## Do not use this skill when

- The work is a single straightforward implementation task.
- Root cause is unknown and requires one deep, shared investigation first.
- Problems are coupled and likely to touch the same files.
- Scope, claim set, or verification cannot be defined.
- Only requirements clarification or option comparison is needed.
- The runtime cannot spawn worker sessions.

## Required Inputs

- Target outcome(s) and constraints.
- Evidence (errors, failing tests, logs, repro).
- Allowed paths, forbidden paths, and candidate claim sets.
- Verification commands and quality bar.
- Runtime capabilities (single session only, or isolated concurrency support).

## Hard Invariants

1. Every task has explicit allowed paths, forbidden paths, and claim set.
2. Concurrency is allowed only with confirmed session isolation and disjoint claims.
3. Verification never runs while any worker session is active.
4. Worker prompts are self-contained and non-interactive; blocked work returns `QUESTIONS`.
5. Controller owns verification, integration, and final completion status.
6. Completion requires passing project quality gates.

## Activation Decision Gate

Before orchestration, answer:

1. Are there at least 2 independent domains?
2. Can each domain have disjoint allowed paths + claim set?
3. Are per-task verification commands and final integration checks defined?
4. Does the runtime support the chosen execution mode?

If any answer is "no", do not orchestrate yet.

## Execution Modes

Select exactly one mode per pass:

- `single-worker`: one task, or root cause is still uncertain/shared. Read `references/execution-single-worker.md`.
- `queued-serial`: multiple tasks, one worker session at a time. Read `references/execution-queued-serial.md`.
- `true-parallel`: isolated concurrent sessions + disjoint claims + worktree plan. Read `references/execution-true-parallel.md`.
- `prompt-parallel`: prepare all packets now, execute sequentially. Read `references/execution-prompt-parallel.md`.

If uncertain, use `single-worker` or `queued-serial`. See `references/execution-modes.md` for a concise mode comparison.

## Runtime Adapter

Load only the runtime guide that matches the host:

- Codex: `references/runtime-codex.md`
- Claude: `references/runtime-claude.md`

## Workflow (Deterministic)

### 0) Partition

Group work by domain, not by symptom.

Examples:

- "auth flow regressions" vs "UI rendering glitches" vs "DB migration failure"
- "test file A failures" vs "test file B failures" (only if they're truly unrelated)

For each candidate domain:

- Define scope (files/modules), success criteria, and constraints.
- Check for shared root causes or overlapping files — if found, collapse into a single domain.

Decision point: if fewer than 2 independent domains can be defined, use `single-worker`.

Output: partition plan listing domain → scope | success criteria | constraints.

### 1) Preflight

- Load required inputs and select execution mode.
- If considering `true-parallel`, preflight worktrees:
  - one worktree per task (`task -> worktree path -> branch`)
  - disjoint claim sets across concurrent tasks
  - integration order and cleanup plan
- If dot-agent files exist, load in this order:
  1. .agent/purpose.md
  2. .agent/memory.md
  3. Last 5-10 entries from .agent/session-log.md
  4. Relevant docs in .agent/docs/

Output: mode decision + preflight notes + initial task board.

### 2) Build Task Board

Record each task with:

- Task ID and outcome.
- Allowed paths, forbidden paths, claim set.
- Inputs/evidence.
- Acceptance criteria.
- Controller-run verification commands.
- Status (`queued | running | needs-info | needs-fix | ready | integrated`).

Output: approved task board with claim-set checks.

### 3) Prepare Packets

- Use `references/packet-templates.md`.
- For implementer packets use `implementer-prompt.md` as a copy-paste base.
- For reviewer packets use `spec-reviewer-prompt.md` and `code-quality-reviewer-prompt.md`.
- Include strict stop rules for ambiguity, scope expansion, and unrelated refactors.

Output: one packet per task.

### 4) Execute Tasks

- Follow the selected mode guide and runtime guide.
- Keep worker scope constrained to claim sets.
- For repetitive orchestration, propose automation scripts only after user confirmation.

Output: per-task worker report (root cause, files changed, recommended verification).

### 5) Barrier and Controller Verification

- Confirm worker sessions are fully exited.
- Run task-level verification commands.
- Re-dispatch only the smallest failing scope with fresh failure evidence.

Output: verified task status and any narrowed follow-up tasks.

### 6) Integration Gate

- Reconcile overlap/conflicts.
- Run full project quality bar.
- Re-dispatch focused fixes if integration verification fails.

Output: final integration result.

### 7) Optional dot-agent Maintenance

If dot-agent files exist:

- Update .agent/memory.md with stable decisions/knowledge.
- Append 2-5 lines to .agent/session-log.md.
- Update .agent/docs/ only when behavior/flows/dependencies changed.

Output: maintenance summary.

## Output Contract

Always return:

- Partition plan (domain → scope | success criteria | constraints).
- Task board summary.
- Per-task report: root cause, files changed, verification commands/results, risks.
- Integration summary: conflicts and final verification.
- dot-agent maintenance summary (when applicable).
- Automation summary (only if user approved script creation).

Use the canonical structure in `references/packet-templates.md` (`Final Report Template`) for consistent reporting.

## Common Failure Modes

- Splitting coupled problems (fixing one invalidates the other's scope).
- Overlapping claims across concurrent tasks.
- Weak packets (missing evidence or acceptance criteria).
- Verification attempted before session barrier.
- Broad re-dispatch that reintroduces overlap.

## References

- `references/README.md`
- `references/execution-modes.md`
- `references/packet-templates.md`
- `references/execution-single-worker.md`
- `references/execution-queued-serial.md`
- `references/execution-true-parallel.md`
- `references/execution-prompt-parallel.md`
- `references/runtime-codex.md`
- `references/runtime-claude.md`
- `references/agent-optimization.md`
- `implementer-prompt.md`
- `spec-reviewer-prompt.md`
- `code-quality-reviewer-prompt.md`
