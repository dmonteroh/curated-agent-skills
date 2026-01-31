---
name: grafana-dashboards
description: Create and manage production Grafana dashboards for real-time visualization of system and application metrics. Use when building monitoring dashboards, visualizing metrics, or creating operational observability interfaces.
---

# Grafana Dashboards

Grafana dashboard authoring with a deterministic layout, query hygiene, and operational usefulness.

## Use this skill when

- You need to create or improve Grafana dashboards
- You need to standardize dashboard layout for on-call usability
- You need dashboard JSON templates/snippets to start from

## Do not use this skill when

- You need end-to-end observability architecture (logs/metrics/traces/alert strategy) — use a broader monitoring/observability skill
- The task is unrelated to Grafana dashboards

## Workflow (Deterministic)

1. Define audience + purpose (on-call overview vs deep dive vs business KPI).
2. Choose a canonical layout:
   - Top row: symptom signals (error rate, latency p95/p99, traffic, saturation).
   - Next: breakdowns (by route/service/tenant/dependency).
   - Last: diagnostics (resource saturation, logs/traces drilldowns).
3. Make every panel answer one question; set units/thresholds/time range.
4. Keep queries safe (bounded labels, avoid high-cardinality explosions).
5. Add drilldowns (links to logs/traces/detailed dashboards) when possible.

## Quality Gates

- The top row answers: "is it broken?"
- An on-call person can find a likely cause within 2-3 clicks.
- Queries are performant (recording rules for expensive aggregations).
- Panels are stable (avoid tiny denominators; avoid misleading averages).

## Assets (Copy/Adapt)

- Dashboard stubs:
  - `assets/dashboard-templates.json`
  - `assets/api-dashboard.json`
  - `assets/infrastructure-dashboard.json`
  - `assets/database-dashboard.json`
- Panel + templating snippets:
  - `assets/panel-examples.json`
- Alert rule patterns (structure only):
  - `assets/alert-templates.json`

## References (Optional)

- Deep-dive playbook: `resources/implementation-playbook.md`
- Design guide: `references/dashboard-design.md`
