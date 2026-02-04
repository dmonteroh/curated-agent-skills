# Rollout and Verification

Use a staged rollout with explicit gates and rollback triggers.

## Rollout sequence

1) Validate in staging or a low-traffic environment.
2) Canary in production (5–10% traffic or a single replica).
3) Expand to full rollout once gates pass.

## Verification gates

- Latency: p95/p99 within agreed thresholds.
- Errors: no increase in error rate or timeouts.
- Replication lag and backup success rates remain stable.
- Cost impact aligns with expected savings range.

## Rollback criteria

- Latency or error gates breached for > N minutes.
- Replication lag exceeds safe threshold.
- Unexpected capacity saturation during peak window.
