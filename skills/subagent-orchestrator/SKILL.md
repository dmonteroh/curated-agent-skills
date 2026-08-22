---
name: subagent-orchestrator
description: "Decide whether and how to split work across subagents, then orchestrate execution safely with mode selection, claim-set and execution-surface control, barriered verification, and deterministic integration."
metadata:
  category: ai
---

# Subagent Orchestrator
Each dispatched task carries two controller-decided halves: a claim set (which files the worker may change) and an execution surface (which directory it boots in, what authority it holds there, which capabilities it keeps, and what content it is handed).

## Use this skill when

- Work has 2+ independent tasks that can be partitioned by subsystem/module.
- Disjoint claims (paths/files) can be assigned per task before dispatch.
- Tasks write surfaces beyond files — a database, a shared service, a deploy target, a bound port, a cache, a shared dataset — whose overlap has to be ruled out before any concurrency.
- Controller-owned verification barriers are required between worker executions.
- Deterministic merge/integration is required across multiple worker outputs.
- Per-task and final quality gates can be defined up front.
- Workers will run as separate sessions or processes holding their own working directories, credentials, tool grants, and command layers.
- A dispatched review/fix loop is running unbounded — the same finding keeps bouncing between reviewer and implementer — and needs a cap and a defined exit (workflow step 6).

## Do not use this skill when

- The work is a single straightforward implementation task.
- Root cause is unknown and requires one deep, shared investigation first.
- Problems are coupled and likely to touch the same files.
- Scope, claim set, or verification cannot be defined.
- Only requirements clarification or option comparison is needed.
- The runtime cannot spawn worker sessions.
- The open question is only whether one agent binary is installed or authenticated: that is a readiness check, not an orchestration.

## Required inputs

- Target outcome(s) and constraints.
- Evidence (errors, failing tests, logs, repro).
- Allowed paths, forbidden paths, and candidate claim sets.
- Verification commands and quality bar.
- Effort authorization: worker reasoning effort defaults to `medium` on every vendor; a level above it is selected only when the operator has authorized it here or as standing policy — never by interrupting a running orchestration to ask.
- Runtime capabilities (single session only, or isolated concurrency support).
- For each worker runtime: how it is launched, which directory it may boot in, what authority and tool grant it can be given, and whether it carries its own command/skill layer.

## Hard Invariants

1. Every task has explicit allowed paths, forbidden paths, claim set, and execution surface: working directory, authority tier, and tool grant (`references/worker-surface.md`).
2. Concurrency is allowed only with confirmed session isolation and disjoint claims.
3. Controller verification reads only quiet surfaces: it never runs while any worker session or worker-started process that writes the surfaces under verification is active. With per-task worktrees and disjoint claims a finished task may be verified while siblings run; without that isolation, verification waits for the global barrier.
4. Worker prompts are self-contained and non-interactive; blocked work returns `QUESTIONS`.
5. Controller owns verification, integration, and final completion status.
6. Completion requires passing project quality gates.
7. No worker boots in the controller's own instruction or state directory — started there, it ingests the controller's instructions as task context. Review and concurrent work get an isolated copy, never the live tree.
8. Any task whose worker writes code ends in a review-class step that reads the resulting diff before integration. A task already gated by its own validator — a build or test task — needs no second reviewer.

## Activation Decision Gate

Two checks, at two moments.

Entry — before step 0:

1. Are there at least 2 candidate domains that look independent? Fewer is not a stop: delegate as `single-worker`, or stand down per `Do not use this skill when`.
2. Can disjoint allowed paths and claim sets plausibly be assigned per domain? If not, investigate first (`single-worker`) and partition after.

Dispatch — answered by the end of step 2, before any worker runs:

3. Are per-task verification commands and final integration checks defined?
4. Did the preflight probe confirm the runtime supports the selected execution mode?
5. For every task that writes a surface in the never-parallel class (`## Claim Sets`), is the explicit human gate recorded on the board?

If any dispatch answer is "no", do not dispatch yet.

## Execution Modes

Select exactly one mode per pass:

- `single-worker`: one task, or root cause is still uncertain/shared. Read `references/execution-single-worker.md`.
- `queued-serial`: multiple tasks, one worker session at a time. Read `references/execution-queued-serial.md`.
- `true-parallel`: isolated concurrent sessions + disjoint claims + worktree plan. Read `references/execution-true-parallel.md`.

If uncertain, use `single-worker` or `queued-serial`.

## Runtime Adapter

Load only the runtime guide that matches the host:

- Codex: `references/runtime-codex.md`
- Claude: `references/runtime-claude.md`

## Claim Sets

A claim set names every surface the task writes, not only the files it edits. Two tasks may run concurrently only when their write surfaces are disjoint on all dimensions at once: file paths, but also databases and schemas, tables, migrations, long-lived services, deploy targets, bound ports, caches, and shared datasets. The full dimension list, worked contrasts, and a pre-dispatch claim-set check: `references/claim-sets.md`.

Five rules ride on that definition, each with its worked contrast in the reference:

- **A never-parallel class.** Destructive commands, schema migrations, two tasks writing one table, and anything customer-visible in production are never admitted to concurrency at all, whatever the disjointness check says: the gated task runs alone, behind an explicit human decision recorded on the board before it runs.
- **Re-derive the partition mid-flight.** When a running task invalidates the plan, pause its dependents and re-partition rather than letting the fan-out finish against a stale split.
- **Contract artifacts are a third ownership class.** The controller writes the boundary where two tasks meet, owns it, and issues it read-first and forbidden to modify.
- **Aggregator files leak out of any partition.** Anything whose content lists its siblings gets one owner, or leaves every claim set for a controller pass after integration.
- **Stub to unblock.** A task gated on another's output gets a stub shaped by the contract artifact, recorded on the board, replaced at integration.

## Workflow

### 0) Partition

Group work by domain, not by symptom.

Prefer domains that cut through the stack over domains that each take one layer: a layer-per-task split creates inter-layer dependencies by construction, so it yields fewer genuinely independent domains than a feature-per-task split of the same work.

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
- Invoke each distinct worker runtime once to confirm it actually runs, and record the outcome in the preflight notes. A worker that cannot run changes the mode decision, not just its packet.
- Assign each task a working directory, an authority tier, and a tool grant. If any task would boot a worker in the controller's own tree, resolve that here — copy or keep the task in-session — not at dispatch time.
- If considering `true-parallel`, preflight worktrees:
  - one worktree per task (`task -> worktree path -> branch`)
  - disjoint claim sets across concurrent tasks
  - integration order and cleanup plan

Output: mode decision + preflight notes + initial task board.

### 2) Build Task Board

Record each task with:

- Task ID and outcome.
- Allowed paths, forbidden paths, claim set.
- Non-file write surfaces claimed: databases and schemas, tables, migrations, services, deploy targets, ports, caches, datasets — `none` where the task writes none.
- Human gate, for any task whose surfaces put it in the never-parallel class: the recorded decision and who took it.
- Contract artifacts the task reads, marked controller-owned and read-only, and any stub it is handed against the implementation the stub stands in for.
- Execution surface: working directory or worktree, authority tier, tool grant, command layer on/off.
- Runtime probe result, carried over from preflight.
- Long-running processes the task is authorised to start, and who stops them before the barrier.
- Inputs/evidence.
- Acceptance criteria.
- Controller-run verification commands.
- Review task, for any task whose worker writes code: reviewer scope, inputs, and the diff it reads. Once review starts, the rounds spent and the findings still open.
- `depends_on`: the tasks this one must integrate after, if any. This is what dependency-first ordering and the integration gate read.
- `rollback_plan`, for any task whose integration is not trivially revertible.
- Status (`queued | running | needs-info | needs-fix | ready | integrated`).

Output: approved task board with claim-set checks (`references/claim-sets.md`).

### 3) Prepare Packets

- Use `references/packet-templates.md` for the worker, reviewer, fix and final-report shapes.
- A packet is complete when it carries all of: a one-sentence outcome, read-first paths, an allowed/forbidden claim set, its execution surface, inputs and evidence, acceptance criteria, the controller-run verification commands, and the deliverable shape. A packet missing any of these is a weak packet — fix it before dispatch.
- Each packet stands alone. A worker must be able to finish without opening the plan or brief the task was cut from; carry a pointer back to that source for provenance, not as a document the worker is expected to read.
- Inherit an out-of-scope clause verbatim when the source plan states one for this task, and omit the clause entirely when it does not. Never compose one. A worker honors a fabricated boundary exactly as it honors a real one, so an invented "out of scope: the migration path" quietly deletes work nobody excluded — worse than saying nothing, because the omission is invisible in the worker's report.
- Include strict stop rules for ambiguity, scope expansion, and unrelated refactors.
- Richer role-prompt libraries exist outside this skill; https://github.com/dmonteroh/ai-workflows maintains a catalog of role templates. Treat it as a source to adapt from, not a dependency: this skill stays self-contained.

Output: one packet per task.

### 4) Execute Tasks

- Follow the selected mode guide and runtime guide.
- Keep worker scope constrained to claim sets.
- Hold to the progress contract below while workers run.
- Do not take over a worker's task. When a worker fails or hangs, re-dispatch it with the failure as evidence or return to the user for direction; a controller that quietly hand-codes the patch itself destroys the record of what the worker could not do.
- When a worker returns `QUESTIONS`: answer from the board, the contract artifact, or the source plan; escalate to the user only what those cannot answer. The answer travels in a re-issued packet — never as a message into a running session — and the task moves `needs-info` back to `queued` on re-issue. A `QUESTIONS` return counts against no round cap.
- For repetitive orchestration, create automation scripts only after the user has confirmed the proposal to add them.

Progress contract — what the user hears while workers run:

- One message at dispatch, naming what is running and where.
- After that, a message only on a milestone, a question raised by a worker, an error, or completion. Nothing in between, including reassurance that work is proceeding.
- Announce a kill immediately, with the reason.
- The contract exists so a failure is legible. Without it the user's entire view of a long dispatch is a final "worker failed", with no way to tell a crashed runtime from a worker that asked a question nobody answered.

Output: per-task worker report (root cause, files changed, recommended verification).

### 5) Barrier and Controller Verification

- Confirm worker sessions are fully exited.
- Confirm the processes those workers started have stopped too. A session exiting says nothing about the servers, builds, watchers, backfills, and deploys it launched, and those keep writing while the controller believes the tree is quiet — so verification reads a tree that is still moving, and the result is unattributable. Account for every long-running process the board authorised: stop it, or wait for it and record its outcome as evidence.
- A process a worker started does not outlive the barrier unless a continuing service was the requested outcome. A dev server the user asked to be left running is a deliverable; the same process left behind by a worker that finished is a leak.
- In `true-parallel`, a task that ran in its own worktree with disjoint claims may be verified early — as soon as its own session and authorised processes have stopped — while siblings still run. Verification that touches shared surfaces, and the integration checks, wait for the global barrier.
- Run task-level verification commands.
- Re-dispatch only the smallest failing scope with fresh failure evidence.

Output: verified task status and any narrowed follow-up tasks.

### 6) Review Convergence

A review verdict of `fail` is not a terminal state and not a licence to integrate anyway. It opens a bounded loop with a defined exit. Each round: keep the blocking findings, dispatch a fix task scoped to those findings and nothing else with a claim set no wider than the files they name, then re-review with a reviewer that has no memory of the previous round.

- A reviewer that proposed a fix never evaluates that fix. Critique and repair are separate dispatches with separate authority.
- Cap the rounds before the first one runs. Three rounds is this skill's chosen default, not a measured threshold.
- At the cap, stop and escalate to the human with the surviving findings and the rounds spent. Integrating at the cap and running one round past it are both failures of this step.
- Record the round count and the open findings on the board.
- Why freshness is load-bearing, how to scope the fix packet, and what to do when a finding survives every round: `references/review-convergence.md`.

Output: per-task review verdict with rounds spent — a task cleared for integration, or an escalation carrying the surviving findings.

### 7) Integration Gate

- Integrate one task at a time, in `depends_on` order, never as a batch. Before a task's turn, replay it onto the current integration head — rebase its branch, re-apply its patch, or re-run its change against the integrated tree — and once it lands, re-run the integration checks before the next task starts.
- Never integrate a task while a task it depends on is failing.
- One check run over N merged tasks attributes a failure to the batch, not to a task, and the controller then re-dispatches by guessing which one caused it. Re-running after each merge names the task that broke it, and the re-dispatch is that task's scope.
- Where a task's integration is not trivially revertible, use its recorded `rollback_plan` when its checks fail rather than repairing forward with the bar red.
- Reconcile overlap/conflicts.
- Where worker reports disagree, name the disagreement and which task each position came from. Do not average two verdicts into a middle one the evidence does not support; an unresolved conflict is a finding, and resolving it is a decision with a stated reason.
- Treat a concern raised independently by several workers as blocking rather than as one more item in a list. Independent arrival at the same concern is the signal a fan-out produces that a single worker cannot.
- Run full project quality bar.
- Re-dispatch focused fixes if integration verification fails.

Output: final integration result.

## Output contract

Always return:

- Partition plan (domain → scope | success criteria | constraints).
- Task board summary.
- Per-task report: root cause, files changed, verification commands/results, risks.
- Per reviewed task: the verdict, the rounds spent, and — where the cap was reached — the escalation with the findings that survived it.
- Integration summary: the order tasks were integrated in, the check result after each merge, conflicts, and final verification.
- Automation summary (only if user approved script creation).

Use the canonical structure in `references/packet-templates.md` (`Final Report Template`) for consistent reporting.

## References

- `references/README.md`
- `references/claim-sets.md`
- `references/packet-templates.md`
- `references/review-convergence.md`
- `references/execution-single-worker.md`
- `references/execution-queued-serial.md`
- `references/execution-true-parallel.md`
- `references/runtime-codex.md`
- `references/runtime-claude.md`
- `references/worker-surface.md`
