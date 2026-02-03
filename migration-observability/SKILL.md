---
name: migration-observability
description: Make database migrations safe and observable. Define progress + safety metrics, dashboards, and runbook gates (go/no-go criteria) for live migrations, backfills, and cutovers. Works standalone and is database/tooling agnostic.
category: observability
---

# migration-observability

This skill is for **running migrations safely** (not for writing migration SQL/ORM steps). It focuses on:
- progress visibility (are we moving? how fast? ETA?)
- safety signals (are we harming prod? are errors rising? is lag growing?)
- runbook gates (objective go/no-go thresholds and rollback triggers)

## Use this skill when

- Running a production migration/backfill/cutover that can’t be “fire and forget”.
- You need dashboards/alerts and objective gates (pause, slow down, rollback, proceed).
- Multiple agents/people need a shared, deterministic runbook for the migration.

## Do not use this skill when

- The change is a tiny, low-risk schema tweak with trivial rollback.
- You’re only authoring migration scripts (this skill is about operating them).

## Outputs (what you should produce)

Minimum artifacts (paths are suggestions; adapt to repo conventions):
- docs/runbooks/migrations/<migration-id>.md (the runbook with gates)
- docs/runbooks/migrations/<migration-id>-dashboard.md (dashboard/queries, tool-agnostic)
- docs/runbooks/migrations/<migration-id>-alerts.md (alert thresholds + paging policy)

Templates:
- `references/runbook-template.md`
- `references/metrics-and-gates.md`

## Workflow (fast, bulletproof)

1) Classify the migration (controls what you must observe)
- Type: schema-only / backfill / online rewrite / cutover / dual-write / reindex
- Blast radius: tables touched, write path impact, worst-case rollback complexity
- Duration: seconds / minutes / hours / days

2) Define progress metrics (prove it is moving)
- rows processed / total rows (or batches complete)
- throughput (rows/sec, batches/min)
- ETA (derived)
- lag vs source (if there is replication/dual-write)

3) Define safety metrics (prove it is not hurting prod)
Pick the ones that match your system:
- DB health: CPU, memory, I/O, disk space, connection pool saturation
- Query health: p95/p99 latency for top queries, lock waits, deadlocks
- App health: request error rate, p95/p99 latency, timeouts
- Data correctness: mismatch rate, invariant violations, checksum diffs (sampled)

4) Turn metrics into gates (objective go/no-go)
For each phase, write:
- **Proceed** criteria (green)
- **Pause/Throttle** criteria (yellow)
- **Rollback** criteria (red)

5) Run the migration with controlled execution
- Start with a canary (small cohort/table slice).
- Use bounded batches and explicit throttling knobs.
- Verify invariants continuously (spot checks + automated checks if possible).

6) Post-migration verification and closeout
- Data correctness checks (spot + systematic where feasible)
- Performance regression check (baseline vs after)
- Document lessons learned and permanent guardrails

## Tooling guidance (agnostic)

This skill does not require a specific stack. Common setups:
- Metrics: Prometheus/OpenTelemetry/Cloud metrics
- Dashboards: Grafana / cloud dashboards
- Alerts: Grafana alerting / PagerDuty / OpsGenie / Slack

If none exist, you can still be “observable” by emitting structured logs + writing a runbook with manual checks and thresholds.
