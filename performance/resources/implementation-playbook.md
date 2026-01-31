# Performance Implementation Playbook

This playbook intentionally stays lean. Use it as a navigation aid, not a textbook.

## Minimal baseline checklist

- Define target journeys/endpoints and success metrics (p95/p99, throughput, error rate, cost).
- Establish a baseline in a controlled environment.
- Capture a profile/trace for the baseline.
- Optimize one bottleneck at a time; measure after each change.
- Add guardrails (budgets, dashboards, alerts) to prevent regressions.

## Common bottleneck buckets

- Database: missing indexes, bad query shapes, N+1, pooling limits.
- Backend: expensive loops, serialization, contention, synchronous I/O.
- Frontend: bundles, render blocking, images, CLS/INP regressions.
- Infra: over/under-provisioning, cold starts, network hops, noisy neighbors.

## Tooling pointers (choose what's already installed)

- Profiling:
  - CPU: flame graphs / sampling profilers
  - Memory: heap snapshots, allocation profiling, GC pressure
  - I/O: slow query logs, tracing spans, network timing
- Load testing:
  - k6 / Gatling / Locust / Artillery (pick one)
- Observability:
  - OpenTelemetry + an APM backend (Datadog/New Relic/etc.)

## Output artifacts (recommended)

- `docs/_docgen/performance/REPORT.md` (generated summary)
- `docs/performance/budgets.md` (what we enforce)
- `docs/performance/runbooks.md` (how to diagnose regressions)
