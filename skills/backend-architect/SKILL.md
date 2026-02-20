---
name: backend-architect
description: "Guides backend architecture for operable services and APIs, covering boundaries, contracts, reliability, integration patterns, and rollout safety. Use when designing or changing backend services/APIs and their operability plans."
metadata:
  category: architecture
---
# Backend Architect

Provides backend architecture guidance focused on design quality and operability, not framework-specific implementation.

## Use this skill when

Use this skill when the user needs architecture decisions for backend services or APIs.

- Designing a new service/API or changing service boundaries
- Defining contracts (request/response, events, schemas) and compatibility rules
- Planning reliability/observability/rollout (SLIs/SLOs, dashboards, runbooks)
- Choosing integration mechanisms (sync vs async, queues, webhooks) with failure modes

## Do not use this skill when

Do not use this skill when the user only needs implementation details without architectural impact.

- You only need a local code fix with no architectural impact
- You need deep physical database tuning or schema refactoring beyond service boundaries
- You only need stack-specific implementation guidance

## Required inputs

- Business goal and primary user journeys
- Data domains involved and ownership expectations
- Non-functional requirements (latency, throughput, availability, consistency, compliance)
- Existing services or contracts that must be preserved
- Known constraints, assumptions, and explicitly out-of-scope areas

## Workflow

1) Capture constraints
- Output: constraint summary with explicit NFR targets, regulatory needs, and “done” criteria.
- Decision: If any NFRs or compliance constraints are unknown, ask for them before proposing architecture.

2) Define boundaries
- Output: boundary map listing in-scope components, owned data, and external dependencies.
- Decision: If ownership is unclear, propose 2-3 boundary options with pros/cons.

3) Design contracts
- Output: request/response or event contract outline with error semantics, pagination, and idempotency rules.
- Decision: If the change is breaking, include versioning and migration steps before finalizing.

4) Plan failure modes + operability
- Output: reliability plan covering timeouts, retries, circuit breakers, telemetry fields, alerts, and dashboards.
- Decision: If sync vs async is unclear, select based on latency, consistency, and failure isolation tradeoffs.

5) Rollout plan
- Output: rollout sequence with migration steps, rollback strategy, and verification gates.
- Decision: If rollout risk is high, require canary or feature-flagged release.

6) Assemble final report
- Output: response formatted exactly per the Output Contract sections.
- Decision: If any required input is missing, include it in Open questions and flag assumptions.

## Common pitfalls to avoid

- Treating contracts as implementation details instead of stable interfaces
- Skipping backward compatibility and migration sequencing
- Leaving observability requirements implicit or unowned
- Ignoring failure modes for downstream dependencies

## Examples

**Example input**
"We need a new payments orchestration service that talks to the ledger and invoicing systems. It must handle retries safely and support future API versioning."

**Example output (excerpt)**
- Boundary map: payments-orchestrator owns payment intent state; ledger is external dependency.
- Contract: POST /payment-intents with idempotency key; errors return {code, message, retryable}.
- Operability: 99.9% availability SLO; traces include payment_intent_id.

## Output Contract (Always)

Produce a report using this format:
- Architecture sketch: boundaries + contract summary + 2-3 alternatives with tradeoffs
- Decision: chosen approach + rationale
- Risks: top risks + mitigations
- Verification plan: tests, observability checks, rollout gates
- Open questions: missing inputs or assumptions to confirm
