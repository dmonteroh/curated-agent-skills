---
name: database-migration-sql
description: "Plan and write forward-only SQL migration files with zero-downtime patterns, validation, rollback guidance, and production safety checks for PostgreSQL, MySQL, and SQL Server."
category: database
---
# database-migration-sql

Provides guidance for planning and writing forward-only SQL migrations with zero-downtime patterns, validation, rollback guidance, and production safety checks for PostgreSQL, MySQL, and SQL Server.

## Use this skill when

- The task involves writing or operating versioned `.sql` migration files.
- The change needs expand/contract patterns for backwards compatibility.
- The work includes safe backfills, indexing changes, or large table changes in production.

## Do not use this skill when

- The workflow is ORM-managed migrations rather than raw SQL files.
- The task is primarily designing a new schema or data model.

## Required inputs

- Database engine and version.
- Migration tool or naming convention (Flyway, Liquibase, custom runner).
- Lock tolerance / maintenance window constraints.
- Expected data volume and critical tables.
- Rollback expectations (forward-only vs reversible).

## Workflow (step-by-step)

1) **Confirm constraints**
   - Ask for engine/version, locking tolerance, data volume, and migration runner.
   - Output: **Constraints Summary** with assumptions.
2) **Choose a safe strategy (decision point)**
   - If table is large or high-traffic, use expand/contract or blue/green.
   - If schema change is metadata-only and low risk, use transactional DDL.
   - Output: **Selected Strategy** with rationale.
3) **Draft migration SQL**
   - Use explicit transaction boundaries only when supported.
   - Prefer idempotent guards (`IF NOT EXISTS`, safe checks) where feasible.
   - Output: **Forward Migration SQL** with file names.
4) **Plan data backfill (decision point)**
   - If backfilling large tables, batch with throttling and resume markers.
   - Output: **Backfill Plan** including batch size and stop conditions.
5) **Define validation queries**
   - Provide pre/post checks for row counts, nulls, uniqueness, and constraints.
   - Output: **Validation Queries**.
6) **Provide rollback guidance**
   - State what is reversible and what is forward-only.
   - Output: **Rollback Plan** with manual steps or SQL where safe.
7) **Execution checklist**
   - Include verification, monitoring, and post-deploy checks.
   - Output: **Execution Checklist**.

## Common pitfalls

- Running blocking DDL without checking lock behavior.
- Backfilling without batch throttling on large tables.
- Forgetting pre/post validation queries.
- Assuming rollback is possible when data is transformed.
- Missing idempotency guards for repeated runs.

## Examples

**Example request**
"Create a zero-downtime migration to add `status` to `orders` and backfill from `state`."

**Example response (abridged)**
- Constraints Summary: PostgreSQL 13, high-traffic table, Flyway naming.
- Selected Strategy: Expand/contract with batch backfill.
- Forward Migration SQL: `V042__expand_orders_status.sql`.
- Backfill Plan: 10k rows/batch with `pg_sleep(0.1)`.
- Validation Queries: row count, null check for `status`.
- Rollback Plan: forward-only (data rewrite), keep old column until verified.

## Output format (contract)

Return responses in this order, using the exact headings:
1. **Constraints Summary**
2. **Selected Strategy**
3. **Forward Migration SQL**
4. **Backfill Plan**
5. **Validation Queries**
6. **Rollback Plan**
7. **Execution Checklist**

## Resources

- `references/README.md` for detailed patterns, examples, and checklists.
