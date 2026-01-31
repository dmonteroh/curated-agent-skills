# Operability First (SRE-Style)

Use this reference when you need to turn “it should work in production” into explicit, testable design outputs.

## Outputs to produce (minimum)

- SLIs/SLOs (and what happens when you’re out of budget)
- Dashboards (golden signals) + alert policy (page vs ticket)
- Rollout/rollback plan (and what metrics gate each phase)
- Failure modes: dependency failures, overload, partial outage

## Monitoring: golden signals

Track the four golden signals at the system boundary:
- **Latency** (p50/p95/p99; separate success vs error where useful)
- **Traffic** (RPS/QPS, active jobs, bytes/sec)
- **Errors** (rate; error budget burn; by class/cause)
- **Saturation** (utilization and queued work; not just CPU)

## SLIs/SLOs and error budgets

- Define SLIs from user-visible behavior (requests, jobs, critical flows).
- Define SLOs as targets over a window (e.g., 28d).
- Use error budgets to make trade-offs explicit:
  - if burn rate is high -> freeze risky releases / reduce scope / add capacity

## Alerting (reduce noise)

- Page only on issues that require urgent human response.
- Prefer multi-window burn-rate alerting (fast + slow signal) when you can.
- Alerts should be:
  - actionable,
  - attributable (what broke),
  - and tied to a runbook.

## Telemetry hygiene (multi-agent + long-lived systems)

- Avoid high-cardinality labels (user IDs, request IDs, raw URLs).
- Enforce stable names and units for metrics.
- Logs:
  - structured, with consistent keys
  - include correlation IDs / trace IDs
  - avoid logging secrets/PII
- Traces:
  - propagate context across services
  - name spans consistently; capture retries/timeouts

## Dependency safety checklist

- Timeouts everywhere (with sane defaults)
- Retries with backoff + jitter (only when safe)
- Circuit breaking / bulkheads for expensive dependencies
- Idempotency on mutating operations (if clients may retry)
- Backpressure (queue limits, load shedding)

## Source references (authoritative)

```text
Google SRE Book (Monitoring Distributed Systems):
  https://sre.google/sre-book/monitoring-distributed-systems/

OpenTelemetry Semantic Conventions:
  https://opentelemetry.io/docs/specs/semconv/
```

