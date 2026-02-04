# Performance Regression Testing (Condensed)

## When to Use

- You have latency/throughput SLAs.
- You want CI gates for performance.

## Approach

- Define budgets (p95 latency, LCP, throughput).
- Build a small, deterministic perf test suite.
- Run in CI on a stable environment.
- Fail the build on regressions.

## Tooling

- API: k6, Artillery, Gatling.
- Frontend: Lighthouse CI.
- DB: targeted benchmarks with representative queries.

## CI Gate Example

- Smoke perf tests on every PR.
- Full perf tests nightly or on release branches.
