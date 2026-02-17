---
name: dispatching-parallel-agents
description: "Split work across multiple agents in parallel when tasks are independent (no shared state, minimal file overlap). Provides a deterministic workflow to partition scope, write focused sub-agent prompts, and merge results safely."
category: ai
---
# Dispatching Parallel Agents

Parallel dispatch is only useful when tasks are truly independent. This skill provides a **subagent execution** pattern (implementer + reviewers) to finish each partition cleanly.

Core principle: **one agent per independent domain**, with explicit constraints and a deterministic merge plan.

## When to Use

Use this skill when:

- 2+ issues can be investigated without shared context (different subsystems, different failure modes)
- Fixes are unlikely to touch the same files (or can be partitioned by folder/module)
- You can define “done” per domain (tests passing, endpoint fixed, doc generated)

Do not use this skill when:

- Problems are likely coupled (fixing one will change the others)
- A single root-cause investigation is needed first (“unknown unknowns”)
- Agents would contend on the same files, the same environment, or the same external resource

## Required Inputs

- Problem statement or goal per domain
- Evidence per domain (errors, failing tests, logs, repro steps)
- Allowed scope (files/modules per domain)
- Constraints (what must not change)
- Verification expectations (tests, commands, or checks)

## Workflow (Deterministic)

### 1) Partition the work

Group by domain, not by symptom.

Examples:

- “auth flow regressions” vs “UI rendering glitches” vs “DB migration failure”
- “test file A failures” vs “test file B failures” (only if they’re truly unrelated)

For each domain, define:

- scope (which files/modules)
- success criteria (what “fixed” means)
- constraints (what must not change)

Decision point: if any domains share likely root causes or overlapping files, collapse them into a single domain before dispatching.

Output: a partition plan listing domain, scope, success criteria, constraints.

### 2) Write sub-agent prompts (narrow + self-contained)

Each prompt should include:

- scope (files/folders to touch)
- inputs (errors, logs, failing tests, reproduction steps)
- constraints (don’t refactor unrelated code; don’t change public APIs; etc.)
- required output (root cause + changes + verification)

Template:

```text
Task: <domain>

Scope:
- Allowed: <files/folders>
- Avoid: <files/folders>

Inputs:
- Failures/errors:
  - <copy/paste key errors or failing test names>

Constraints:
- <e.g., no behavior changes beyond the failing cases>
- <e.g., keep public API stable>

Definition of done:
- <e.g., these tests pass>
- <e.g., this command produces expected output>

Return:
- Root cause
- Exact changes made (files)
- Verification
```

Output: one task packet per domain, ready to dispatch.

### 3) Dispatch in parallel

Dispatch one agent per domain. If the environment supports it, run them concurrently; otherwise run sequentially while keeping prompts separate and focused.

Output: dispatched prompts with clear ownership per domain.

### 4) Execute with subagents (per domain)

Use the subagent packets and reviewers to implement each domain safely. If no subagent mechanism exists, perform the implementer and review passes sequentially using the same packets.

Output: per-domain implementation summary (root cause, files changed, verification).

### 5) Merge safely (integration gate)

Before merging:

- check file overlap (if two agents edited the same file, integrate manually)
- run the full verification (test suite / build / smoke checks)
- require each agent to report “what changed” + “how verified”

Decision point: if verification fails, send the relevant domain back for fixes before finalizing.

Output: integrated change set and final verification status.

## Common Mistakes

- Too broad: “fix everything” (agents thrash and overlap)
- No constraints: agents refactor adjacent code and create conflicts
- No evidence: prompts lack failing output or reproduction steps
- No verification: changes land without a final integration gate

## Output Contract (Always)

- Partition plan (domain -> agent prompt)
- One summary per agent: root cause, changes, verification
- Integration summary: conflicts (if any) + final verification result

Reporting format:

```text
Partition Plan:
- <domain>: <scope> | <success criteria> | <constraints>

Agent Summaries:
- <domain>: Root cause: <...> | Changes: <files> | Verification: <...>

Integration Summary:
- Conflicts: <none or details>
- Final verification: <command/result>
```

## Composition (Recommended)

- Use this skill to partition work into independent domains and write scope-limited prompts.
- Use the included subagent execution flow (implementer + reviewers) to complete each domain.

## Notes

- This skill is model-agnostic: it describes *how to split work*, not a specific vendor’s agent API.
- If the environment has a specific “spawn sub-agent” mechanism, use it. The important part is the partitioning, constraints, and merge gate.
- This skill is self-contained and does not rely on other skills.

## References (Optional)

- `references/README.md` (index of optional reference material)
# Code Quality Reviewer Prompt (Copy/Paste Template)

Purpose: verify the implementation is well-built: correct, maintainable, tested, and safe.

Only run this after spec compliance passes (or if explicitly asked to review quality regardless).

```text
Review type: code-quality

Scope:
- Review only these paths: <paths>

Inputs:
- Summary of change intent:
  - <1-3 bullets>
- Optional: diff range:
  - <base sha>..<head sha>

Checks:
- Correctness: edge cases, error handling, concurrency, idempotency (if relevant)
- Maintainability: naming, structure, duplication, complexity
- Safety: secrets/logging, unsafe defaults, dangerous operations
- Tests: presence, quality, and whether they actually validate behavior
- Verification gap: did anyone run the right commands?

Output:
- Verdict: pass | fail | needs-info
- Findings ordered by severity (Critical/Important/Minor)
- Concrete fixes (file paths)
- What to verify (commands)
```
# Implementer Subagent Prompt (Copy/Paste Template)

Use this to dispatch an implementer subagent. It is designed to work in **non-interactive** subagent environments.

```text
Task: <one sentence, explicit outcome>.

Context:
- Why: <why this exists>
- Where: <module/service>
- Constraints: <compat/security/perf>

Scope:
- Allowed: <paths>
- Avoid: <paths>

Inputs:
- Read these files first:
  - <paths>
- Evidence:
  - <failing tests / logs / repro steps>

Rules:
- If anything is ambiguous or conflicts: STOP and output QUESTIONS. Do not guess.
- Do not expand scope.
- Do not refactor unrelated code.
- Preserve existing APIs unless explicitly instructed.

Steps:
1) Inspect current state (read the listed files).
2) Implement the minimal change that satisfies the acceptance criteria.
3) Update/add tests if appropriate.
4) Run verification commands, or explain why you cannot.

Acceptance Criteria:
- [ ] <criterion>
- [ ] <criterion>

Verification:
- Command(s):
  - <e.g., dotnet test>
  - <e.g., npm test>

Output:
- Root cause.
- Files changed/moved.
- Verification commands + results.
- Any risks or follow-ups.
- If blocked: QUESTIONS (explicit) + what info is missing.
```
# References Index

Use these optional references when you need deeper guidance while keeping `SKILL.md` concise.

- `agent-optimization.md`: Baseline → improve → validate loop for iterative agent work.
- `claude.md`: Example of parallel dispatch phrased for Claude Code workflows.
- `codex-exec.md`: Codex CLI-style subagent dispatch via `codex exec`.
- `codex.md`: Codex usage patterns, including sequential “prompt-parallel” mode.
- `review-packet-template.md`: Template for reviewer packet inputs and outputs.
- `subagent-execution.md`: Implementer + reviewers flow for each domain.
- `task-packet-template.md`: Template for task packet inputs and outputs.
# Agent Optimization Workflow (Condensed)

Use this when iterating on agent quality or coordinating multi-agent optimization.

## Phase 1: Baseline

- Gather task success rates, correction patterns, tool usage quality.
- Identify recurring failure modes.
- Record a baseline report (success rate, latency, token usage).

## Phase 2: Improve

- Tighten role definition and constraints.
- Add targeted examples for edge cases.
- Add self-check steps (format validation, completeness checks).

## Phase 3: Validate

- Run a fixed test set (golden paths + prior failures).
- Compare before/after results.
- Keep a rollback plan if quality regresses.

## Multi-Agent Optimization

- Assign agents by domain (frontend, backend, data, infra).
- Run in parallel only if file overlap is unlikely.
- Merge via a single integration gate with verification.
# Using This Skill In Claude Code (Example)

This is an optional reference for environments that support spawning parallel sub-agents.

## Pattern

1) Partition the work into independent domains.
2) Write one narrow prompt per domain.
3) Dispatch one sub-agent per domain.
4) Merge with an integration gate (check overlaps + run full verification).

## Example (Claude Code-style "Task" dispatch)

The exact API varies by host environment. The key is that each task is:

- scope-limited (files/modules)
- has explicit success criteria
- returns a summary + verification

```text
Task("Fix failing tests in packages/auth")
Task("Investigate deployment config drift in k8s manifests")
Task("Update docs for new CLI flags")
```

## Prompt Template (Copy)

```text
Task: <domain>

Scope:
- Allowed: <files/folders>
- Avoid: <files/folders>

Inputs:
- Failures/errors:
  - <copy/paste key errors or failing test names>

Constraints:
- <no refactors beyond scope>
- <keep public API stable>

Definition of done:
- <tests pass / command output matches>

Return:
- Root cause
- Exact changes made (files)
- How you verified
```
# Codex Subagents via `codex exec`

This reference captures a reliable pattern for spawning a separate, non-interactive Codex agent process.

## Key properties

- Subagents are **non-interactive**: no mid-task back-and-forth.
- Subagents can read local skills/files **from disk** (within sandbox limits).
- Subagents do not share chat context; include all needed context in the prompt or point them to files to read.

## Sandboxing

The sandbox you pass applies to that subagent only:

- `read-only`: can read files but cannot edit/move/write.
- `workspace-write`: can write inside the workspace.
- `danger-full-access`: unrestricted; use only with explicit intent.

## Best-practice prompt template

```sh
codex exec --sandbox workspace-write "
Task: <one sentence, explicit outcome>.
Scope: Only touch <paths>. Do not touch <paths>.
Rules:
- Preserve filenames and content unless explicitly told to edit.
- If a rule conflicts or requirements are ambiguous, STOP and output QUESTIONS (do not guess).
Steps:
1) Inspect <files> to establish current state.
2) Perform <exact actions>.
3) Update <specific file(s)> with <specific changes>.
Output:
- List files changed.
- List files moved.
- Summarize edits with file paths.
- Verification performed (commands + result), or explain why verification could not be run.
"
```

## Practical tips

- Prefer `workspace-write` by default.
- If the task is risky, restrict scope to a small directory and explicit file list.
- Require explicit reporting: files changed + verification.
# Using This Skill In Codex (Example)

This skill is still useful even if you cannot literally spawn multiple sub-agents.

## Two Modes

### Mode A: True parallelism (if your host supports it)

If your Codex environment supports parallel sub-tasks, dispatch one per domain and then merge with an integration gate.

### Mode B: "Prompt-parallel" (works everywhere)

Even without true parallelism, you can get most of the benefit by:

- partitioning the work
- writing 2-5 tight sub-task prompts
- executing them sequentially without mixing context

This avoids thrash and reduces accidental coupling.

## Practical Workflow (Recommended)

1) Partition
- Identify domains that do not share files/state.

2) Create sub-task prompts
- Use the prompt template from the main skill.

3) Execute one sub-task at a time
- Treat each sub-task as its own mini-session.
- Before moving to the next sub-task, write down:
  - root cause
  - files changed
  - verification result

4) Merge gate
- Check for file overlap and reconcile.
- Run the full verification (tests/build/smoke checks).

## Optional: Isolation via Git worktrees

If you have a git repo and want better isolation (still model-agnostic):

- Create one worktree per domain
- Do changes in each worktree
- Merge in a controlled order

(Only do this if it fits your repo workflow.)
# Review Packet Template (Subagent)

Use this when dispatching a reviewer subagent (spec compliance or code quality).

```text
Review type: <spec-compliance|code-quality>

Scope:
- Review only these paths: <paths>

Inputs:
- Requirements/spec:
  - <spec file path(s) or pasted requirements>
- Code changes:
  - <git diff summary or file list>
  - <commit SHA(s)> (optional)

Rules:
- Be strict and explicit.
- If you cannot verify, say so.

Output:
- Verdict: pass | fail | needs-info
- Findings (ordered by severity)
- Concrete fixes (file paths)
- Verification gap (if any)
```
# Subagent Execution (Condensed)

Use this when executing a partitioned plan with implementer + reviewers.

## Steps

1. Prepare task packets (scope, constraints, verification).
2. Dispatch implementer for each task.
3. Run verification commands.
4. Run spec + code quality reviews.
5. Integrate and re-verify.
# Task Packet Template (Subagent)

Use this template to provide a subagent enough context to work non-interactively.

```text
Task: <one sentence, explicit outcome>.

Context:
- Why: <why this change exists>
- Where it fits: <module/service>
- Constraints: <compat/security/perf/etc>

Scope:
- Allowed: <paths>
- Avoid: <paths>

Inputs:
- Pointers:
  - <file paths to read>
- Evidence:
  - <failing test names / stack traces / logs>

Rules:
- If ambiguous or conflicting: STOP and output QUESTIONS.
- Do not expand scope.
- Do not refactor unrelated code.

Steps:
1) Inspect current state (read the listed files).
2) Implement minimal changes to satisfy the acceptance criteria.
3) Update/add tests if appropriate.
4) Run verification (or explain why you cannot).

Acceptance Criteria:
- [ ] <criterion>
- [ ] <criterion>

Output:
- Root cause.
- Files changed/moved.
- Verification commands + results.
- Any follow-ups or risks.
```
# Spec Compliance Reviewer Prompt (Copy/Paste Template)

Purpose: verify the implementation matches requirements **line-by-line** (nothing missing, nothing extra).

```text
Review type: spec-compliance

Requirements:
<copy/paste or point to the exact spec text>

Scope:
- Review only these paths: <paths>

Inputs:
- Files changed (if known):
  - <paths>
- Optional: commit(s) or diff range:
  - <base sha>..<head sha>

Rules:
- Do not trust the implementer report.
- Verify by reading code and/or diffs.
- Call out missing requirements and extra scope explicitly.

Output:
- Verdict: pass | fail | needs-info
- Missing requirements (with file references)
- Extra/unrequested changes (with file references)
- Ambiguities in spec (if any) and questions for the controller
```
