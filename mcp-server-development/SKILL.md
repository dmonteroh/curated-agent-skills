---
name: mcp-server-development
description: "Build high-quality MCP (Model Context Protocol) servers: workflow-first tool design, tight schemas, predictable outputs, safe error handling, and eval-driven iteration. Framework-agnostic (Node/TS or Python). No web fetching required."
---

# MCP Server Development

This skill is for designing and implementing MCP servers that agents can use reliably.

## Use this skill when

- Designing an MCP server tool surface (not just wrapping REST endpoints)
- Implementing an MCP server in Node/TypeScript or Python
- Tightening schemas, output formats, errors, pagination, and safety hints
- Adding deterministic evaluations and integration tests for tool usefulness

## Do not use this skill when

- You only need to call existing tools (use the relevant domain skill)
- You need to implement a non-MCP HTTP API (use backend skills)

## Workflow (Deterministic)

1) Define the agent workflow
- Write 3-5 realistic tasks the agent must complete end-to-end.
- Identify where the agent will fail without better tooling (missing filters, unclear IDs, too much output).

2) Design tools around workflows (not endpoints)
- Prefer “do the thing” tools (create + validate + summarize) over thin wrappers.
- Consolidate related operations when it reduces round-trips and ambiguity.

3) Design input/output contracts
- Inputs: strict validation (types, ranges, enums), helpful field descriptions.
- Outputs: stable shape; include primary identifiers; provide concise defaults.
- Add `readOnlyHint`, `idempotentHint`, `destructiveHint` accurately.

4) Make errors actionable
- Error messages should tell the agent what to try next (valid values, missing permissions, how to filter).
- Avoid dumping raw upstream payloads; summarize and keep an escape hatch to “details” if needed.

5) Implement shared infrastructure once
- HTTP client + auth; pagination helpers; retry/backoff policy (if applicable).
- Response formatting helpers (concise vs detailed).
- Centralized error normalization.

6) Add evaluations early
- Create eval prompts that simulate real usage with realistic data volume.
- Run them after every meaningful tool change.
- Track regressions (“tool worked before, now fails”).

## Output Contract (Always)

- Proposed tool list (name -> purpose -> inputs/outputs -> safety hints)
- A minimal “happy path” usage example per tool
- Evaluation plan (at least 5 scenarios) and how to run it

## References (Optional)

- Tool design principles and checklists: `references/tool-design.md`
- Schema + output conventions: `references/contracts.md`
- Error handling patterns: `references/errors.md`
- Evaluation playbook: `references/evals.md`
- Protocol + SDK notes (compact): `references/sdk/`
