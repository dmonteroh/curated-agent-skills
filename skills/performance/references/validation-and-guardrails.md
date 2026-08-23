# Validation and Guardrails

Use this reference to verify improvements and prevent regressions.

## Validation checklist

- Re-run the baseline measurement in the same environment, in the same session as the winner. A delta assembled from two sessions carries whatever else changed between them.
- Compare before/after metrics with a simple table.
- Confirm no increase in error rate or resource saturation.
- Confirm the freshness age of served values did not increase. A latency win bought with staler data is a regression that a latency-only comparison will score as a success.
- Read the change back on a deployed surface where one exists: response timing and headers, upstream freshness timestamp, queue or job state, cache and edge state, and the retry or degraded-mode log lines. Client-side labels are not measurement.
- Confirm the promotion gate in `references/bounded-variant-search.md` passed before a variant was made the default.

## Load and stress testing

- Use realistic traffic profiles (peak, steady, spike).
- Start in a safe environment that mirrors production.
- Capture latency percentiles, throughput, and saturation.

Decision:
- If a safe environment is not available, document the limitation and propose a lower-risk proxy test.

## Guardrails

- Performance budgets for key endpoints or user journeys.
- Freshness budgets on cache-, queue-, or stream-backed read paths: a maximum age for a served value, alerted on like any other budget. Choose the value per path from what the consumer can tolerate; there is no portable default.
- An accuracy guardrail on any path whose result is approximate — an approximate index, a sample, a lossy or quantized representation: the accuracy metric re-measured against the exact reference on a schedule, not only during the pass that tuned it. Accuracy drifts with the data rather than with the code, so no deploy, test run, or error rate marks the day it fell.
- Regression gates in CI where feasible.
- Dashboards and alerts for SLIs/SLOs.
- Runbooks for diagnosing regressions.
- Baselines stored as version-controlled artifacts keyed to the commit they were measured at, rather than local scratch files, so before/after comparison is shared across contributors and can run as a per-PR check.
- Guardrails on the developer feedback loop too — build, rebuild, test, type check, lint, image build — since nothing else in the pipeline notices when they get slower.

## Rollout considerations

- Staged rollout with monitoring at each step.
- Explicit rollback criteria tied to metrics.

## Outputs

- Before/after comparison table with metrics and environment.
- Guardrail list with owners and alert thresholds.
