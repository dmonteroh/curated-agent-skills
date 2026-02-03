# Observability Strategy (Condensed)

## Core Signals

- Metrics: latency, throughput, errors, saturation.
- Logs: structured, correlated, searchable.
- Traces: end-to-end spans with context propagation.

## Instrumentation Order

1. Critical user journeys.
2. Core APIs and background jobs.
3. Dependencies (DB, cache, external APIs).

## SLI/SLO Basics

- Define SLIs per journey (latency p95, error rate).
- Set SLO targets and track error budgets.

## Alerting

- Alert on symptoms, not internal metrics alone.
- Use multi-window burn rate for SLO alerts.

## Tooling Notes

- OpenTelemetry for vendor-neutral traces/metrics.
- Grafana + Prometheus for dashboards.
