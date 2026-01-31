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

## Aggregation Pitfalls

- Averages hide tail latency; show p95/p99.
- Percentiles are not aggregatable across dimensions unless computed properly.
- Always label what you're aggregating by (service, route, instance, tenant).

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

- Does the top row tell you if you should page someone?
- Can an on-call person find the likely cause within 2-3 clicks?
- Are panels stable (no constant flapping due to tiny denominators)?
- Are queries bounded and performant?
