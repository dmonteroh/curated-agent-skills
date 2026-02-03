---
name: sql-querying
description: Write correct, maintainable SQL and design queries (joins, CTEs, window functions) for OLTP/analytics. Use for query authoring and query-level reasoning; for DB-wide performance diagnosis use database-performance, and for schema architecture use database-architect / postgresql-engineering.
category: database
---

# SQL Querying

This skill is for writing and reasoning about SQL: correctness first, then performance, then readability.

## Use this skill when

- Writing complex queries (joins, grouping, CTEs, window functions)
- Refactoring queries for readability and correctness
- Reasoning about query outputs and edge cases (NULLs, duplicates, join cardinality)
- Doing query-level optimization with EXPLAIN

## Do not use this skill when

- You need DB-wide performance diagnosis (index strategy, lock contention, pool sizing) — use `database-performance`
- You need to design a schema/data model from scratch — use `database-architect` (or `postgresql-engineering` if Postgres-specific)
- You need ORM-specific guidance — use an ORM/database migration skill

## Workflow (Deterministic)

1. Confirm target database/dialect (Postgres/MySQL/SQL Server/etc.).
2. Write the simplest correct query first.
3. Validate correctness with representative inputs (including edge cases).
4. Use EXPLAIN to validate plan changes.
5. If performance requires new indexes or systemic tuning, escalate to `database-performance`.

## Output Contract (Always)

- Final query (formatted) and a short explanation of shape (joins/CTEs/windows)
- Correctness notes (NULL handling, duplicate risk, cardinality assumptions)
- Optional: EXPLAIN guidance and what to look for

## References (Optional)

- Patterns: `references/query-patterns.md`
- Window functions: `references/window-functions.md`
- Dialect notes: `references/dialect-notes.md`
- EXPLAIN basics: `references/explain-basics.md`
