---
name: performance
description: End-to-end performance optimization skill combining orchestration (workflow) and deep-dive engineering. Establishes baselines, profiles bottlenecks, proposes fixes with measurable impact, and adds regression guardrails. Includes a safe-by-default perf wrapper script to capture repo signals and write a deterministic report. Use PROACTIVELY for latency/throughput/resource issues, scalability work, or perf gating.
category: observability
---

# performance

One canonical performance skill that merges:
- **Workflow orchestration** (baseline -> profile -> optimize -> validate -> guardrails)
- **Deep-dive performance engineering** (profiling, observability, load testing, caching, query tuning)

## Use this skill when

- Diagnosing performance bottlenecks (backend/frontend/infra).
- Designing load tests, capacity plans, performance budgets, or SLOs.
- Setting up observability for performance and reliability targets.
- Preventing regressions (perf gates, continuous profiling, indexable reports).

## Do not use this skill when

- The task is feature work with no performance goals.
- There is no way to measure (no metrics/traces/profiles and cannot run tests locally).

## Quick start (fast path)

In the target repo (not this skills repo):

```sh
./performance/scripts/perf.sh scan
./performance/scripts/perf.sh report
```

This writes a deterministic report to `docs/_docgen/performance/REPORT.md`.

## Workflow (orchestration)

### Phase 0: Define goals + constraints

Output:
- target journeys/endpoints
- metrics: p50/p95/p99, throughput, error rate, cost, Core Web Vitals
- constraints: budget, deadline, infra limits, rollout strategy

### Phase 1: Baseline

Output:
- current baseline numbers
- how measured (tooling + environment)
- known bottlenecks/hypotheses

### Phase 2: Profile to find real bottlenecks

Collect (as available):
- CPU profiling (flame graphs/hot paths)
- memory profiling (heap, GC pressure/leaks)
- I/O profiling (DB queries, network, filesystem)
- tracing (distributed traces, span timing)
- frontend (Core Web Vitals, bundle size, render costs)

### Phase 3: Optimize by layer (measure after each change)

- Database: indexes, query plans, N+1 elimination, pooling
- Backend: algorithmic fixes, batching, concurrency, caching
- Frontend: bundles, critical path, lazy loading, caching headers
- Infrastructure: autoscaling, resource limits, CDN, network

### Phase 4: Validate + guardrails

- Load tests / perf tests (safe environments only)
- Perf budgets and regression gates in CI (if feasible)
- Observability dashboards + alerts

## Deep-dive reference (engineering)

For detailed tactics (profiling tools, caching strategies, perf testing), follow `resources/implementation-playbook.md`.

## Integration notes

- If perf work becomes structured (multiple phases/tasks), use `tracks-conductor-protocol` to create a track + tasks.
- If the optimization requires a major architectural decision, record it via `adr-madr-system`.

## Resources

- `resources/implementation-playbook.md` (deep reference)
- `resources/optimization-workflow.md` (end-to-end perf workflow)
- `scripts/perf.sh` (scan + report wrapper)
