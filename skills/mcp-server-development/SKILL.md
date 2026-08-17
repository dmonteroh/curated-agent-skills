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
- Normalize the success path the way errors are normalized: a recommended envelope of `status`, a one-line `summary`, `next_actions` (follow-ups that make sense from this result), and `artifacts` (IDs or paths produced). Declare per tool the fields that carry real information rather than mandating all four on every response, and keep the names identical across the tools that declare them (`references/contracts.md`).
- Add `readOnlyHint`, `idempotentHint`, `destructiveHint` accurately.
- Output: Schema drafts for each tool.

4) Make errors actionable
- Error messages should tell the agent what to try next (valid values, missing permissions, how to filter).
- Every error path that invites a retry also states its stop condition: the signal that means stop retrying and escalate — a code that is never transient, an attempt or time budget the caller sets, or a state that should have changed between attempts and did not. A retry hint with no stop condition is an invitation to loop (`references/errors.md`).
- Avoid dumping raw upstream payloads; summarize and keep an escape hatch to “details” if needed.
- Output: Error shape + example messages.

5) Implement shared infrastructure once
- HTTP client + auth; pagination helpers; retry/backoff policy (if applicable).
- Response formatting helpers (concise vs detailed).
- Centralized error normalization.
- If the server wraps one or more optional, swappable backend providers, give them a capability contract: define a small required-op set plus a separate optional-op set (the required set is the honest common denominator across expected providers, not the richest provider's feature list); providers advertise exactly what they back, asserted at construction; an unadvertised call throws a typed error, never a silent no-op; and give that layer a closed, enumerated error-code set with exactly one code designated the non-fatal "degrade and continue" signal, every other code fatal to that call (`references/provider-contracts.md`).
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
- If the server can run with a backend provider disabled or unselected, the resolver returns `null` for "no provider" rather than a stub or mock — callers get an explicit, checkable off state, and the server stays fully functional with the provider off (`references/provider-contracts.md`).
- If a provider can operate non-locally (network egress), gate every capability call on explicit consent inside the contract itself, not left to each call site: installing/enabling the provider and letting it receive content are two separate axes, and neither is ever auto-granted; a provider that runs entirely locally has nothing to consent to on the egress axis (`references/provider-contracts.md`).

## Common pitfalls

- Wrapping endpoints without a workflow goal.
- Returning unbounded arrays or verbose payloads.
- Missing stable identifiers in responses.
- Throwing raw upstream errors with no guidance.
- Skipping evals until after integration.
- Letting a missing optional capability silently no-op instead of throwing a typed error — a silent no-op is indistinguishable from "ran and legitimately found nothing," which corrupts every caller's ability to reason about the result.

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
- `assign_issue` returns `status`, a one-line `summary` ("assigned ISSUE-412 to a.chen"), `next_actions` (`summarize_issue_updates` for the same ID), and `artifacts` (the issue ID).
- Errors: `INVALID_STATUS` suggests valid values, and stops the loop — it is never transient, so a retry with the same value cannot succeed.

## References (Optional)

- Index: `references/README.md`
- Tool design principles and checklists: `references/tool-design.md`
- Schema + output conventions: `references/contracts.md`
- Error handling patterns: `references/errors.md`
- Optional-capability provider contract: `references/provider-contracts.md`
- Evaluation playbook: `references/evals.md`
- Protocol quick reference: `references/protocol-quickref.md`
- Python SDK notes: `references/python-sdk-notes.md`
- TypeScript SDK notes: `references/typescript-sdk-notes.md`
