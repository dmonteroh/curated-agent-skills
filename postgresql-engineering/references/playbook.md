# PostgreSQL Engineering - Playbook

This file contains the detailed Postgres guidance that was intentionally moved out of the skill entrypoint to keep it fast.

## Core Rules

- Define a **PRIMARY KEY** for reference tables (users, orders, etc.). Not always needed for time-series/event/log data. When used, prefer `BIGINT GENERATED ALWAYS AS IDENTITY`; use `UUID` only when global uniqueness/opacity is needed.
- **Normalize first (to 3NF)** to eliminate data redundancy and update anomalies; denormalize **only** for measured, high-ROI reads where join performance is proven problematic. Premature denormalization creates maintenance burden.
- Add **NOT NULL** everywhere it’s semantically required; use **DEFAULT**s for common values.
- Create **indexes for access paths you actually query**: PK/unique (auto), **FK columns (manual!)**, frequent filters/sorts, and join keys.
- Prefer **TIMESTAMPTZ** for event time; **NUMERIC** for money; **TEXT** for strings; **BIGINT** for integer values, **DOUBLE PRECISION** for floats (or `NUMERIC` for exact decimal arithmetic).

## PostgreSQL “Gotchas”

- **Identifiers**: unquoted → lowercased. Avoid quoted/mixed-case names. Convention: use `snake_case` for table/column names.
- **Unique + NULLs**: UNIQUE allows multiple NULLs. Use `UNIQUE (...) NULLS NOT DISTINCT` (PG15+) to restrict to one NULL.
- **FK indexes**: PostgreSQL **does not** auto-index FK columns. Add them.
- **Sequences/identity have gaps** (normal; don't \"fix\"). Rollbacks, crashes, and concurrency create gaps in ID sequences.
- **Heap storage**: no clustered PK by default; `CLUSTER` is one-off reorg, not maintained.
- **MVCC**: updates/deletes leave dead tuples; vacuum handles them—design to avoid hot wide-row churn.

## Data Types (high-value guidance)

- **IDs**: `BIGINT GENERATED ALWAYS AS IDENTITY` preferred; `UUID` for federation/opaque IDs.
- **Strings**: prefer `TEXT`; use `CHECK (LENGTH(col) <= n)` if a hard limit matters.
- **Money**: `NUMERIC(p,s)` (never float).
- **Time**: `TIMESTAMPTZ` for timestamps; `now()` is transaction start time.
- **Enums**: use `ENUM` for small, stable sets; otherwise a lookup table.

## Partitioning (when it pays off)

- Use when retention or query patterns are time-sliced and tables are large.
- Partition by time ranges for append-heavy/event/log tables.
- Validate with real queries and avoid premature complexity.

## Upsert-friendly design

- `ON CONFLICT` requires a matching UNIQUE index on the conflict target.
- Update only changed columns to reduce write amplification.

## Safe schema evolution (rules of thumb)

- Prefer transactional DDL for safe testing.
- Use `CREATE INDEX CONCURRENTLY` to avoid blocking writes (cannot run in a transaction).
- Avoid table rewrites caused by volatile defaults when adding NOT NULL columns.

## JSONB guidance

- Prefer `JSONB` + GIN indexes for containment and key existence queries.
- Heavy containment workloads may benefit from `jsonb_path_ops` (containment only).
- For scalar fields used in filters/sorts, extract into generated/expression indexes.

## Examples

### Users

```sql
CREATE TABLE users (
  user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX ON users (LOWER(email));
CREATE INDEX ON users (created_at);
```

### Orders

```sql
CREATE TABLE orders (
  order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(user_id),
  status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','PAID','CANCELED')),
  total NUMERIC(10,2) NOT NULL CHECK (total > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON orders (user_id);
CREATE INDEX ON orders (created_at);
```

### JSONB with generated column

```sql
CREATE TABLE profiles (
  user_id BIGINT PRIMARY KEY REFERENCES users(user_id),
  attrs JSONB NOT NULL DEFAULT '{}',
  theme TEXT GENERATED ALWAYS AS (attrs->>'theme') STORED
);
CREATE INDEX profiles_attrs_gin ON profiles USING GIN (attrs);
```

