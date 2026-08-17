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

## Naming guidance

- Prefer versioned names (`V042__add_orders_status.sql`) or timestamped names if your tool requires them.
- Keep one logical change per file to simplify rollback guidance.

## Idempotency guidance

- Use `IF NOT EXISTS`/`IF EXISTS` guards where supported.
- Avoid re-running destructive statements without explicit checks.
- Separate expand and contract phases into distinct files.
