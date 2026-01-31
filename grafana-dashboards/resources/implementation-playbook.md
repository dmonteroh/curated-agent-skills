# Grafana Dashboards - Implementation Playbook

Use this playbook when you need a production-ready dashboard pack, review an existing dashboard, or standardize dashboards across teams.

## Inputs

- Audience: on-call responder, developer, leadership, customer support.
- Data sources: Prometheus/Mimir, Loki, Tempo/Jaeger, Elasticsearch, Cloud provider.
- SLOs: target availability/latency, error budgets.
- Runbooks: links/IDs for incident response.

## Deliverables

- A dashboard (or dashboard set) with a clear hierarchy.
- Alert rules (where Grafana-managed or external).
- A short operator guide: what to look at first, what actions to take.

## Dashboard Quality Gates

- Top row: symptom signals (availability, error rate, latency, saturation).
- Each panel:
  - Has a single question it answers.
  - Has units, thresholds, and sane time ranges.
  - Has drilldowns (links to logs/traces or detailed dashboards).
- Avoid misleading aggregations (especially percentiles and averages).
- Avoid high-cardinality queries that will melt your metrics backend.

## Standard Layout (Recommended)

1) "Is it broken?"
- Availability (SLO burn, error rate)
- Latency (p95/p99)
- Traffic (RPS)

2) "Where is it broken?"
- By route/operation
- By status code / error type
- By dependency (DB, cache, external service)

3) "Why is it broken?"
- Saturation: CPU/mem, queue depth, DB connections
- Error logs (Loki) and trace exemplars (Tempo)

## Panel Patterns

- Big number: current error rate / current p95 latency.
- Time series: rates and percentiles over time.
- Heatmap: latency distribution.
- Table: top-N routes/errors.

## Query Notes (Prometheus)

- Prefer `rate()`/`increase()` over raw counters.
- Use recording rules for expensive aggregations.
- Use label filters intentionally; avoid `.*` and unbounded cardinality.

## Assets

Optional templates live in `grafana-dashboards/assets/`.

- `assets/dashboard-templates.json` - minimal dashboard JSON stubs you can copy/adapt
- `assets/alert-templates.json` - example alert rule patterns (structure only)

## Deep-Dive Reference

See `references/dashboard-design.md`.
