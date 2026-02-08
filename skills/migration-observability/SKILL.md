---
name: migration-observability
description: "Make database migrations safe and observable. Define progress + safety metrics, dashboards, and runbook gates (go/no-go criteria) for live migrations, backfills, and cutovers. Works standalone and is database/tooling agnostic."
category: observability
---
# migration-observability

Provides guidance for **running migrations safely** (not for authoring SQL/ORM migration steps). It focuses on:
- progress visibility (are we moving? how fast? ETA?)
- safety signals (are we harming prod? are errors rising? is lag growing?)
- runbook gates (objective go/no-go thresholds and rollback triggers)

## Use this skill when

- Running a production migration/backfill/cutover that can’t be “fire and forget”.
- Dashboards/alerts and objective gates (pause, slow down, rollback, proceed) are required.
- A shared, deterministic runbook is required for the migration.

## Do not use this skill when

- The change is a tiny, low-risk schema tweak with trivial rollback.
- Only authoring migration scripts (this skill is about operating them).

## Required inputs

- Migration summary: what changes, why, scope, expected duration, rollback complexity.
- Migration type: schema-only / backfill / online rewrite / cutover / dual-write / reindex.
- Operational constraints: maintenance window, allowed error budget, throttling knobs.
- Available telemetry: metrics, logs, traces, dashboards, alerting system.
- Data correctness expectations: invariants, validation approach, sampling strategy.

## Outputs (artifacts produced)

Minimum artifacts (paths are suggestions; adapt to repo conventions):
- docs/runbooks/migrations/<migration-id>.md (the runbook with gates)
- docs/runbooks/migrations/<migration-id>-dashboard.md (dashboard/queries, tool-agnostic)
- docs/runbooks/migrations/<migration-id>-alerts.md (alert thresholds + paging policy)

Templates:
- `references/runbook-template.md`
- `references/metrics-and-gates.md`

## Workflow (step-by-step with outputs)

1) Classify the migration (controls what must be observed)
- Decide type, blast radius, and rollback complexity.
- Output: short classification summary to include in the runbook.

2) Define progress metrics (prove it is moving)
- Pick counters and derived rates (rows processed, throughput, ETA, lag).
- Decision point: if instrumentation is unavailable, define structured logs and manual sampling cadence.
- Output: a progress metrics list with target values or expected ranges.

3) Define safety metrics (prove it is not hurting prod)
- Select DB, query, app, and correctness signals that exist today.
- Decision point: if a metric is missing, either add lightweight instrumentation or choose a proxy metric.
- Output: a safety metrics list with thresholds and measurement sources.

4) Turn metrics into gates (objective go/no-go)
- Write Proceed (green), Pause/Throttle (yellow), Rollback (red) per phase.
- Decision point: if rollback is impossible, define a “stop and stabilize” gate plus explicit escalation steps.
- Output: a gate table for each phase.

5) Build the runbook, dashboard, and alert specs
- Use the templates to capture phases, checks, and thresholds.
- Output: the three runbook artifacts in your repo structure.

6) Execute with controls and document outcomes
- Start with a canary, ramp cautiously, and validate invariants continuously.
- Decision point: if any gate triggers, follow the runbook’s pause/rollback steps.
- Output: a short closeout section with verification results and follow-ups.

## Common pitfalls

- Missing baselines, so regressions cannot be detected.
- Gates with vague language instead of numeric thresholds.
- No throttle/rollback plan for long-running backfills.
- Correctness checks that rely on assumptions that cannot be measured.
- Alerting that pages the wrong team or has no escalation path.

## Tooling guidance (agnostic)

This skill does not require a specific stack. Common setups:
- Metrics: Prometheus/OpenTelemetry/Cloud metrics
- Dashboards: Grafana / cloud dashboards
- Alerts: Grafana alerting / PagerDuty / OpsGenie / Slack

If none exist, remain “observable” by emitting structured logs + writing a runbook with manual checks and thresholds.

## Examples

Example input:
- Migration type: backfill
- Operational constraints: 2-hour maintenance window, batch size throttle
- Available telemetry: Prometheus metrics + Grafana dashboarding
- Data correctness: checksum sampling every 10k rows

Example output summary (abbreviated):
- Runbook: docs/runbooks/migrations/2024-09-customer-backfill.md
- Dashboard spec: docs/runbooks/migrations/2024-09-customer-backfill-dashboard.md
- Alerts spec: docs/runbooks/migrations/2024-09-customer-backfill-alerts.md
- Gates: proceed/pause/rollback thresholds for canary, ramp, full run

## Output contract (reporting format)

Return a single summary using labeled bullets with the following fields, in this order:

- Migration classification (type, blast radius, rollback complexity).
- Progress metrics with thresholds + sources.
- Safety metrics with thresholds + sources.
- Gate table by phase (proceed/pause/rollback).
- Runbook/dashboard/alerts file paths produced.
- Risks, assumptions, and missing instrumentation.

## References

- `references/README.md`
