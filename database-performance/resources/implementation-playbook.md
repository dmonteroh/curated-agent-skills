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

