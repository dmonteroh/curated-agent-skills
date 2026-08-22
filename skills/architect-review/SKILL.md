---
name: architect-review
description: "Review system designs and major changes for architectural integrity, scalability, and maintainability; use for architecture decisions, tradeoffs, and risks across distributed systems and clean architecture patterns."
metadata:
  category: architecture
---
# Architect Review

## Use this skill when

- Reviewing system architecture or major design changes
- Evaluating scalability, resilience, or maintainability impacts
- Assessing architecture compliance with standards and patterns
- Providing architectural guidance for complex systems
- Checking layering, bounded-context, or aggregate boundaries in a Clean, Hexagonal, or DDD codebase

## Do not use this skill when

- The task is a small code review without architectural impact
- The change is minor and local to a single module
- Critical system context remains unavailable after asking clarifying questions

## Instructions

### Required inputs
- System context: current architecture, key components, and data flows
- Change description: what is being added/changed and why
- Constraints: non-functional requirements (scalability, resilience, security, cost)
- Dependencies: key integrations or platform constraints
- Success criteria: SLAs, SLOs, or measurable outcomes if available
- Optional artifacts: diagrams, ADRs, API contracts, deployment topology
- Existing components or assets that might already cover the need (for the reuse-first audit)

### Workflow
1. Confirm scope and inputs; list missing context.
   - Output: concise context summary + open questions.
   - Decision: if the change is minor/local, state that the skill is not applicable and stop.
   - Decision: if critical context is missing, ask targeted questions and pause.
2. Check the premise, before reviewing the design itself.
   - Output: three questions, answered directly, not rhetorically: Is this the right problem? What happens if we do nothing? What is the risk of acting?
   - Decision: if the answers show the wrong problem is being solved, or that doing nothing is clearly safer than acting, say so and stop before spending review effort on the design.
3. Audit for reuse before evaluating anything new.
   - Output: a table of existing assets relevant to the change and how each is reused rather than rebuilt (columns: asset, reuse). List every component, service, or library the new design could extend instead of replace.
   - Decision: where an existing asset already covers the need, recommend extending it and flag the new component as unnecessary.
4. Map the current architecture and change impact.
   - Output: architecture snapshot + assumptions.
5. Evaluate decisions against goals and quality attributes.
   - Output: impact rating (High/Medium/Low) + risk list.
   - Decision: if impact is High, require mitigation and rollback strategy.
6. Identify architectural violations or anti-patterns.
   - Output: findings with evidence or reasoning.
   - Decision: classify findings as blocking vs. advisory and require fixes for blocking items.
   - Decision: run the "Boundary violation diagnostics" table below against the design or codebase. Each symptom present is a finding carrying its named structural fix — not an observation to phrase as a preference.
7. Build a failure modes registry.
   - Output: one table, one row per code path that can fail, with fixed columns: codepath, failure mode, rescued? (yes/no + mechanism), test? (yes/no + which test), what the user sees, and where it is logged.
   - Invariant, stated literally so it is a checkable rule and not a mood: every failure mode needs a rescue, a test, and visibility. Visibility is satisfied jointly by "what the user sees" and "logged" — a failure that is silently rescued with nothing surfaced to the user and nothing written to a log is still a visible gap in the table, even though it is technically "rescued".
   - Decision: any row with a missing or hedged answer in rescued?, test?, or the visibility columns is a structural gap to close before the design proceeds — treat it as blocking, not a judgment call. The table's job is to make the gap visually obvious rather than easy to miss inside a paragraph.
8. Recommend improvements with tradeoffs and alternatives.
   - Output: prioritized recommendations with pros/cons.
9. Define validation and follow-up actions.
   - Output: verification plan (tests, load checks, PoC, rollout guardrails).
10. Document decisions and next steps.
    - Output: ADR suggestion list and owners if provided.

## Boundary violation diagnostics

Layering violations are easier to catch by their observable symptom than by arguing about which pattern the design claims to follow. Each row below is a symptom a reviewer can look for directly, what it means structurally, and the fix that removes it. A symptom found is a finding; the middle column is the evidence, the right column is the recommendation.

| Symptom | What it means structurally | Structural fix |
| --- | --- | --- |
| Use-case or business-logic tests need a live database, broker, or third-party service | Business logic has leaked into the infrastructure layer | Put the dependency behind an abstract port and inject a fake or in-memory implementation in tests; the use case accepts the port, never the concrete class |
| Import cycle between an inner layer and an outer one | An inner-layer module imports a concrete implementation instead of an abstract interface | Inner layers import only from the domain/core layer, never from adapters or infrastructure; wire the concrete implementations at composition time |
| Framework-specific decorators or annotations (ORM column definitions, serializer field declarations) sit on a core domain object | The domain model is not pure — persistence or transport concerns are fused into it | Keep a separate persistence/transport model and map between it and the domain object at the boundary |
| A controller or request handler keeps growing | Logic belonging to a use case is accumulating at the transport edge | Extract it into a use-case or service object; a controller parses the request, invokes the use case, and formats the response — nothing else |
| A value object accepts invalid data and fails deep inside business logic later | Invariants are not enforced at construction | Validate in the constructor so an invalid instance cannot exist at all, surfacing bad data at the boundary |
| One bounded context imports another context's domain objects directly | The two contexts share a model, so either can break the other | Introduce an anti-corruption layer that translates the foreign model into a local representation; hold a local identifier, not the foreign entity |
| A domain entity reads configuration or environment | Infrastructure concerns reach into the core | Pass the values in as constructor arguments, resolved at the infrastructure boundary |
| Two aggregates import each other | Direct coupling where a fact should flow | One aggregate emits a domain event; the other's use case subscribes and reacts, and neither imports the other |
| A repository calls a use case to do extra work after saving | Persistence is orchestrating behavior | Move the extra work into a domain service or use case; repositories persist state and do not orchestrate |

Where the language has a dependency-graph tool, rendering the module graph makes the direction check mechanical rather than a reading exercise: the domain/core layer must show no outgoing edges to adapters or infrastructure, and any arrow pointing outward is a violation to report.

## Aggregate boundary sizing

Where to draw an aggregate boundary is a recurring call that reviews tend to settle by taste. Put every question below to the design and record the answer. Most decide membership — what sits inside the boundary; one identifies the root; the last is a size check that can overrule a membership answer the others produced.

| Question | If yes |
| --- | --- |
| Must these two objects always be consistent with each other, as one atomic change? | Same aggregate |
| Can they be eventually consistent? | Separate aggregates, synchronized by a domain event |
| Is one object the owner controlling access to the other? | The owner is the aggregate root |
| Does removing the root make the child meaningless on its own? | The child belongs inside the aggregate |
| Would a single state change require loading a large object graph? | The aggregate is too large — split it |

Contrast, on a customer-and-orders model:

- Wrong: `Customer` holds full `Order` objects, so every change to a customer loads that customer's entire order history.
- Right: `Customer` holds order identifiers only; `Order` is its own aggregate and references the customer by identifier. Consistency between them is maintained by domain events, not by one object graph.

## Output contract
Produce an **Architectural Review Report** using Markdown headings with these exact labels, in this order:
- Context summary (assumptions + open questions)
- Premise check (right problem / cost of doing nothing / risk of acting)
- Reuse-first audit (existing assets and how each is reused, not rebuilt)
- Impact rating (High/Medium/Low)
- Findings and risks (blocking vs. advisory)
- Failure modes registry (codepath / failure mode / rescued? / test? / what the user sees / logged)
- Recommendations with tradeoffs
- Validation plan
- Decisions/ADRs and next steps
Format the premise check, reuse-first audit, and failure modes registry as tables; format the remaining sections as bullet points. Label each finding as `blocking` or `advisory`.

## Examples
**Input:** "We want to split a monolith into services for payments and orders; review the design for boundaries and data ownership."

**Output (excerpt):**
- Context summary: current monolith with shared order/payment tables; new services for orders and payments.
- Premise check: right problem — yes, payment/order coupling already causes deploy contention between the two teams; cost of doing nothing — the coupling keeps compounding as both teams grow; risk of acting — data migration and a dual-write window during cutover.
- Reuse-first audit: existing `OrderRepository` and `PaymentGateway` clients are reused as-is inside the new services; only the shared-table access layer is replaced, not the clients that call it.
- Impact rating: High (data migration + cross-service transactions).
- Findings and risks: shared database coupling (blocking); missing saga/outbox strategy (blocking).
- Failure modes registry: `POST /orders` → payment service unreachable → rescued? yes, circuit breaker + retry queue → test? yes, chaos test `payment-timeout` → user sees "Order pending payment confirmation" → logged? yes, `order.payment.timeout` event.
- Recommendations with tradeoffs: introduce payment bounded context + event-driven order updates; use saga with compensations.
- Validation plan: load-test event throughput; run migration rehearsal.
- Decisions/ADRs and next steps: draft ADR for event schema and ownership.
