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
- Coordinating provider and consumer work that proceeds in parallel across a boundary owned by different people, teams, or agents

## Do not use this skill when

Do not use this skill when the user only needs implementation details without architectural impact.

- You only need a local code fix with no architectural impact
- You need deep physical database tuning or schema refactoring beyond service boundaries
- You only need stack-specific implementation guidance
- The boundary is internal to one module, changes in a single atomic commit, and has no independent consumer — a shared type is enough, and contract machinery is overhead

## Required inputs

- Business goal and primary user journeys
- Data domains involved and ownership expectations
- Non-functional requirements (latency, throughput, availability, consistency, compliance)
- Existing services or contracts that must be preserved
- Known constraints, assumptions, and explicitly out-of-scope areas
- For each affected boundary: who consumes it, who owns the provider, and who may approve a contract change

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
- Decision: If the boundary has consumers that change independently of the provider, work through "Contract-first boundary changes" below and name the authoritative artifact in the output.

4) Plan failure modes + operability
- Output: reliability plan covering timeouts, retries, circuit breakers, telemetry fields, alerts, and dashboards.
- Decision: If sync vs async is unclear, select based on latency, consistency, and failure isolation tradeoffs.

5) Rollout plan
- Output: rollout sequence with migration steps, rollback strategy, and verification gates.
- Decision: If rollout risk is high, require canary or feature-flagged release.

6) Assemble final report
- Output: response formatted exactly per the Output Contract sections.
- Decision: If any required input is missing, include it in Open questions and flag assumptions.

## Contract-first boundary changes

Applies when a boundary has consumers that change independently of the provider: separate teams, separate repositories, separate agents, or frontend and backend work proceeding in parallel.

### One authoritative artifact per boundary

Name exactly one version-controlled, machine-checkable artifact per boundary, chosen by the kind of boundary:

| Boundary kind | Artifact |
| --- | --- |
| HTTP API | OpenAPI document |
| Event-driven API | AsyncAPI document |
| RPC or message schema | Protocol buffer definitions |
| Standalone payload | JSON Schema |
| All participants on one build and one runtime | A shared typed interface |

The artifact defines the observable behavior consumers depend on: operation or event name, request and response shapes, required versus optional fields, nullability and defaults, enum values, error responses, and the compatibility rule. Keep out anything consumers cannot observe — database columns, internal classes, and query plans are not part of a contract.

The filename does not matter; authority does. When the same payload shape is maintained independently in a wiki page, a consumer-side interface, a provider serializer, and a mock fixture, none of the four is authoritative: each can change without the others, and drift is invisible until integration.

### Record consumers and owners before designing the shape

Write down who consumes the boundary, who owns the provider, who may approve a change to the contract, and which artifact is authoritative. One owner exists to resolve ambiguity — ownership does not mean the provider designs the contract alone.

### Elicit consumer jobs, not provider storage

Start from what each consumer must render or accomplish, and put these questions to each consumer before writing the artifact:

- Which fields are actually required?
- What do missing, empty, and null each mean here?
- Which identifiers must stay strings?
- Which enum values can the consumer handle, and what should it do with one it has never seen?
- Can one task-oriented response replace several coupled calls?
- Which errors require *different* consumer behavior, as opposed to the same generic failure path?

Rule: do not expose a database row and call it a contract. A storage-shaped response hands the storage model control of the public interface, including accidental renames and fields no consumer asked for.

### Verify against serialized output, not compile-time types

A compile-time type is not proof that the bytes on the wire match the contract. A cast satisfies a type checker while the serialized payload drifts underneath it. Validate real serialized responses against the artifact — runtime schema validation, or a contract test at the serialization boundary — because storage drivers, language coercion, and conditional response paths all drift below the type system.

Worked instance: an identifier too large for the consumer's default numeric type. Converting it to a string *after* the driver has already returned it as a rounded floating-point value does not restore the original identifier; the driver has to be configured to return a string or a wide integer type first. The type checker reports a string in both cases.

Verify every materially different path, not only the happy one:

- production mode and sandbox/mock mode
- success and each documented error
- empty collections
- nullable fields
- feature-flagged or versioned response variants

### The integration gate

The integration question is not "did both sides pass their own tests?" It is "did both sides pass against the same boundary artifact?"

- Wrong: the consumer's suite is green and the provider's suite is green, so ship it.
- Right: the consumer's fixtures and the provider's real responses both validate against the same committed artifact, and one end-to-end path ran against it.

Before merge, confirm all of:

- consumer types or clients generate from the artifact without error
- consumer fixtures validate against the artifact
- provider responses validate against the artifact
- at least one end-to-end happy path runs
- no consumer reads a field the artifact does not document

Delete handwritten copies once generated or derived versions exist; a surviving copy is a second source of truth.

### Change protocol: artifact before implementation

1. Propose the consumer need and the compatibility impact.
2. Change the canonical artifact.
3. Review the contract diff with the affected consumers and the provider.
4. Regenerate types, clients, and fixtures.
5. Change the provider and consumer implementations.
6. Run consumer and provider verification.
7. Merge only when every affected side agrees on the new contract.

Never change an implementation first and update the contract afterward: a contract written after the fact records what happened, it does not coordinate parallel work or prevent drift. Renaming a field in one implementation without changing and reviewing the artifact is a breaking change even when that implementation's own tests stay green. For an additive change, verify that existing consumers still work; for a breaking one, apply the versioning or migration policy rather than silently repurposing an existing field.

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
- Boundary artifact: the payments-orchestrator OpenAPI document is authoritative; the invoicing team's client and fixtures generate from it, and the ledger integration validates provider responses against it before merge.
- Operability: 99.9% availability SLO; traces include payment_intent_id.

## Output Contract (Always)

Produce a report using this format:
- Architecture sketch: boundaries + contract summary + 2-3 alternatives with tradeoffs
- Decision: chosen approach + rationale
- Risks: top risks + mitigations
- Verification plan: tests, observability checks, rollout gates; for a boundary with independent consumers, the artifact both sides validated against
- Open questions: missing inputs or assumptions to confirm
