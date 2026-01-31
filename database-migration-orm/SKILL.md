---
name: database-migration-orm
description: Plan and execute ORM-managed database migrations (Prisma/TypeORM/Sequelize/EF) with zero-downtime patterns, safe backfills, and rollback discipline. Use only for ORM migration tooling (not raw SQL-file migration workflows).
---

# Database Migration (ORM)

This skill is intentionally ORM-oriented. If the repo uses raw SQL migrations, use the SQL migration skill instead.

## Use this skill when

- Creating or reviewing ORM migrations (schema + data transforms)
- Planning safe, staged rollouts (expand/contract) with backfills
- Debugging migration failures, drift, or inconsistent environments

## Do not use this skill when

- The project uses forward-only SQL migration files as the primary mechanism
- You are only tuning queries (use database-performance / sql-querying)

## Workflow (Deterministic)

1) Identify the change type
- Pure schema change vs data backfill vs both.
- Online/zero-downtime requirement? If yes, expand/contract is the default.

2) Choose the safest rollout
- Expand: add new columns/tables (nullable or default-safe).
- Backfill: migrate data in controlled batches.
- Switch reads/writes in application code.
- Contract: drop old fields only after verifying no usage.

3) Verify and gate
- Run migration on a copy of production-like data size when possible.
- Confirm runtime safety (locks, timeouts, long transactions).
- Define rollback: can we revert schema? can we re-run safely? what is irreversible?

4) Observability and cleanup
- Track backfill progress and error rates.
- Document operational steps for production runs (runbook).

## Output Contract (Always)

- Migration plan (steps, order, safety gates)
- Rollback plan (what is reversible vs not)
- Verification steps (staging rehearsal + prod monitoring)

## Resources (Optional)

- Implementation playbook with examples and checklists: `resources/implementation-playbook.md`

