---
name: database-architect
description: "Design data layers and database architectures by selecting storage models, modeling schemas, and planning safe evolution with tradeoffs and migration/rollback plans. Use when making data-layer decisions or re-architecting storage."
category: database
---
# Database Architect

Provides database architecture and modeling guidance (not query-by-query tuning).

## Use this skill when

Use this skill when durable data-layer decisions are needed, not short-term query fixes.

- Choosing a database or storage pattern (relational, document, time-series, search)
- Designing schemas, constraints, and indexes for real access patterns
- Planning sharding/partitioning/replication and lifecycle policies
- Re-architecting an existing data layer or planning a migration

## Do not use this skill when

- Only query tuning or a single slow query fix is needed
- Vendor-specific operational runbooks are required

## Required inputs

- Entities + invariants (what must always be true)
- Access patterns (reads/writes, filters/sorts/joins, hot paths)
- Scale targets (rows, QPS, retention, growth)
- Consistency + latency requirements
- Migration constraints (downtime tolerance, rollback expectations)

## Workflow (Deterministic)

1) Collect inputs (must be explicit)
- Captures entities + invariants (what must always be true).
- Captures access patterns (reads/writes, filters/sorts/joins, hot paths).
- Captures scale targets (rows, QPS, retention, growth).
- Captures consistency + latency requirements (and what can be eventually consistent).
Decision: If critical inputs are missing, pause and ask targeted questions before proceeding.
Produces: requirements summary with assumptions and open questions.

2) Select the storage model
- Starts with the simplest model that fits invariants and access patterns.
- Considers operational complexity and failure modes, not just raw throughput.
Decision: If invariants require strong relational constraints, prefer relational.
Decision: If primary access is time-windowed append, prefer time-series/partitioning.
Decision: If OLTP + analytics needs diverge, recommend separating systems with a clear source of truth.
Produces: 2-3 candidate storage models with tradeoffs.

3) Model the data
- Defines tables/collections, primary keys, relationships.
- Specifies constraints for invariants (NOT NULL, UNIQUE, CHECK, FK where appropriate).
- Maps indexes to real access paths (not theoretical ones).
Decision: If read performance dominates and invariants allow, denormalize with compensating checks.
Produces: schema sketch + index plan tied to access patterns.

4) Plan evolution + safety
- Describes migration steps (expand/contract when needed).
- Documents backups, rollback strategy, and validation plan.
Decision: If the change is breaking or large, use expand/contract with staged verification.
Produces: migration/rollback plan with verification steps.

5) Synthesize recommendation
- Selects the primary option and notes why alternatives were rejected.
- Provides operational risks and mitigations.
Produces: final recommendation in the reporting format below.

## Common pitfalls

- Designing indexes without mapping to top queries
- Picking storage tech before clarifying invariants
- Ignoring rollback/verification steps for migrations
- Assuming consistency/latency requirements without confirmation

## Output Contract (Always)

- Recommended data model + key invariants
- 2-3 alternatives with tradeoffs (including operational complexity)
- Indexing/partitioning approach tied to access patterns
- Migration/rollout/rollback plan + verification steps

## Reporting format

1) Requirements summary
2) Recommended architecture
3) Alternatives + tradeoffs
4) Schema + indexing plan
5) Migration + rollback plan
6) Risks, mitigations, and open questions

## Example

Input: "We need to store orders and order items, report daily revenue, and handle 2k writes/sec with 2 years retention. Strong consistency required for inventory updates."

Output (abridged):
1) Requirements summary: orders/items entities, strong consistency on inventory, 2k writes/sec, 2-year retention.
2) Recommended architecture: relational DB with partitioned orders table by month.
3) Alternatives + tradeoffs: document DB (simpler writes, weaker constraints), time-series (good for reporting but needs relational source).
4) Schema + indexing plan: orders PK, order_items FK, index on order_date + customer_id.
5) Migration + rollback plan: expand/contract steps, backfill, read switch, rollback path.
6) Risks/open questions: inventory consistency SLA, retention archival storage.

## References (Optional)

- See `references/README.md`
