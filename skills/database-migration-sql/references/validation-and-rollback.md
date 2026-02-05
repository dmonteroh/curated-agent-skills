# Validation and rollback

## Pre-migration validation queries

```sql
-- Null check on required column
SELECT COUNT(*) AS null_count
FROM users
WHERE email IS NULL;

-- Duplicate check for uniqueness
SELECT email, COUNT(*) AS count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

## Post-migration validation queries

```sql
-- Row count verification
SELECT COUNT(*) FROM users;

-- Ensure new column populated
SELECT COUNT(*) AS missing_status
FROM orders
WHERE status IS NULL;
```

## Rollback guidance

- If data is transformed or backfilled, treat rollback as forward-only and keep the old column until validated.
- If a change is additive and unused, rollback can drop the new column or index.
- Always document irreversible steps in the rollback plan.

## Example rollback script (PostgreSQL)

Requirements: `bash`, `psql`, `pg_dump`.

Usage:

```bash
./rollback.sh <migration_version> <database_name>
```

Verification:

```bash
psql -d <database_name> -c "SELECT version FROM schema_migrations ORDER BY applied_at DESC LIMIT 1;"
```

```bash
#!/bin/bash
set -e

MIGRATION_VERSION=$1
DATABASE=$2

CURRENT_VERSION=$(psql -d "$DATABASE" -t -c \
  "SELECT version FROM schema_migrations ORDER BY applied_at DESC LIMIT 1" | xargs)

if [ "$CURRENT_VERSION" != "$MIGRATION_VERSION" ]; then
  echo "Version mismatch"
  exit 1
fi

BACKUP_FILE="pre_rollback_${MIGRATION_VERSION}.sql"
pg_dump -d "$DATABASE" -f "$BACKUP_FILE"

psql -d "$DATABASE" -f "migrations/${MIGRATION_VERSION}.down.sql"
psql -d "$DATABASE" -c \
  "DELETE FROM schema_migrations WHERE version = '$MIGRATION_VERSION';"
```
