---
name: performance
description: End-to-end performance optimization workflow for baselining, profiling bottlenecks, proposing measurable fixes, and adding regression guardrails. Includes a safe-by-default scan/report script to capture repo signals and write a deterministic report. Use for latency/throughput/resource issues, scalability work, or performance gating.
category: observability
---

# performance

Provides a unified performance workflow that combines:
- **Workflow orchestration** (baseline -> profile -> optimize -> validate -> guardrails)
- **Deep-dive performance engineering** (profiling, observability, load testing, caching, query tuning)

## Use this skill when

- Diagnosing performance bottlenecks (backend/frontend/infra).
- Designing load tests, capacity plans, performance budgets, or SLOs.
- Setting up observability for performance and reliability targets.
- Preventing regressions (perf gates, continuous profiling, indexable reports).

## Do not use this skill when

- The task is feature work with no performance goals.
- There is no way to measure and you cannot establish any baseline or plan to measure.

## Activation cues (trigger phrases)

- "slow", "latency", "p95", "p99", "throughput", "RPS", "perf regression"
- "optimize", "profile", "bottleneck", "hot path", "slow query"
- "capacity planning", "load test", "performance budget"

## Required inputs

- Target system scope (service, endpoint, user journey, or UI flow)
- Environment constraints (staging/prod-like, hardware limits, data volume)
- Success metrics (latency percentiles, throughput, error rate, cost)
- Known incidents or regressions (if any)

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

Decision:
- If goals are unclear, request scope + success metrics before proceeding.

### Phase 1: Baseline

Output:
- current baseline numbers
- how measured (tooling + environment)
- known bottlenecks/hypotheses

Decision:
- If no baseline is possible, document missing telemetry and propose a minimal measurement plan.

### Phase 2: Profile to find real bottlenecks

Collect (as available):
- CPU profiling (flame graphs/hot paths)
- memory profiling (heap, GC pressure/leaks)
- I/O profiling (DB queries, network, filesystem)
- tracing (distributed traces, span timing)
- frontend (Core Web Vitals, bundle size, render costs)

Output:
- ranked bottlenecks with evidence (top 3 by impact)
- trace/profile artifacts or pointers

### Phase 3: Optimize by layer (measure after each change)

- Database: indexes, query plans, N+1 elimination, pooling
- Backend: algorithmic fixes, batching, concurrency, caching
- Frontend: bundles, critical path, lazy loading, caching headers
- Infrastructure: autoscaling, resource limits, CDN, network

Output:
- proposed fixes with estimated impact and risk
- measurement plan for each change

### Phase 4: Validate + guardrails

- Load tests / perf tests (safe environments only)
- Perf budgets and regression gates in CI (if feasible)
- Observability dashboards + alerts

Output:
- before/after comparison table
- guardrails and owners

## Common pitfalls

- Optimizing before baselining or profiling
- Changing multiple variables at once and losing causality
- Reporting improvements without describing the environment
- Relying on production-only changes without safe rollout plans

## Tools & scripts

`scripts/perf.sh` is a safe-by-default helper that scans repo signals and emits a deterministic report.

Usage:

```sh
./performance/scripts/perf.sh scan
./performance/scripts/perf.sh report
```

Outputs:
- `docs/_docgen/performance/raw/inventory.md`
- `docs/_docgen/performance/REPORT.md`

Requirements:
- POSIX shell
- `rg` (optional; falls back to `find`)

Verification:
- Confirm the report exists and lists inventory + measurement plan.

Decision:
- If the script is unavailable or not permitted, follow the workflow phases manually and document equivalent outputs.

## Examples

Trigger test prompts:
- "Our checkout p95 jumped to 1.8s last release. Find the bottleneck."
- "Set up a performance budget and guardrails for this API."

Input/output example:

Input: "Profile the slowest endpoint in staging and propose fixes."

Output:
- Baseline numbers (environment + tooling)
- Top bottleneck evidence (profile or trace)
- 2-3 fixes with estimated impact
- Validation plan (how to re-measure)

## Output contract (reporting format)

When this skill runs, respond with:

- Summary (scope + goals)
- Baseline (metrics, environment, tooling)
- Bottlenecks (ranked, evidence-linked)
- Recommendations (fixes, impact, risk)
- Validation plan (tests, measurements, success criteria)
- Guardrails (budgets, alerts, owners)
- Open questions or missing data

## References

See `references/README.md` for detailed tactics, workflows, and source material.

## Resources

- `scripts/perf.sh` (scan + report wrapper)
