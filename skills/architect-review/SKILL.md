---
name: architect-review
description: "Review system designs and major changes for architectural integrity, scalability, and maintainability; use for architecture decisions, tradeoffs, and risks across distributed systems and clean architecture patterns."
metadata:
  category: architecture
---
# Architect Review
Provides architectural review guidance for system designs and major changes, focusing on scalability, resilience, maintainability, and tradeoffs across distributed systems and clean architecture patterns.

## Use this skill when

- Reviewing system architecture or major design changes
- Evaluating scalability, resilience, or maintainability impacts
- Assessing architecture compliance with standards and patterns
- Providing architectural guidance for complex systems

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

## Safety

- Avoid approving high-risk changes without validation plans.
- Document assumptions and dependencies to prevent regressions.

## Pitfalls to avoid
- Reviewing without clear constraints or goals
- Ignoring data flows, failure modes, or operational requirements
- Suggesting over-engineering without a tradeoff analysis
- Missing cross-service impact or migration complexity
- Skipping the premise check and reviewing a design for a problem that may not be the right one to solve
- Designing or approving a new component before checking whether an existing asset already covers the need
- Treating failure-mode coverage as a prose judgment call instead of a table — a gap hides easily in a paragraph and stands out in a row with an empty cell

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
Format the premise check, reuse-first audit, and failure modes registry as tables; format the remaining sections as bullet points. Label each finding as `blocking` or `advisory`. In the failure modes registry, a row is complete only when rescued?, test?, and the visibility columns all carry a concrete answer — a missing or hedged cell is a gap, not a stylistic choice.

## References
See `references/README.md` for detailed reference guides and knowledge areas.

## Example
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

## Example Interactions
- "Review this microservice design for proper bounded context boundaries"
- "Assess the architectural impact of adding event sourcing to our system"
- "Evaluate this API design for REST and GraphQL best practices"
- "Review our service mesh implementation for security and performance"
- "Analyze this database schema for microservices data isolation"
- "Assess the architectural trade-offs of serverless vs. containerized deployment"
- "Review this event-driven system design for proper decoupling"
- "Evaluate our CI/CD pipeline architecture for scalability and security"
