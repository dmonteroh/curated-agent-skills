# System Manual Template (Long-Form Deep Dive)

Use this only when you truly need a book-like, durable reference (e.g., onboarding a team onto a complex system, regulated environments, or long-lived platforms). Default to smaller docs otherwise.

Output suggestion:
- `docs/manual/README.md` (entrypoint + index)
- `docs/manual/chapters/*.md`

## Template (copy/paste)

```md
# System Manual: <System Name>

Audience: <devs / ops / both>
Last updated: YYYY-MM-DD

## 0. How To Use This Manual

- If you are new: read Chapters 1–3 first.
- If you are operating: jump to Chapters 8–9.
- If you are debugging: jump to Chapters 6–7 and runbooks.

## 1. Executive Summary (1–2 pages)

- What this system is for
- What it is not for (non-goals)
- Key risks and invariants

## 2. Architecture Overview

- System boundary
- Major components and responsibilities
- Key data flows (diagram)
- Integration points (diagram)

## 3. Domain Concepts & Vocabulary

- Core entities, states, invariants
- Glossary of terms

## 4. External Interfaces / Contracts

- Public APIs (endpoints, schemas, error contracts)
- Event contracts (topics, payloads, ordering semantics)
- Data contracts (tables, schema guarantees)

## 5. Data Model & Persistence

- High-level data model (diagram)
- Migrations approach and operational constraints
- Consistency model / concurrency / transactions

## 6. Core Flows (Happy Path + Edge Cases)

For each flow:
- Preconditions
- Steps (sequence diagram)
- State transitions
- Failure modes and expected behavior

## 7. Error Handling & Reliability Semantics

- Retry policy and idempotency behavior (if relevant)
- Timeouts and backpressure
- Degradation strategy
- “What happens when X is down?”

## 8. Security Model

- Authentication and session model
- Authorization model
- Secrets handling
- Threats and mitigations (high-level)

## 9. Observability & Operations

- Logs (structure, correlation IDs)
- Metrics (golden signals, SLOs)
- Tracing (spans, propagation)
- Common dashboards and alerts

## 10. Deployment & Environments

- Environments (dev/stage/prod) and what differs
- Config and feature flags
- Release process and rollback strategy

## 11. Performance Characteristics

- Known bottlenecks and why
- Capacity expectations
- Profiling approach

## 12. Appendix

- Glossary
- Links to ADRs (optional)
- Links to specs/tracks/tasks (optional)
```

