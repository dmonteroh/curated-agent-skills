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

### Capture the deadlock report before anything else

An engine's deadlock diagnostic is usually a single-slot buffer holding only the *most recent* deadlock — InnoDB's `SHOW ENGINE INNODB STATUS` is the common case, and the equivalent view on other engines has the same shape. The next deadlock overwrites it. So the capture is the first action after the report arrives, ahead of retrying the transaction, ahead of reproducing it, and ahead of reasoning about it: a retry that deadlocks again destroys the record of the deadlock under investigation, and so does any unrelated deadlock elsewhere in the workload.

Persist the raw output into the incident record rather than reading it in a session. Where deadlocks are frequent enough that a human cannot win that race, make the capture automatic instead of manual: log the diagnostic from the application's deadlock error path, or enable the engine's option for appending every deadlock to the error log where one exists. *(Authored: the source states the overwrite hazard and the manual capture, not what to do when deadlocks arrive faster than an operator can read them.)*

Failure looks like: an investigation reconstructed from application error logs alone, because the diagnostic was opened after the next deadlock had already replaced it — the two transactions, the locks each held, and the one the engine chose to roll back are all unrecoverable at that point.

## Connection pooling

- Ensure the app uses a pool (and that the pool size is sane).
- Avoid “too many connections” (it can reduce throughput).
- Ensure timeouts are explicit:
  - connect timeout
  - statement/query timeout
  - transaction timeout (if supported)

### Recycle pooled connections below the server's idle timeout

The server closes idle connections on its own schedule, and it does not tell the pool. If the pool holds a connection longer than the server's idle-connection timeout, it eventually hands the application a socket the server has already closed. The rule is the relation, not any particular pair of values: **the pool's connection-recycle interval sits below the server's idle timeout, with margin.** Read that server-side timeout out of the running server's configuration rather than assuming its default, since it is routinely tuned per deployment, and re-check it whenever the database is reconfigured or replaced.

The symptom this prevents is easy to misdiagnose: intermittent connection-reset or "server has gone away" errors on the *first* statement after a quiet period, spread across unrelated endpoints, with no correlation to load or to any particular query. Under load the pool recycles naturally and the errors disappear, so the failure looks worse the healthier the traffic is.

Validate-on-checkout (pre-ping) is a complement, not a replacement. It catches connections lost to failover and network events that no timeout relation can predict, and it costs one round trip per checkout; it does not make an over-long recycle interval correct. *(Authored: the source pairs the two settings without ranking them; the ordering matters because pre-ping is the setting reached for first and it masks the misconfiguration instead of fixing it.)*

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
