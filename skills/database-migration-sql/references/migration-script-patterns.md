# Migration script patterns

## Forward-only SQL templates

**Transactional DDL (no concurrent index)**

```sql
-- V042__add_orders_status.sql
BEGIN;

ALTER TABLE orders ADD COLUMN IF NOT EXISTS status TEXT;

CREATE INDEX IF NOT EXISTS idx_orders_status
    ON orders(status);

COMMIT;
```

**Non-transactional DDL (concurrent index)**

```sql
-- V043__add_orders_status_index.sql
ALTER TABLE orders ADD COLUMN IF NOT EXISTS status TEXT;

-- PostgreSQL: CREATE INDEX CONCURRENTLY cannot run inside a transaction.
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status
    ON orders(status);
```

## Adding a column without a table rewrite

```sql
-- Metadata-only: nullable, no default.
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- Metadata-only on PostgreSQL 11 and later: NOT NULL with a non-volatile
-- constant default. The default is stored as table metadata and existing
-- rows are not touched.
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;

-- Full rewrite under an exclusive lock: NOT NULL with no default at all.
ALTER TABLE users ADD COLUMN role TEXT NOT NULL;

-- Full rewrite: a volatile default must be evaluated once per row.
ALTER TABLE events ADD COLUMN correlation_id UUID NOT NULL DEFAULT gen_random_uuid();
```

The PostgreSQL 11 boundary is a version gate, not a universal rule: MySQL and SQL Server have their own rules for which `ALTER TABLE` forms are performed in place. Confirm the behavior for the exact engine and version recorded in the Constraints Summary before relying on any of these being instant — the claim is externally checkable in the engine's own release notes, so check it rather than assuming.

Where the rewrite-free form is unavailable on the target engine or version, add the column nullable, backfill in batches, then promote it with a `NOT VALID` check constraint followed by `VALIDATE CONSTRAINT` — see `references/zero-downtime-strategies.md`.

## Dialect forks: write the statement after the version check

The version answer captured in the Constraints Summary is not only a locking question. Engines that share a dialect name — a fork and its upstream, or two major versions of the same product — accept different syntax for the same operation, and both forms look correct in review because each one is valid somewhere. A statement written from habit therefore fails at run time, in the migration runner, against production.

The upsert is where this lands most often in a migration, because a backfill that has to be safely re-runnable is usually written as one. MySQL and MariaDB have diverged on how the inserted row is referenced inside `ON DUPLICATE KEY UPDATE`:

```sql
-- MySQL: reference the incoming row through a row alias.
-- The older VALUES(col) function form is deprecated there.
INSERT INTO user_settings (user_id, setting_key, setting_value, updated_at)
VALUES (?, ?, ?, CURRENT_TIMESTAMP) AS new
ON DUPLICATE KEY UPDATE
    setting_value = new.setting_value,
    updated_at    = new.updated_at;

-- MariaDB, and any mixed MySQL/MariaDB fleet: VALUES(col) is the supported
-- form, and the row alias above is not accepted.
INSERT INTO user_settings (user_id, setting_key, setting_value, updated_at)
VALUES (?, ?, ?, CURRENT_TIMESTAMP)
ON DUPLICATE KEY UPDATE
    setting_value = VALUES(setting_value),
    updated_at    = VALUES(updated_at);
```

The row-alias form arrived in a specific MySQL 8 minor release and is unavailable before it, so "MySQL" alone does not settle the choice — the exact version does. Both engines document which form applies to a given release; confirm there rather than from memory, the same check the PostgreSQL 11 boundary above requires. Where the migration must run unchanged across a mixed fleet, the form the fork still accepts is the portable one even when the upstream engine has deprecated it — record that as an assumption in the Constraints Summary so the deprecation is a known debt rather than a surprise at the next major upgrade.

Rehearsing against a production-sized copy (see the Gates in `SKILL.md`) exercises the locking behavior, not the dialect: a rehearsal run on the wrong fork proves nothing about the fork that will actually run the migration. Match the rehearsal engine and version to the target. *(Authored: the fork rule and the rehearsal gate come from different places, and nothing said the rehearsal has to run on the same fork.)*

## Naming guidance

- Prefer versioned names (`V042__add_orders_status.sql`) or timestamped names if your tool requires them.
- Keep one logical change per file to simplify rollback guidance.

## Idempotency guidance

- Use `IF NOT EXISTS`/`IF EXISTS` guards where supported.
- Avoid re-running destructive statements without explicit checks.
- Separate expand and contract phases into distinct files.
