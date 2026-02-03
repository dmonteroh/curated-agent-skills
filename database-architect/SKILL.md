---
name: database-architect
description: "Design data layers and database architectures: data modeling, technology selection, schema/index strategy, lifecycle/retention, and safe evolution. Produces tradeoffs + migration/rollback plans. Use PROACTIVELY for data-model decisions."
category: database
---

# Database Architect

This skill is DB-architecture and modeling focused (not query-by-query tuning).

## Use this skill when

- Choosing a database or storage pattern (relational, document, time-series, search)
- Designing schemas, constraints, and indexes for real access patterns
- Planning sharding/partitioning/replication and lifecycle policies
- Re-architecting an existing data layer or planning a migration

## Do not use this skill when

- You only need query tuning or a single slow query fix (use database-performance / sql-querying)
- You need a database-specific playbook (use postgresql-engineering for Postgres)

## Workflow (Deterministic)

1) Inputs (must be explicit)
- Entities + invariants (what must always be true).
- Access patterns (reads/writes, filters/sorts/joins, hot paths).
- Scale targets (rows, QPS, retention, growth).
- Consistency + latency requirements (and what can be eventually consistent).

2) Pick the storage model
- Start with the simplest model that fits invariants and access patterns.
- Consider operational complexity and failure modes, not just raw throughput.

3) Model the data
- Tables/collections, primary keys, relationships.
- Constraints for invariants (NOT NULL, UNIQUE, CHECK, FK where appropriate).
- Indexes for real access paths (not theoretical ones).

4) Plan evolution + safety
- Migration steps (expand/contract when needed).
- Backups, rollback strategy, and validation plan.

## Output Contract (Always)

- Recommended data model + key invariants
- 2-3 alternatives with tradeoffs (including operational complexity)
- Indexing/partitioning approach tied to access patterns
- Migration/rollout/rollback plan + verification steps

## References (Optional)

- Tech selection and tradeoffs: `references/tech-selection.md`
- Modeling and schema checklist: `references/modeling-checklist.md`
- Migration safety patterns: `references/migration-safety.md`

