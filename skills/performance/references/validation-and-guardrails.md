# Validation and Guardrails

Use this reference to verify improvements and prevent regressions.

## Validation checklist

- Re-run the baseline measurement in the same environment.
- Compare before/after metrics with a simple table.
- Confirm no increase in error rate or resource saturation.

## Load and stress testing

- Use realistic traffic profiles (peak, steady, spike).
- Start in a safe environment that mirrors production.
- Capture latency percentiles, throughput, and saturation.

Decision:
- If a safe environment is not available, document the limitation and propose a lower-risk proxy test.

## Guardrails

- Performance budgets for key endpoints or user journeys.
- Regression gates in CI where feasible.
- Dashboards and alerts for SLIs/SLOs.
- Runbooks for diagnosing regressions.

## Rollout considerations

- Staged rollout with monitoring at each step.
- Explicit rollback criteria tied to metrics.

## Outputs

- Before/after comparison table with metrics and environment.
- Guardrail list with owners and alert thresholds.
