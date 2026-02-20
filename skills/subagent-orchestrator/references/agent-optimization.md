# Agent Optimization Workflow (Condensed)

Use this when iterating on orchestration quality within this skill.

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

## Parallel Optimization

- Assign worker tasks by domain (frontend, backend, data, infra).
- Run concurrent workers only when claim sets are disjoint.
- Merge through a single integration gate with controller-owned verification.
