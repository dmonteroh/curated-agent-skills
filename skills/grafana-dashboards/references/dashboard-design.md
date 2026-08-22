# Dashboard Design Guide

This guide is focused on making dashboards operationally useful and safe (no noisy panels, no misleading charts, no backend-killing queries).

## Principles

- Optimize for decisions, not for beauty.
- Default to symptom-based monitoring; drill down to causes.
- Prefer consistency across dashboards: same layout, same time ranges, same naming.

## Naming Conventions

- Dashboard title: `<domain> / <system> / <purpose>`
  - Example: `Auth / Verifier / On-call Overview`
- Panel titles should be questions:
  - `Is latency increasing?`
  - `Which routes are failing?`

## Time Ranges

- Default: last 1 hour.
- Common presets: 15m, 1h, 6h, 24h, 7d.
- Avoid dashboards that only make sense at one time range.

## Standard Layout

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

## Aggregation Pitfalls

- Percentiles are not aggregatable across dimensions unless computed properly.

See `SKILL.md` Common pitfalls for other pitfalls to avoid.

## Drilldowns

Every overview dashboard should link to:

- Logs (Loki) filtered to the same service/route.
- Traces (Tempo/Jaeger) with exemplars.
- A detailed dashboard for infra dependencies (DB/Redis/Kafka).

## Good Defaults

- Units: always set units (ms, req/s, %).
- Thresholds: set meaningful thresholds, not arbitrary colors.
- Legends: keep short; include only the labels needed to interpret.

## Review Checklist

See `SKILL.md` Quality Gates for the checklist used to review a dashboard before shipping it.
