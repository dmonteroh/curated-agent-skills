---
name: database-performance
description: "Diagnose and fix database performance issues (slow queries, locks, pool saturation, caching, partitioning) using evidence from metrics and query plans."
category: database
---
# Database Performance

## Use this skill when

- Investigating slow queries, timeouts, or lock contention.
- Tuning indexes, queries, connection pooling, caching, or partitioning.
- Latency/throughput regressions likely originate in the database layer.

## Do not use this skill when

- Choosing a database or designing a schema from scratch.
- The bottleneck is clearly outside the database (app CPU, upstream APIs, network).

## Required inputs

- Database engine + version.
- Problematic queries/endpoints (with parameters if possible).
- Baseline metrics (p95/p99 latency, throughput, error rate).
- Concurrency, timeouts, and current pool size.
- Constraints (uptime requirements, migration windows, read/write mix).

## Workflow (step-by-step)

1. **Confirms scope and baseline.**
   - Output: concise problem statement + baseline metrics table.
2. **Collects evidence.**
   - Gathers query plans (`EXPLAIN`/equivalent), slow query logs, and lock/connection stats.
   - Output: evidence summary and the top 3–5 suspects.
3. **Classifies the bottleneck (decision points).**
   - If plans show sequential/full scans on selective filters → propose index or rewrite.
   - If lock waits dominate → reduce transaction scope, adjust isolation, batch writes.
   - If pool saturation → right-size pool, check DB max connections, add timeouts.
   - If IO/bloat → vacuum/analyze/rebuild strategy and data retention plan.
   - Output: primary bottleneck class + supporting evidence.
4. **Designs fixes with rollout safety.**
   - Provides 1–3 ranked options with risks, expected impact, and required changes.
   - Includes zero/low-downtime rollout guidance (concurrent index builds where supported).
   - Output: recommended change set + verification criteria.
5. **Validates and guards against regressions.**
   - Specifies before/after metrics, plan diffs, and any test/benchmark additions.
   - Output: validation checklist + rollback plan.

## Common pitfalls to avoid

- Adding indexes without verifying selectivity or plan changes.
- Increasing pool size beyond DB capacity, causing worse contention.
- Caching without a clear invalidation strategy.
- Optimizing without baseline metrics or measurable success criteria.
- Large updates in single transactions that amplify lock time.

## Examples

**Example 1: slow query**
- Input: “Our `orders` search endpoint times out at p99. Here’s the query and EXPLAIN.”
- Output: diagnosis of scan/join issue, recommended composite index, and a verification plan.

**Example 2: lock contention**
- Input: “We see elevated lock waits after a bulk backfill.”
- Output: batch update plan, reduced transaction scope, and rollback steps.

## Output format

Produces a report with these sections:

- **Summary**: 2–3 sentence diagnosis.
- **Evidence**: key metrics, plans, and logs used.
- **Findings**: bottleneck class + reasoning.
- **Recommendations**: ranked fixes with expected impact.
- **Validation Plan**: metrics to confirm improvement.
- **Risks/Rollback**: safety notes and rollback steps.
- **Open Questions**: missing inputs needed to proceed.

## References

- `references/README.md`
