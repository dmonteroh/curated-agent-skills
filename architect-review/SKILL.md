---
name: architect-review
description: Review system designs and major changes for architectural integrity,
  scalability, and maintainability; use for architecture decisions, tradeoffs, and
  risks across distributed systems and clean architecture patterns.
category: architecture
---
# Architect Review
Provides architectural review guidance for system designs and major changes, focusing on scalability, resilience, maintainability, and tradeoffs across distributed systems and clean architecture patterns.

## Use this skill when

- Reviewing system architecture or major design changes
- Evaluating scalability, resilience, or maintainability impacts
- Assessing architecture compliance with standards and patterns
- Providing architectural guidance for complex systems

## Trigger phrases
- "architectural review" or "architecture review"
- "system design review" or "design review"
- "microservices boundaries" or "bounded contexts"
- "event-driven architecture" or "clean architecture"
- "scalability risk" or "resilience tradeoffs"

## Do not use this skill when

- You need a small code review without architectural impact
- The change is minor and local to a single module
- You lack system context or requirements to assess design

## Instructions

### Required inputs
- System context: current architecture, key components, and data flows
- Change description: what is being added/changed and why
- Constraints: non-functional requirements (scalability, resilience, security, cost)
- Dependencies: key integrations or platform constraints
- Optional artifacts: diagrams, ADRs, API contracts, deployment topology

### Workflow
1. Confirm scope and inputs; list missing context.
   - Output: concise context summary + open questions.
   - Decision: if critical context is missing, ask targeted questions and pause.
2. Map the current architecture and change impact.
   - Output: architecture snapshot + assumptions.
3. Evaluate decisions against goals and quality attributes.
   - Output: impact rating (High/Medium/Low) + risk list.
4. Identify architectural violations or anti-patterns.
   - Output: findings with evidence or reasoning.
5. Recommend improvements with tradeoffs and alternatives.
   - Output: prioritized recommendations with pros/cons.
6. Define validation and follow-up actions.
   - Output: verification plan (tests, load checks, PoC, rollout guardrails).
7. Document decisions and next steps.
   - Output: ADR suggestion list and owners if provided.

## Safety

- Avoid approving high-risk changes without validation plans.
- Document assumptions and dependencies to prevent regressions.

## Pitfalls to avoid
- Reviewing without clear constraints or goals
- Ignoring data flows, failure modes, or operational requirements
- Suggesting over-engineering without a tradeoff analysis
- Missing cross-service impact or migration complexity

## Output contract
Provide an **Architectural Review Report** using this format:
- Context summary (including assumptions and open questions)
- Impact rating (High/Medium/Low)
- Findings and risks
- Recommendations with tradeoffs
- Validation plan
- Decisions/ADRs and next steps

## References
See `references/README.md` for detailed reference guides and knowledge areas.

## Example
**Input:** "We want to split a monolith into services for payments and orders; review the design for boundaries and data ownership."

**Output (excerpt):**
- Context summary: current monolith with shared order/payment tables; new services for orders and payments.
- Impact rating: High (data migration + cross-service transactions).
- Findings and risks: shared database coupling; missing saga/outbox strategy.
- Recommendations with tradeoffs: introduce payment bounded context + event-driven order updates; use saga with compensations.
- Validation plan: load-test event throughput; run migration rehearsal.
- Decisions/ADRs and next steps: draft ADR for event schema and ownership.

## Trigger test
- "Can you do an architectural review of our new event-driven workflow?"
- "Evaluate the scalability risks of this microservices proposal."

## Example Interactions
- "Review this microservice design for proper bounded context boundaries"
- "Assess the architectural impact of adding event sourcing to our system"
- "Evaluate this API design for REST and GraphQL best practices"
- "Review our service mesh implementation for security and performance"
- "Analyze this database schema for microservices data isolation"
- "Assess the architectural trade-offs of serverless vs. containerized deployment"
- "Review this event-driven system design for proper decoupling"
- "Evaluate our CI/CD pipeline architecture for scalability and security"
