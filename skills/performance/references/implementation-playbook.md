# Performance Implementation Playbook

This playbook intentionally stays lean. Use it as a navigation aid, not a textbook.

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
- `docs/performance/budgets.md` (enforced budgets)
- `docs/performance/runbooks.md` (how to diagnose regressions)
