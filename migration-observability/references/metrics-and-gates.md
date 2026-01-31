# Metrics and Gates (Progress + Safety)

Use this as a checklist to build objective go/no-go criteria. Pick metrics that are available; don’t invent precision you can’t measure.

## Progress metrics (is it moving?)

- Rows/batches processed (counter)
- Total rows/batches remaining (gauge/derived)
- Throughput (rate)
- ETA (derived)
- Queue depth (if work is queued)
- Replication / dual-write lag (seconds)

## Safety metrics (is prod safe?)

Database health (examples; choose what your DB exposes):
- CPU %, memory %, disk %, IOPS, read/write latency
- Connection pool usage / saturation
- Lock waits / blocked sessions
- Deadlocks (count)
- Replication health (if any)

Query health:
- p95/p99 latency for critical queries
- slow query count (rate)
- errors/timeouts on DB calls

Application health:
- request error rate (5xx, retries)
- request p95/p99 latency
- worker queue latency (if relevant)

Correctness signals:
- invariant violations (count)
- mismatch rate (source vs target; sampled or systematic)
- checksum/digest diffs (if feasible)

## Gate patterns

Write gates per phase. Keep them numeric and unambiguous.

### Proceed (green)
- Throughput above minimum floor for N minutes
- Error rate below threshold
- p99 latency within acceptable delta vs baseline
- Lag below threshold

### Pause / Throttle (yellow)
- Throughput drops below floor for N minutes
- DB load exceeds “soft cap”
- p99 latency exceeds baseline by X% for Y minutes
- lock waits spike above threshold

### Rollback (red)
- sustained elevated error rates
- correctness/invariant violations above threshold
- unsafe DB conditions (disk near full, deadlocks sustained, severe timeouts)
- SLA/SLO breach risk

## Example: Gate table skeleton

```text
Phase | Proceed if | Pause/Throttle if | Rollback if
----- | ---------- | ----------------- | ----------
Canary | ... | ... | ...
Ramp   | ... | ... | ...
Full   | ... | ... | ...
Cutover| ... | ... | ...
```

