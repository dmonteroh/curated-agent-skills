---
name: dispatching-parallel-agents
description: Split work across multiple agents in parallel when tasks are independent (no shared state, minimal file overlap). Provides a deterministic workflow to partition scope, write focused sub-agent prompts, and merge results safely.
category: ai
---

# Dispatching Parallel Agents

Parallel dispatch is only useful when tasks are truly independent. The goal is to reduce wall-clock time without creating merge conflicts or duplicated investigation.

Core principle: **one agent per independent domain**, with explicit constraints and a deterministic merge plan.

## When to Use

Use when:

- 2+ issues can be investigated without shared context (different subsystems, different failure modes)
- Fixes are unlikely to touch the same files (or can be partitioned by folder/module)
- You can define “done” per domain (tests passing, endpoint fixed, doc generated)

Don’t use when:

- Problems are likely coupled (fixing one will change the others)
- A single root-cause investigation is needed first (“unknown unknowns”)
- Agents would contend on the same files, the same environment, or the same external resource

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

### 3) Dispatch in parallel

Dispatch one agent per domain. If your environment supports it, run them concurrently; otherwise run sequentially but keep prompts separate and focused.

### 4) Merge safely (integration gate)

Before merging:

- check file overlap (if two agents edited the same file, integrate manually)
- run the full verification (test suite / build / smoke checks)
- require each agent to report “what changed” + “how verified”

## Common Mistakes

- Too broad: “fix everything” (agents thrash and overlap)
- No constraints: agents refactor adjacent code and create conflicts
- No evidence: prompts lack failing output or reproduction steps
- No verification: changes land without a final integration gate

## Output Contract (Always)

- A partition plan (domain -> agent prompt)
- One summary per agent: root cause, changes, verification
- An integration summary: conflicts (if any) + final verification result

## Composition (Recommended)

- Use this skill to partition work into independent domains and write scope-limited prompts.
- If you have a spec/plan and want strict per-task verification + review gates, execute each domain using `subagent-driven-development`.

## Notes

- This skill is model-agnostic: it describes *how to split work*, not a specific vendor’s agent API.
- If your environment has a specific “spawn sub-agent” mechanism, use it. The important part is the partitioning, constraints, and merge gate.

## References (Optional)

- `references/codex.md` (Codex usage patterns, including sequential “prompt-parallel” mode)
- `references/claude.md` (Claude Code-style parallel dispatch example)
