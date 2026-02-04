---
name: dispatching-parallel-agents
description: Split work across multiple agents in parallel when tasks are independent (no shared state, minimal file overlap). Provides a deterministic workflow to partition scope, write focused sub-agent prompts, and merge results safely.
category: ai
---

# Dispatching Parallel Agents

Parallel dispatch is only useful when tasks are truly independent. This skill includes a **subagent execution** pattern (implementer + reviewers) to finish each partition cleanly.

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

## Trigger Phrases

- “dispatch in parallel”
- “split this into independent sub-tasks”
- “parallelize the investigation”
- “assign separate agents per module”

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
- How you verified
```

Output: one task packet per domain, ready to dispatch.

### 3) Dispatch in parallel

Dispatch one agent per domain. If your environment supports it, run them concurrently; otherwise run sequentially but keep prompts separate and focused.

Output: dispatched prompts with clear ownership per domain.

### 4) Execute with subagents (per domain)

Use the subagent packets and reviewers to implement each domain safely. If no subagent mechanism exists, perform the implementer and review passes sequentially yourself using the same packets.

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
- If your environment has a specific “spawn sub-agent” mechanism, use it. The important part is the partitioning, constraints, and merge gate.
- This skill is self-contained and does not rely on other skills.

## Trigger Test

Example prompts that should activate this skill:

- “We have UI and API bugs in different modules — can you dispatch them in parallel?”
- “Split this investigation across separate agents for auth and payments.”

## References (Optional)

- `references/README.md` (index of optional reference material)
