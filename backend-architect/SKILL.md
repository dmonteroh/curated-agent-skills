---
name: backend-architect
description: "Guides backend architecture for operable services and APIs: boundaries, contracts, reliability, integration patterns, and rollout safety. Produces clear architecture decisions and verification steps. Use proactively when creating or changing backend services/APIs."
category: architecture
---

# Backend Architect

Provides guidance on backend design quality and operability, not framework-specific implementation.

## Use this skill when

- Designing a new service/API or changing service boundaries
- Defining contracts (request/response, events, schemas) and compatibility rules
- Planning reliability/observability/rollout (SLIs/SLOs, dashboards, runbooks)
- Choosing integration mechanisms (sync vs async, queues, webhooks) with failure modes

## Do not use this skill when

- You only need a local code fix with no architectural impact
- You need deep physical database tuning or schema refactoring beyond service boundaries
- You only need stack-specific implementation guidance

## Trigger phrases

- “Design a new backend service for…"
- “Define the API contract and versioning plan for…"
- “How should these services integrate reliably?"
- “Plan the rollout and observability for a backend change"

## Required inputs

- Business goal and primary user journeys
- Data domains involved and ownership expectations
- Non-functional requirements (latency, throughput, availability, consistency, compliance)
- Existing services or contracts that must be preserved
- Known constraints, assumptions, and explicitly out-of-scope areas

## Workflow (Deterministic)

1) Capture constraints
- Output: constraint summary with explicit NFR targets and “done” criteria.
- Decision: If any NFRs or compliance constraints are unknown, ask for them before proposing architecture.

2) Define boundaries
- Output: boundary map listing in-scope components, owned data, and external dependencies.
- Decision: If ownership is unclear, propose 2-3 boundary options with pros/cons.

3) Design contracts
- Output: request/response or event contract outline with error semantics, pagination, and idempotency rules.
- Decision: If the change is breaking, include versioning and migration steps before finalizing.

4) Plan failure modes + operability
- Output: reliability plan covering timeouts, retries, circuit breakers, and telemetry fields.
- Decision: If sync vs async is unclear, choose based on latency, consistency, and failure isolation tradeoffs.

5) Rollout plan
- Output: rollout sequence with migration steps, rollback strategy, and verification gates.
- Decision: If rollout risk is high, require canary or feature-flagged release.

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

Report in this format:
- Architecture sketch: boundaries + contract summary + 2-3 alternatives with tradeoffs
- Chosen approach + rationale
- Risks + mitigations
- Verification plan: tests, observability checks, rollout gates

## Trigger test

Use this skill when a user asks:
- “Design the backend service boundaries for our new order API.”
- “Create an operability and rollout plan for a new event-driven integration.”
