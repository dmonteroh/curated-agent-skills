# Performance Optimization Workflow (Condensed)

Use this as an end-to-end performance runbook.

## Phase 1: Baseline

- Profile CPU, memory, I/O, and DB queries.
- Capture p50/p95/p99, throughput, and error rate.
- Identify top bottlenecks with evidence.

## Phase 2: Optimize by Layer

- Database: indexes, query plans, pooling, caching.
- Backend: batching, concurrency, algorithm fixes.
- Frontend: bundle size, critical path, lazy loading.
- Infra: autoscaling, CDN, compression.

## Phase 3: Validate

- Run load tests with realistic traffic.
- Compare against baseline.
- Define performance budgets and regression gates.

## Phase 4: Monitor

- Add tracing + metrics for critical paths.
- Define SLIs/SLOs and alerting thresholds.
- Keep a backlog of perf debt.
