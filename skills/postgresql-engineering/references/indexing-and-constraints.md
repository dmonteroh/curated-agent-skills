# Indexing and constraints

## Index types

| Type | Reach for it when | Notes |
| --- | --- | --- |
| B-tree | equality, range, and `ORDER BY` on scalar columns | the default; what `PRIMARY KEY` and `UNIQUE` create implicitly |
| Composite | a predicate filters on more than one column | column order decides usability — see below |
| Covering (`INCLUDE`) | the query's whole projection can come from the index | `CREATE INDEX ON t (id) INCLUDE (name, email)` keeps non-key columns in the index so the heap is never visited |
| Partial (`WHERE`) | only a subset of rows is ever queried | `CREATE INDEX ON t (user_id) WHERE status = 'active'` — only queries carrying that same predicate can use it, and an `ON CONFLICT` inference has to repeat the predicate to match it |
| Expression | the search key is computed | `CREATE INDEX ON t (lower(email))` — the query's expression must match the index's exactly, character for character |
| GIN | JSONB containment/key existence, array containment and overlap (`@>`, `&&`), full-text (`@@`) | |
| GiST | range and geometric types, and every `EXCLUDE` constraint | |
| BRIN | very large tables whose physical row order correlates with the column (append-only time series) | tiny next to a B-tree; worthless once the correlation is lost, so re-check it after bulk deletes or a rewrite |

## Composite index column order

`WHERE a = ? AND b > ?` can use an index on `(a, b)`. `WHERE b = ?` cannot: only a leftmost prefix of the index columns is matchable. Order accordingly — equality-filtered columns first (most selective first among those), then the column carrying a range predicate or the `ORDER BY`, last.

An index on `(b, a)` for that query is not a slower version of the right index; it is an unused one. Verify by reading the plan: if the index name does not appear, the ordering is wrong, not the statistics.

## EXCLUDE constraints

`EXCLUDE` generalizes `UNIQUE`: instead of rejecting rows that are equal, it rejects rows whose values are related by any operator. The common case is preventing overlapping ranges.

```sql
CREATE TABLE bookings (
  booking_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  room_id        BIGINT NOT NULL REFERENCES rooms(room_id),
  booking_period TSTZRANGE NOT NULL,
  EXCLUDE USING gist (room_id WITH =, booking_period WITH &&)
);
```

This makes double-booking a constraint violation rather than a race the application has to win. It needs a range (or geometric) type for the overlapping column and a GiST index, which the constraint creates; mixing a scalar column such as `room_id` into the same constraint needs the `btree_gist` extension.

Pick a range-bounds scheme and use it everywhere — `[)` (inclusive lower, exclusive upper) is the default worth standardizing on, because adjacent periods then do not overlap.

Verification: insert two overlapping periods for the same key. The second insert must fail. If it succeeds, the constraint is missing an operator or was written against the wrong columns.

## DEFERRABLE constraints

A constraint declared `DEFERRABLE INITIALLY DEFERRED` is checked once at commit rather than per statement. Use it where two tables reference each other and neither row can be inserted first, or where a batch temporarily violates a uniqueness rule mid-transaction (renumbering an ordered list, for example).

Cost: the violation surfaces at `COMMIT`, far from the statement that caused it, and the check is done for the whole transaction at once. Default to immediate checking and defer only where the cycle genuinely requires it.

## UNIQUE and NULLs

`UNIQUE` treats NULLs as distinct from one another, so `(1, NULL)` can be inserted any number of times. Declare `UNIQUE (...) NULLS NOT DISTINCT` (PG15 and later) as the default and relax it only where duplicate NULL rows are genuinely wanted; otherwise a nullable column quietly accumulates the exact duplicates the constraint was added to prevent.

## Foreign-key indexing

Postgres creates an index for the *referenced* side (the PK/UNIQUE it points at) and none for the *referencing* column. Without one, every parent delete or key update scans the child table, and the scan holds locks while it runs.

This query lists foreign-key columns with no index that mentions them:

```sql
SELECT c.conrelid::regclass AS table_name,
       a.attname            AS column_name,
       c.conname            AS constraint_name
FROM pg_constraint c
JOIN pg_attribute a
  ON a.attrelid = c.conrelid
 AND a.attnum = ANY (c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
        SELECT 1
        FROM pg_index i
        WHERE i.indrelid = c.conrelid
          AND a.attnum = ANY (i.indkey)
      );
```

An empty result means every FK column is mentioned by at least one index. Read the output as a lower bound, not a complete answer: a column that appears only in a trailing position of some composite index counts as covered here, even though such an index usually cannot serve the FK check — leftmost-prefix rules still apply.
