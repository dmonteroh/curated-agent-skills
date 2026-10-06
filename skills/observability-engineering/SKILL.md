---
name: observability-engineering
description: "Designs what a service emits and what pages a human: structured logs, metrics, traces, dashboards and alerts, then proves each signal and alert route works. Use for instrumenting a service, fixing noisy or unowned alerts, or catching regressions after a deploy."
metadata:
  category: observability
---
# Observability Engineering

Provides a process for deciding which failures a service must reveal, which signals reveal them, and who is paged, then checking that the signals and the paging path work before rollout.

## Use this skill when

- A service has no telemetry, or telemetry nobody can follow from one request across logs, metrics and traces.
- Alerts are noisy, ownerless, or fire on internal causes rather than user-visible symptoms.
- An outage was found by a customer, or by an expiry nobody was watching, instead of by monitoring.
- A release must be judged against how the service behaved just before it, not only against fixed thresholds.

## Do not use this skill when

- The request is a single vendor UI walkthrough with no design decisions.
- The task is a post-deploy smoke or synthetic check of one URL.
- The work is load testing, capacity forecasting or profiling a slow code path.
- The user is building a product feature that shows analytics to their own customers.
- A one-off local bug needs a `console.log` or a debugger, not standing telemetry.

## Required inputs

- Services, runtime and deployment model.
- Existing telemetry stack and any mandated vendor.
- Critical user journeys and their latency and error targets.
- Data handling limits: PII, secrets, retention.

## Workflow

1. **Name the failures first.** List the three to five user-visible failures to detect (journey plus symptom, for example "checkout returns 5xx" or "search p95 over 500 ms"). Drop any proposed signal that no listed failure needs.
   - Output: failure list with the signal that detects each.
2. **Instrument for correlation.** Emit JSON logs, metrics and traces that share one request or trace ID.
   - Redact passwords, tokens and PII at the emit point, not in the pipeline.
   - Metric labels take only bounded values. Never put a user ID, raw URL path or error message in a label; use the route template. Multiply the label cardinalities per metric and reject any estimate above the backend's series budget.
   - Propagate trace context across every hop, queues and background jobs included. A trace that ends at a queue is a broken trace.
   - Where traces and metrics both exist, attach trace-ID exemplars to latency histograms, and keep error and slow-path sampling high enough that an exemplar resolves to a stored trace.
   - Output: instrumentation backlog with owners and acceptance criteria.
3. **Fit the stack.** Choose collection, storage and retention within the existing or mandated stack. Without tracing, ship logs and metrics with correlation IDs.
4. **Build dashboards for decisions.** One RED view per service and one USE view per resource, each named for its audience and the decision it supports. The top row shows the signals the pages key on.
5. **Write alerts that page on symptoms.**
   - Page on user-visible symptoms and burn rate over multiple windows; causes (CPU, queue depth) open tickets or appear on dashboards.
   - Every alert carries an owner and a runbook link. Do not ship one without both.
   - For release validation, capture a pre-deploy baseline and alert on the delta from it beside the absolute threshold.
   - Add expiry alerts, with lead time to finish rotation, for certificates, signing keys and fixed-lifetime credentials.
   - Output: alert policy and routing matrix.
6. **Verify before rollout.** A check that cannot fail does not count.
   - Send one test request. Its log line, metric observation and trace must all show the same trace ID. Any missing one fails.
   - Seed a fake secret in a request and grep emitted logs for it. A hit fails.
   - Trigger every alert (lower its threshold or inject the failure) and confirm it reaches the declared owner. An alert that does not page blocks rollout.
   - Query series count per new metric against the estimate from step 2.
   - Output: verification checklist with each result.

## Examples

Input: "Add observability to our Node.js API and make the latency alerts useful."

Weak: alert `cpu > 80%` to the whole team channel, logs as free-text `console.log`, metric `http_requests{url="/users/8812"}`.

Better:
- Failures: checkout 5xx, search p95 over 400 ms.
- Instrumentation: JSON logs carrying `trace_id`; `http.server.duration` histogram labelled by route template and status class, with trace-ID exemplars; traces on `/checkout` across the payment queue.
- Alerts: 5 m and 1 h burn-rate page on checkout errors, owner `payments-oncall`, runbook linked; p99 delta against the pre-deploy baseline after each release; CPU shown on the USE dashboard only.
- Verification: one test request produced matching log, exemplar and trace IDs; seeded `Bearer` token absent from logs; the burn-rate alert paged `payments-oncall` after an injected 500.

## Output contract

- **Failures to detect**: the list from step 1.
- **Instrumentation plan**: signals, labels, owners, sampling.
- **Dashboards and alerts**: panels, thresholds or burn rates, owner and runbook per alert.
- **Verification**: each check from step 6 and its result.
- **Assumptions and risks**: inferred context and open decisions.

## Resources

| Topic | Reference | Load when |
|-------|-----------|-----------|
| Strategy | `references/observability-strategy.md` | Planning signal order and SLI basics |
| Logging | `references/structured-logging.md` | Pino or structlog setup, log levels |
| Metrics | `references/prometheus-metrics.md` | Metric types, labels, exemplars |
| Tracing | `references/opentelemetry.md` | Spans, context propagation, SDK setup |
| Alerting | `references/alerting-rules.md` | Prometheus rules, baseline regressions, expiry |
| Dashboards | `references/dashboards.md` | RED and USE panels, service topology |

See `references/README.md` for the index.
