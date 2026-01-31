# Migration Runbook Template (Copy/Paste)

```md
# Migration Runbook: <migration-id> — <short title>

Owner(s): <name/team>
Date: YYYY-MM-DD

## Summary

- What changes:
- Why now:
- Expected duration:
- Blast radius:
- Rollback complexity: low / medium / high

## Preconditions / Readiness

- Backups/snapshots verified:
- Rollback plan is written and tested (if feasible):
- Observability is in place (dashboards + alerts):
- Throttling knobs exist (batch size, sleep, concurrency):

## Phases

### Phase 0 — Baseline
- Capture pre-migration baselines (app p95/p99, DB key metrics).
- Confirm dashboards are live and alert routing works.

### Phase 1 — Canary
- Scope: <small subset>
- Start command/procedure:
- Validation checks:

Gate (go/no-go):
- Proceed if: <green criteria>
- Pause/throttle if: <yellow criteria>
- Rollback if: <red criteria>

### Phase 2 — Ramp
- Scope: <larger subset>
- Ramp schedule:
- Validation checks:

Gate:
- Proceed if:
- Pause/throttle if:
- Rollback if:

### Phase 3 — Full Run
- Scope: <full set>
- Execution details:
- Validation checks:

Gate:
- Proceed if:
- Pause/throttle if:
- Rollback if:

### Phase 4 — Cutover (if applicable)
- Steps:
- Verification:

Gate:
- Proceed if:
- Rollback if:

## Data Correctness Checks

- Invariants:
- Sampling approach:
- Systematic checks:

## Rollback Plan

- Trigger conditions:
- Steps:
- Data recovery steps (if needed):

## Communications

- Status update cadence:
- Channels:
- Stakeholders:

## Closeout

- Post-migration verification complete:
- Performance baseline re-captured:
- Residual risks:
- Follow-ups / hardening tasks:
```

