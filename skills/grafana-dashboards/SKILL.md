---
name: grafana-dashboards
description: "Provides guidance to create and manage production Grafana dashboards for real-time visualization of system and application metrics. Use when building monitoring dashboards, visualizing metrics, or creating operational observability interfaces."
metadata:
  category: observability
---
# Grafana Dashboards

## Use this skill when

- A request asks to create or improve Grafana dashboards
- A request asks to standardize dashboard layout for on-call usability
- A request asks for dashboard JSON templates or snippets
- A request asks for a dashboard covering a specific infrastructure system (message broker, search cluster, database)

## Do not use this skill when

- The request is for end-to-end observability architecture beyond dashboards

## Required inputs

- Target service/domain and dashboard purpose
- Audience (on-call, developer deep dive, leadership KPI)
- Data sources available (Prometheus/Mimir, Loki, Tempo/Jaeger, etc.)
- SLOs or KPIs (if available)
- Existing dashboard JSON or screenshots (if refactoring)
- Constraints (time range defaults, label cardinality limits, naming standards)

## Workflow

1. Confirm scope and data sources.
   - Output: a 2-4 sentence scope summary + list of data sources.
   - Decision: if any required data source is unknown/unavailable, ask for it before continuing.
2. Select a layout template based on audience.
   - Output: row-by-row layout sketch with row intent.
   - Decision: if KPI-focused, add a KPI row before symptom signals.
3. Specify panels for each row.
   - Output: panel list with question, viz type, unit, threshold, and query stub.
   - Decision: if the target is a named infrastructure system (message broker, search cluster, database), seed the system-specific row from `references/operator-panel-sets.md` instead of the generic templates, which carry no system-specific signal.
   - Decision: if a panel depends on a missing metric, propose a fallback panel or mark it as "needs metric".
4. Draft queries and variables safely.
   - Output: query list + variable list with label constraints.
   - Decision: if a query risks high cardinality, recommend a recording rule or pre-aggregation.
5. Add drilldowns and links.
   - Output: link map to logs/traces/detail dashboards.
6. Produce dashboard JSON or snippets.
   - Output: Grafana JSON sections or template references.
7. Run quality gates and note fixes.
   - Output: pass/fail checklist with remediation steps.

## Quality Gates

- Symptom-first check: the top row alone answers "is it broken?" Failure: an operator has to scan more than one row to tell whether the service is healthy.
- Click-depth check: a likely cause is reachable within 2-3 clicks of the top row. Failure: finding the cause requires opening a query editor or an external tool first.
- Query-cost check: every expensive aggregation runs behind a recording rule. Failure: a panel aggregates raw high-cardinality series live on every dashboard load.
- Denominator/average check: rate and latency panels guard against tiny denominators and expose percentiles alongside averages. Failure: a panel spikes to 100% during low traffic, or its average line stays flat while p99 has already breached SLO.

## Common pitfalls

- Using unbounded labels (wildcards or regex on high-cardinality labels).
- Relying on averages for latency or error rates without percentiles.
- Mixing multiple questions into a single panel.
- Omitting units or thresholds, which hides intent.
- Building dashboards that only work at one specific time range.

## Resources

- Dashboard stubs:
  - `assets/dashboard-templates.json`
  - `assets/api-dashboard.json`
  - `assets/infrastructure-dashboard.json`
  - `assets/database-dashboard.json`
- Panel + templating snippets:
  - `assets/panel-examples.json`
- Alert rule patterns (structure only):
  - `assets/alert-templates.json`

## Examples

**Input:** "Create an on-call Grafana dashboard for the payments API using Prometheus and Loki. Focus on latency, errors, and top routes."

**Output (abridged):**

1. Summary: On-call overview for payments API with symptom-first layout.
2. Inputs & Assumptions: Prometheus + Loki available; SLO not provided.
3. Layout Sketch: Row 1 symptoms; Row 2 top routes; Row 3 infra saturation + logs.
4. Panel Specs: Error rate (timeseries, %, threshold 1%); p95 latency (ms); RPS.
5. Queries & Variables: `service="payments"`, `route` variable (top 20).
6. Drilldowns & Links: Loki logs filtered by `service` + `route`.
7. JSON Snippets: `assets/dashboard-templates.json` skeleton + panel JSON blocks.
8. Quality Gates: Pass; add recording rule for p99 latency if needed.

## References

- Index: `references/README.md`
- Design guide: `references/dashboard-design.md`
- Per-system panel sets: `references/operator-panel-sets.md`
