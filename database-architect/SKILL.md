---
name: database-architect
description: "Design data layers and database architectures by selecting storage models, modeling schemas, and planning safe evolution with tradeoffs and migration/rollback plans. Use when making data-layer decisions or re-architecting storage." 
category: database
---

# Database Architect

This skill is DB-architecture and modeling focused (not query-by-query tuning).

## Use this skill when

- Choosing a database or storage pattern (relational, document, time-series, search)
- Designing schemas, constraints, and indexes for real access patterns
- Planning sharding/partitioning/replication and lifecycle policies
- Re-architecting an existing data layer or planning a migration

## Trigger phrases

- "choose the right database"
- "design the schema and indexes"
- "plan a data migration"
- "model entities and relationships"
- "partitioning or sharding strategy"

## Do not use this skill when

- You only need query tuning or a single slow query fix
- You need vendor-specific operational runbooks

## Workflow (Deterministic)

1) Inputs (must be explicit)
- Entities + invariants (what must always be true).
- Access patterns (reads/writes, filters/sorts/joins, hot paths).
- Scale targets (rows, QPS, retention, growth).
- Consistency + latency requirements (and what can be eventually consistent).
Output: requirements summary with assumptions and open questions.

2) Pick the storage model
- Start with the simplest model that fits invariants and access patterns.
- Consider operational complexity and failure modes, not just raw throughput.
Decision: If invariants require strong relational constraints, prefer relational.
Decision: If primary access is time-windowed append, prefer time-series/partitioning.
Output: 2-3 candidate storage models with tradeoffs.

3) Model the data
- Tables/collections, primary keys, relationships.
- Constraints for invariants (NOT NULL, UNIQUE, CHECK, FK where appropriate).
- Indexes for real access paths (not theoretical ones).
Output: schema sketch + index plan tied to access patterns.

4) Plan evolution + safety
- Migration steps (expand/contract when needed).
- Backups, rollback strategy, and validation plan.
Output: migration/rollback plan with verification steps.

5) Synthesize recommendation
- Choose the primary option and note why alternatives were rejected.
- Provide operational risks and mitigations.
Output: final recommendation in the reporting format below.

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

## Trigger test

- "Help pick a database for a multi-tenant analytics app and design the schema."
- "We need a safe plan to migrate from a single table to partitioned storage."

## References (Optional)

- See `references/README.md`
