---
name: performance
description: "End-to-end performance optimization workflow for baselining, profiling bottlenecks, proposing measurable fixes, and adding regression guardrails. Includes a safe-by-default scan/report script to capture repo signals and write a deterministic report. Use for latency/throughput/resource issues, data freshness, build-loop timing, scalability work, or performance gating."
metadata:
  category: observability
---
# performance

Provides a unified performance workflow that combines:
- **Workflow orchestration** (baseline -> profile -> optimize -> promote -> validate -> guardrails)
- **Deep-dive performance engineering** (profiling, observability, load testing, caching, query tuning)

## Use this skill when

- Diagnosing performance bottlenecks (backend/frontend/infra).
- Designing load tests, capacity plans, performance budgets, or SLOs.
- Setting up observability for performance and reliability targets.
- Preventing regressions (perf gates, continuous profiling, indexable reports).
- Running a bounded search over implementation variants to pick the fastest safe one.
- Latency work where data freshness, cache staleness, or queue backpressure is in play.
- Baselining the developer feedback loop (cold build, incremental rebuild, test suite, type check, lint, image build).

## Do not use this skill when

- The task is feature work with no performance goals.
- There is no way to measure and no feasible baseline plan.
- No correctness gate can be named for the operation being optimized — settle what must stay true before making it faster.
- Stale or wrong data is the whole problem and the cost of serving it is not in question; that is a correctness fix, not an optimization pass.

## Activation cues (trigger phrases)

- "slow", "latency", "p95", "p99", "throughput", "RPS", "perf regression"
- "optimize", "profile", "bottleneck", "hot path", "slow query"
- "capacity planning", "load test", "performance budget"

## Required inputs

- Target system scope (service, endpoint, user journey, or UI flow)
- Environment constraints (staging/prod-like, hardware limits, data volume)
- Success metrics (latency percentiles, throughput, error rate, cost)
- Known incidents or regressions (if any)
- The correctness gate that must stay green while the system is changed
- The search budget for the pass: maximum variants, maximum time, maximum spend, maximum data impact

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
- freshness age wherever a read path is served from a cache, queue, or stream — the age of the value served, tracked as a metric in its own right and not folded into latency
- constraints: budget, deadline, infra limits, rollout strategy
- the correctness gate that must stay green for the whole pass
- the search budget: max variants, max time, max spend, max data impact

Decision:
- If goals are unclear, request scope + success metrics before proceeding.
- If no search budget has been set, set one before optimizing. Its values are chosen per pass against what the win is worth — there is no default variant count or time cap. An unbounded pass ends when attention runs out and reports whatever it measured last. Mechanics: `references/bounded-variant-search.md`.

### Phase 1: Baseline

Baseline the running system and the developer feedback loop. The feedback loop is its own measured surface — cold build, incremental rebuild or hot reload, test-suite duration, type-check time, lint time, container image build — and it degrades the way runtime performance does: monotonically, unnoticed, one dependency at a time. No runtime profiler sees any of it.

Output:
- current baseline numbers
- how measured (tooling + environment)
- feedback-loop timings, where a build or test pipeline exists
- known bottlenecks/hypotheses

Store the baseline as a version-controlled artifact keyed to the commit it was measured at, not a local scratch file. A shared baseline is what lets a before/after comparison run as a per-PR check and mean the same thing to every contributor.

Decision:
- If no baseline is possible, document missing telemetry and propose a minimal measurement plan.

### Phase 2: Profile to find real bottlenecks

Collect (as available):
- CPU profiling (flame graphs/hot paths)
- memory profiling (heap, GC pressure/leaks)
- I/O profiling (DB queries, network, filesystem)
- tracing (distributed traces, span timing)
- frontend (Core Web Vitals, bundle size, render costs)
- freshness (age of the value served on cache-, queue-, or stream-backed reads, measured beside the latency to serve it)

Output:
- ranked bottlenecks with evidence (top 3 by impact)
- trace/profile artifacts or pointers

Decision:
- If no distributed tracing exists, write the hot path out by hand as a segment chain from triggering event to user-visible state, then measure each segment separately. A hand-written chain is a weaker artifact than a trace but it still localizes the cost.

### Phase 3: Optimize by layer (measure after each change)

- Database: indexes, query plans, N+1 elimination, pooling
- Backend: algorithmic fixes, batching, concurrency, caching, backpressure applied at the ingress before a queue grows unbounded rather than scaling the consumer after it has
- Frontend: bundles, critical path, lazy loading, caching headers
- Infrastructure: autoscaling, resource limits, CDN, network, hot/cold path splitting so the latency-critical path carries only what it needs

Run the changes as a bounded search over variants, not as a sequence of edits:

- One hypothesis per variant, against the same input shape as the baseline, so every delta is attributable to a named idea.
- Record every run in a ledger — variant, hypothesis, exact command, measurement, correctness verdict, note — including the rejected ones.
- Compare each variant against the best *accepted* variant, never against the previous run. Run-to-run comparison lets a search walk downhill across several rounds without noticing.
- Stop when the improvement is within run-to-run noise, when correctness fails, when the declared budget is spent, or when the search is changing more variables than it can explain. That last condition stops a search that has become unattributable, not merely one that has become unprofitable.

Output:
- proposed fixes with estimated impact and risk
- measurement plan for each change
- the variant ledger, and the stopping condition that ended the search

### Phase 4: Promote the winner through a gate

A variant becomes the new default only when all of these hold:

- correctness tests pass on the variant as it will ship
- the delta is repeated across runs, or explained by a mechanism someone can state
- rollback is obvious: a flag, a revert, or a documented config change
- the change is encoded durably — source control, a script, a test, or a runbook — not only in the session that found it
- the summary carries the exact commands and measurements
- no metric outside the optimized one regressed unnoticed; check freshness age, error rate, and saturation first

Then re-run baseline and winner together in the same environment to confirm the delta survives.

Decision:
- If the win came from serving older data — a higher hit rate on staler values, a longer TTL, a batch window that delays the stream — that is a correctness cost converted into a latency win, and a dashboard measuring latency alone will report it as a success. Reject it, or re-declare the freshness loss as an accepted trade with a named owner and a freshness budget.

### Phase 5: Validate + guardrails

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
- Starting a variant search with no declared budget, so it ends on attention rather than on evidence
- Comparing each variant against the previous run instead of against the best accepted one
- Hiding stale data behind fast cache hits, then reporting the latency win on its own
- Calling a bounded search's winner "optimal" — it is the best measured safe variant
- Tuning runtime while the build, test, and lint loop degrades unmeasured

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

Input/output example:

Input: "Profile the slowest endpoint in staging and propose fixes."

Output:
- Baseline numbers (environment + tooling)
- Top bottleneck evidence (profile or trace)
- 2-3 fixes with estimated impact
- Validation plan (how to re-measure)

Variant search, wrong vs. right:

Wrong — one variant batches writes *and* raises worker count, comes back faster, and is promoted. The delta cannot be assigned to either change, so nobody learns that batching carried the whole win while the extra workers were costing error rate.

Right — `batch-500` is measured alone against the baseline and accepted; `parallel-8` is then layered on the accepted variant and measured against *it*, not against the last run. Both rows land in the ledger with their exact commands, and `parallel-8` is rejected on the error-rate check with the reason recorded.

Cache win, wrong vs. right:

Wrong — "p95 dropped sharply after raising the cache TTL." Latency improved; the report never mentions that the value served is now older.

Right — the same change reported with freshness age beside latency, so the trade is visible and someone owns the decision to accept it.

## Output contract (reporting format)

When this skill runs, respond with:

- Summary (scope + goals)
- Baseline (metrics, environment, tooling)
- Bottlenecks (ranked, evidence-linked)
- Recommendations (fixes, impact, risk)
- Variant ledger (hypothesis, exact command, measurement, correctness verdict), the budget spent, and the stopping condition that fired
- Promotion decision (what became the default, what was rejected, the rollback path)
- Validation plan (tests, measurements, success criteria)
- Guardrails (budgets, alerts, owners)
- Open questions or missing data

Phrase the result as the best measured safe variant, never as optimal, unless the search space was actually exhausted.

## References

See `references/README.md` for detailed tactics, workflows, and source material.

## Resources

- `scripts/perf.sh` (scan + report wrapper)
