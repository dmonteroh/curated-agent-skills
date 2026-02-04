# ORM Migration Playbook (Safe-by-Default)

Use this when your migration workflow is driven by an ORM tool (Prisma/TypeORM/Sequelize/EF, etc.).

Goal: keep production safe while still using ORM tooling.

## Core principles

- Prefer **expand/contract** even when using an ORM.
- Avoid long locks and table rewrites in peak hours.
- Large backfills should be **batched and throttled** (often outside the migration runner).

## Safe pattern: expand/contract

1) Expand (backward compatible)
- Add nullable column / new table / new index.
- Deploy app that writes both old+new (or supports both).

2) Backfill (online)
- Run batched backfill with explicit progress tracking.
- Throttle to protect DB latency.

3) Contract (cleanup)
- Remove old column/paths only after verifying all clients are migrated.

## Backfills (don’t do them in a single transaction)

- Prefer an application job/CLI that:
  - processes batches by primary key
  - commits each batch
  - can be resumed safely
  - emits progress metrics/logs

## Verification checklist

- Schema matches expectations (on staging first).
- App still works with mixed versions (backward compatibility period).
- Index creation does not block writes (use online/concurrent options where supported).
- Rollback plan is written (what is reversible vs forward-only).
