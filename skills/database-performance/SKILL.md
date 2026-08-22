---
name: database-performance
description: "Diagnoses and fixes database performance issues — slow queries, lock contention, pool saturation, caching, partitioning — using evidence from metrics and query plans. Use when a latency or throughput regression traces to the database layer."
metadata:
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

## Workflow

1. **Confirm scope and baseline.**
   - Output: concise problem statement + baseline metrics table.
2. **Collect evidence.**
   - Gather query plans (`EXPLAIN`/equivalent), slow query logs, and lock/connection stats.
   - Output: evidence summary and the top 3–5 suspects.
3. **Classify the bottleneck (decision points).**
   - If plans show sequential/full scans on selective filters → propose index or rewrite.
   - If lock waits dominate → reduce transaction scope, adjust isolation, batch writes.
   - If pool saturation → right-size pool, check DB max connections, add timeouts.
   - If IO/bloat → vacuum/analyze/rebuild strategy and data retention plan.
   - Output: primary bottleneck class + supporting evidence.
4. **Design fixes with rollout safety.**
   - Provide 1–3 ranked options with risks, expected impact, and required changes.
   - Include zero/low-downtime rollout guidance (concurrent index builds where supported).
   - Output: recommended change set + verification criteria.
5. **Validate and guard against regressions.**
   - Specify before/after metrics, plan diffs, and any test/benchmark additions.
   - Failure looks like: the before/after comparison shows no improvement in the targeted metric, or the plan diff still shows the scan/lock pattern that motivated the fix — treat either as the change not landing, and use the rollback plan rather than re-measuring.
   - Output: validation checklist + rollback plan.

## Examples

**Example 1: slow query**
- Input: “Our `orders` search endpoint times out at p99. Here’s the query and EXPLAIN.”
- Output: diagnosis of scan/join issue, recommended composite index, and a verification plan.

**Example 2: lock contention**
- Input: “We see elevated lock waits after a bulk backfill.”
- Output: batch update plan, reduced transaction scope, and rollback steps.

## Output contract

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
