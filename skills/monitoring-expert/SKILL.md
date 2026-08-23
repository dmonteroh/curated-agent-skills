---
name: monitoring-expert
description: "Provides end-to-end observability across logs, metrics, traces, alerting, and performance testing. Use when instrumenting services, setting alert strategy, or designing an observability stack."
metadata:
  category: observability
---
# Monitoring Expert

## Use this skill when

- Setting up application monitoring
- Implementing structured logging
- Creating metrics and dashboards
- Configuring alerting rules
- Detecting release regressions against a captured pre-deploy baseline
- Correlating metrics to traces, or mapping service dependencies
- Implementing distributed tracing
- Debugging production issues with observability
- Performance testing and load testing
- Application profiling and bottleneck analysis
- Capacity planning and resource forecasting

## Do not use this skill when

- The request is only for a single vendor UI walkthrough with no implementation decisions
- The system already has a finalized observability plan and only needs routine execution
- The task is post-deploy smoke or synthetic checking of a deployed URL, not deciding what the service itself measures
- The user wants unrelated security auditing or code review not tied to monitoring

## Required inputs

- Service overview (architecture, language/runtime, deployment model)
- Current telemetry stack (if any) and constraints
- Critical user journeys or business KPIs
- Traffic profile and latency/error targets
- Compliance or data handling constraints (PII, retention)

## Workflow

1. **Scope goals** - Confirm critical paths, SLIs/SLOs, and stakeholders.
   - Output: Monitoring goals and scope statement.
2. **Plan instrumentation** - Define structured (JSON) logs, metrics, and traces to add, every signal carrying a request/trace ID for correlation and sensitive fields (passwords, tokens, PII) redacted; include a health check endpoint when the architecture does not already expose an equivalent.
   - Decision: If no tracing is feasible, prioritize logs + metrics with correlation IDs.
   - Decision: If both traces and metrics are collected, attach trace IDs as exemplars on latency histograms so a metric spike resolves to one concrete trace, and keep error/slow-path trace sampling high enough that an exemplar resolves to a stored trace rather than a dropped one (`references/prometheus-metrics.md`).
   - Output: Instrumentation backlog with owners and acceptance criteria.
3. **Select collection/storage** - Choose agents, pipelines, retention, and cardinality limits.
   - Decision: If managed services are mandated, align to vendor-specific exporters and limits.
   - Output: Telemetry architecture and data flow summary.
4. **Design dashboards** - Build RED/USE-based views covering business KPIs alongside technical signals, each dashboard named for its audience and the decision it serves.
   - Output: Dashboard spec (panels, queries, refresh, owners).
5. **Define alerting** - Alert on critical-path symptoms and error budgets, never on every error; set thresholds, burn-rate alerts, and paging policies.
   - Decision: If alert volume is high, switch to error budget or anomaly alerts.
   - Decision: If releases must be validated after rollout, capture a pre-deploy baseline and alert on the delta from it alongside the absolute thresholds (`references/alerting-rules.md`).
   - Decision: If the service terminates TLS, signs tokens, or holds fixed-lifetime credentials, add expiry alerts with enough lead time to complete rotation.
   - Output: Alert policy and routing matrix, every alert carrying an owner and a runbook link.
6. **Performance & capacity** - Plan load tests, profiling, and capacity models.
   - Output: Test plan, profiling targets, and capacity assumptions.
7. **Verify & roll out** - Emit a test request and require its correlated log, metric, and trace to all appear; exercise each alert route and treat a failure to page the declared owner as a rollout blocker.
   - Output: Verification checklist and operational handoff notes.

## Resources

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Logging | `references/structured-logging.md` | Pino, JSON logging |
| Metrics | `references/prometheus-metrics.md` | Counter, Histogram, Gauge, exemplars |
| Tracing | `references/opentelemetry.md` | OpenTelemetry, spans |
| Alerting | `references/alerting-rules.md` | Prometheus alerts, baseline regressions, expiry |
| Dashboards | `references/dashboards.md` | RED/USE method, Grafana, topology |
| Performance Testing (k6) | `references/performance-testing-k6.md` | Load test types, k6 stages |
| Performance Testing (tools) | `references/performance-testing-tools.md` | Artillery, Locust, JMeter |
| Performance Testing (scenarios) | `references/performance-testing-scenarios-metrics.md` | Metrics, user journeys |
| Profiling (Node/Python) | `references/application-profiling-node-python.md` | CPU/memory profiling |
| Profiling (Go/Java) | `references/application-profiling-go-java.md` | pprof, async-profiler |
| Profiling (databases) | `references/application-profiling-database.md` | Query profiling |
| Profiling (APM) | `references/application-profiling-apm.md` | Custom spans, vendor hooks |
| Profiling (quick reference) | `references/application-profiling-quick-reference.md` | Tooling summary |
| Capacity Planning (forecasting) | `references/capacity-planning-forecasting.md` | Trends, predict_linear |
| Capacity Planning (resource models) | `references/capacity-planning-resource-models.md` | CPU, memory, connections |
| Capacity Planning (scaling) | `references/capacity-planning-scaling.md` | Autoscaling patterns |
| Capacity Planning (budgets/costs) | `references/capacity-planning-budgets-costs.md` | Budgets, sizing |
| Capacity Planning (alerts/reference) | `references/capacity-planning-alerts-reference.md` | Alerts, heuristics |
| Strategy | `references/observability-strategy.md` | End-to-end observability planning |

## Examples

**Example 1: Instrumentation plan**

Input: “Add observability to our Node.js API and define alerts for latency.”

Output:
- Goals: 95th percentile latency < 400ms; error rate < 1%
- Instrumentation: JSON logs with request_id, `http.server.duration` histogram with trace-ID exemplars, traces for `/checkout`
- Alerting: 5m burn-rate alert on latency, error budget alert on 4xx/5xx, post-deploy alert on the delta from the captured pre-deploy baseline
- Verification: one test request traced end to end — its log line, histogram observation, and trace all carry the same trace ID

**Example 2: Performance testing**

Input: “We need load tests to validate 2x traffic before launch.”

Output:
- k6 scenario: ramp 50 → 200 VUs over 10m, steady for 15m
- Targets: `/search`, `/checkout`, `/login`
- Pass criteria: p95 < 500ms, error rate < 0.5%

## Output contract

When executing this skill, respond with the following sections:

- **Summary**: One-paragraph overview of the monitoring plan.
- **Assumptions & Inputs**: Any inferred context or missing data.
- **Instrumentation Plan**: Logs/metrics/traces to add, with owners.
- **Telemetry Architecture**: Collection, storage, retention, limits.
- **Dashboards**: Panel list and KPIs.
- **Alerting**: Policies, thresholds, routing.
- **Performance & Capacity**: Test plan and profiling targets.
- **Verification**: Steps to confirm signals and alerting work.
- **Risks & Follow-ups**: Gaps or decisions needed.

## References

See `references/README.md` for the index of detailed playbooks.
