# Migration script patterns

## Forward-only SQL template

```sql
-- V042__add_orders_status.sql
BEGIN;

ALTER TABLE orders ADD COLUMN IF NOT EXISTS status TEXT;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status
    ON orders(status);

COMMIT;
```

## Naming guidance

- Prefer versioned names (`V042__add_orders_status.sql`) or timestamped names if your tool requires them.
- Keep one logical change per file to simplify rollback guidance.

## Idempotency guidance

- Use `IF NOT EXISTS`/`IF EXISTS` guards where supported.
- Avoid re-running destructive statements without explicit checks.
- Separate expand and contract phases into distinct files.
