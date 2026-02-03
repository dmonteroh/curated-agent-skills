---
name: postgresql-engineering
description: "PostgreSQL-specific schema and data-layer engineering: DDL, data types, constraints, indexing, JSONB, partitioning, RLS, and safe schema evolution. Use when you are targeting Postgres specifically."
category: database
---

# PostgreSQL Engineering

This skill is Postgres-specific. Use it when you are making schema/data-layer decisions for PostgreSQL (not just writing SQL queries).

## Use this skill when

- Designing Postgres schemas, constraints, and indexing strategy
- Choosing Postgres data types (JSONB, arrays, enums, money/time types)
- Planning partitioning or RLS policies
- Reviewing schema changes for safety and operational impact

## Do not use this skill when

- You are targeting a non-PostgreSQL database
- You only need query authoring/tuning (use sql-querying / database-performance)
- You need DB-agnostic modeling guidance (use database-architect)

## Workflow (Deterministic)

1) Capture requirements
- Entities + invariants (what must always be true).
- Access paths (top queries, filters/sorts/joins).
- Scale targets (rows, QPS, retention) and operational constraints.

2) Design schema + constraints
- Use constraints for invariants (NOT NULL, UNIQUE, CHECK, FK where appropriate).
- Pick types intentionally (money/time/text/ids).

3) Index for real access paths
- Add indexes for join keys + frequent filters/sorts.
- Validate with `EXPLAIN (ANALYZE, BUFFERS)` when possible.

4) Plan safe evolution
- Use expand/contract for risky changes.
- Avoid production-breaking DDL without a rollback plan.

## Output Contract (Always)

- Schema proposal (tables/columns/constraints) tied to invariants
- Index plan tied to real access paths
- Migration/rollout/rollback plan + verification steps

## References (Optional)

- Full Postgres playbook (types, indexing, JSONB, migrations): `references/playbook.md`

