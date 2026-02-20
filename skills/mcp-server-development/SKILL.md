---
name: mcp-server-development
description: "Build high-quality MCP (Model Context Protocol) servers: workflow-first tool design, tight schemas, predictable outputs, safe error handling, and eval-driven iteration. Framework-agnostic (Node/TS or Python). No web fetching required."
metadata:
  category: ai
---
# MCP Server Development

Provides guidance for designing and implementing MCP servers that agents can use reliably.

## Use this skill when

- Designing an MCP server tool surface (not just wrapping REST endpoints)
- Implementing an MCP server in Node/TypeScript or Python
- Tightening schemas, output formats, errors, pagination, and safety hints
- Adding deterministic evaluations and integration tests for tool usefulness

## Do not use this skill when

- You only need to call existing tools without new MCP server work
- You need to implement a non-MCP HTTP API

## Inputs required

- Target domain + core user/agent workflows
- Existing APIs or data sources (if any)
- Constraints (auth, rate limits, privacy, allowed storage)
- Preferred implementation stack (Node/TS or Python)

## Workflow (Deterministic)

1) Define the agent workflow
- Write 3-5 realistic tasks the agent must complete end-to-end.
- Identify where the agent will fail without better tooling (missing filters, unclear IDs, too much output).
- Output: A short list of workflows + failure points.

2) Design tools around workflows (not endpoints)
- Prefer “do the thing” tools (create + validate + summarize) over thin wrappers.
- Consolidate related operations when it reduces round-trips and ambiguity.
- Output: Draft tool list with workflow coverage notes.

3) Design input/output contracts
- Inputs: strict validation (types, ranges, enums), helpful field descriptions.
- Outputs: stable shape; include primary identifiers; provide concise defaults.
- Add `readOnlyHint`, `idempotentHint`, `destructiveHint` accurately.
- Output: Schema drafts for each tool.

4) Make errors actionable
- Error messages should tell the agent what to try next (valid values, missing permissions, how to filter).
- Avoid dumping raw upstream payloads; summarize and keep an escape hatch to “details” if needed.
- Output: Error shape + example messages.

5) Implement shared infrastructure once
- HTTP client + auth; pagination helpers; retry/backoff policy (if applicable).
- Response formatting helpers (concise vs detailed).
- Centralized error normalization.
- Output: Reusable helper modules and integration notes.

6) Add evaluations early
- Create eval prompts that simulate real usage with realistic data volume.
- Run them after every meaningful tool change.
- Track regressions (“tool worked before, now fails”).
- Output: Eval suite plan + run instructions.

## Decision points

- If workflows span multiple data sources, add a single “join” tool before exposing low-level calls.
- If inputs are ambiguous, add enum constraints and example values.
- If tool output exceeds a page, add pagination and a summary-only response mode.
- If auth or permissions are unclear, add an explicit “permission_check” tool before destructive actions.

## Common pitfalls

- Wrapping endpoints without a workflow goal.
- Returning unbounded arrays or verbose payloads.
- Missing stable identifiers in responses.
- Throwing raw upstream errors with no guidance.
- Skipping evals until after integration.

## Output Contract (Always)

- Proposed tool list (name -> purpose -> inputs/outputs -> safety hints)
- A minimal “happy path” usage example per tool
- Evaluation plan (at least 5 scenarios) and how to run it

## Reporting format

- Summary: 3-6 bullets of decisions and rationale
- Tools: table with name, purpose, inputs, outputs, hints
- Examples: per-tool request/response blocks
- Evals: numbered scenarios + run command

## Examples

**Input**
“We need an MCP server for internal issue triage. It should search issues, assign owners, and summarize recent changes. Stack is Node/TS. Auth is OAuth; rate limit 60/min.”

**Output (excerpt)**
- Tools: `search_issues`, `assign_issue`, `summarize_issue_updates`
- `search_issues` schema includes `status` enum and `max_results` with cap.
- Errors: `INVALID_STATUS` suggests valid values.

## References (Optional)

- Index: `references/README.md`
- Tool design principles and checklists: `references/tool-design.md`
- Schema + output conventions: `references/contracts.md`
- Error handling patterns: `references/errors.md`
- Evaluation playbook: `references/evals.md`
- Protocol quick reference: `references/protocol-quickref.md`
- Python SDK notes: `references/python-sdk-notes.md`
- TypeScript SDK notes: `references/typescript-sdk-notes.md`
