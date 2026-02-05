# Zero-downtime strategies

## Expand/contract pattern

**Phase 1: Expand (backward compatible)**

```sql
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
CREATE INDEX CONCURRENTLY idx_users_email_verified ON users(email_verified);
```

**Phase 2: Backfill (batching)**

```sql
-- Repeat this statement in separate transactions until rows_updated = 0.
WITH batch AS (
    SELECT id
    FROM users
    WHERE email_verified IS NULL
    ORDER BY id
    LIMIT 10000
)
UPDATE users
SET email_verified = (email_confirmation_token IS NOT NULL)
FROM batch
WHERE users.id = batch.id;
```

**Phase 3: Contract (after app deploy)**

```sql
ALTER TABLE users DROP COLUMN email_confirmation_token;
```

## Blue/green schema migration

1) Create the new table or schema version.
2) Dual-write via triggers or application logic.
3) Backfill historical data in batches.
4) Cut over reads and remove old structures later.

```sql
CREATE TABLE v2_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_v2_orders_customer
        FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE OR REPLACE FUNCTION sync_orders_to_v2()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO v2_orders (id, customer_id, total_amount, status)
    VALUES (NEW.id, NEW.customer_id, NEW.amount, NEW.state)
    ON CONFLICT (id) DO UPDATE SET
        total_amount = EXCLUDED.total_amount,
        status = EXCLUDED.status;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_orders_trigger
AFTER INSERT OR UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION sync_orders_to_v2();
```

## Online schema change (PostgreSQL example)

```sql
ALTER TABLE large_table ADD COLUMN new_field VARCHAR(100);

UPDATE large_table
SET new_field = 'default_value'
WHERE new_field IS NULL;

ALTER TABLE large_table
    ADD CONSTRAINT chk_new_field_not_null
    CHECK (new_field IS NOT NULL) NOT VALID;

ALTER TABLE large_table
    VALIDATE CONSTRAINT chk_new_field_not_null;
```
