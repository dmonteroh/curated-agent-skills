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
