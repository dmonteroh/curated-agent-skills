# Database Performance Playbook (Tool-Agnostic)

This playbook is a pragmatic checklist for diagnosing and fixing database performance issues.

## Triage checklist (fast)

- What regressed? (date/time, deploy, migration, load change)
- Is it a single query or system-wide?
- Is the DB saturated? (CPU, IO, memory, connections)
- Are we blocked on locks?

## Query plan workflow

1) Capture the query + parameters (representative).
2) Capture the plan (`EXPLAIN` / equivalent) and runtime stats.
3) Ask:
- Are we scanning too much? (seq scan / full scan)
- Are joins exploding rows?
- Are we sorting/hashing large intermediate sets?
- Are we missing a selective index?
4) Fix options (in rough order of preference):
- add/adjust index (and verify selectivity)
- rewrite query (limit rows earlier; avoid correlated subqueries)
- change access pattern (precompute, materialize, or denormalize when justified)

## Indexing checklist

- Choose indexes based on real query patterns (not “index every FK” blindly).
- Composite indexes: order matters (most selective first, then join/filter, then sort).
- Avoid redundant indexes (write amplification).
- Consider partial indexes for hot subsets.

## Locks / contention

- Identify blockers and lock types.
- Reduce transaction scope; avoid holding locks across network calls.
- Use the weakest safe isolation level.
- Break large updates into batches.

## Connection pooling

- Ensure the app uses a pool (and that the pool size is sane).
- Avoid “too many connections” (it can reduce throughput).
- Ensure timeouts are explicit:
  - connect timeout
  - statement/query timeout
  - transaction timeout (if supported)

## Caching and read scaling

- Cache only when you have stable keys and clear invalidation strategy.
- Prefer “cache-aside” as a default.
- Read replicas help read scaling but complicate consistency; document it.

## Verification (required)

- Before/after metrics (latency, throughput, error rate).
- Plan diff (or equivalent evidence).
- Regression guard: add a benchmark/query test if feasible.

## Common optimization patterns (high ROI)

### Avoid `SELECT *`

Fetch only needed columns to reduce IO and improve index-only scan chances.

### Cursor/keyset pagination over large OFFSET

OFFSET pagination becomes slower as offsets grow.

- Prefer keyset (cursor) pagination:
  - `WHERE (created_at, id) < ($cursorCreatedAt, $cursorId)`
  - plus an index on `(created_at, id)` in the same ordering.

### Decide between an estimated and an exact count

An unfiltered `COUNT(*)` reads every row, or every entry of some index, on every call. An index-only scan lowers the constant factor but not the shape: the cost still grows with the table. Before tuning the query, establish which kind of count the caller actually needs.

- **An estimate is enough** for an "about N results" label, a dashboard tile, a capacity gauge, or a decision about whether to paginate at all. Read the planner's cached row estimate out of the catalog instead of scanning. Postgres: `SELECT reltuples::bigint FROM pg_class WHERE relname = 'orders';`. Other engines expose an equivalent estimate in their own statistics or catalog views. Accuracy tracks how recently statistics were refreshed, so the estimate is worst immediately after a bulk load and before the table is analyzed.
- **An exact count is required** for billing, reconciliation, an invariant check, or any number a user can dispute. Pay for the scan, but shrink it first: filter on an indexed column so the count runs over a selective index range rather than the whole table.

Verification: run the estimate and one exact count against the real table and compare. If the gap exceeds what the call site can tolerate, the estimate path is not usable there — report that rather than shipping it.

### Fix N+1 at the boundary

Symptoms:
- many similar queries differing only by an ID

Fixes:
- batch queries (`WHERE id IN (...)`)
- joins + aggregation
- application-side grouping after one batch fetch

### Reduce correlated subqueries

Replace “subquery per row” with:
- a join + group by
- or window functions (when appropriate)

### Batch large updates/backfills

Avoid single huge transactions:
- update by primary key ranges
- commit per batch
- throttle to protect p95 latency

### Know when indexes help vs hurt

- Indexes speed reads but slow writes.
- Remove redundant indexes; prefer partial indexes for hot subsets.

### Use materialization deliberately

When reads dominate and the query is expensive:
- materialized view / summary table
- incremental refresh strategy
- treat it as derived state (rebuildable)
