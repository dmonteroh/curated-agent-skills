---
name: monitoring-expert
description: "Provides end-to-end observability across logs, metrics, traces, alerting, and performance testing. Use when instrumenting services, setting alert strategy, or designing an observability stack."
category: observability
---
# Monitoring Expert

Provides guidance for implementing monitoring, alerting, tracing, and performance testing systems.

## When to Use This Skill

- Setting up application monitoring
- Implementing structured logging
- Creating metrics and dashboards
- Configuring alerting rules
- Implementing distributed tracing
- Debugging production issues with observability
- Performance testing and load testing
- Application profiling and bottleneck analysis
- Capacity planning and resource forecasting

## Do Not Use This Skill When

- The request is only for a single vendor UI walkthrough with no implementation decisions
- The system already has a finalized observability plan and only needs routine execution
- The user wants unrelated security auditing or code review not tied to monitoring

## Activation Cues

- “Add observability/monitoring to this service”
- “We need logs/metrics/traces/alerts”
- “Set up Prometheus/Grafana/Loki/Jaeger/OpenTelemetry”
- “Design an alert strategy or SLO/SLA monitoring”
- “Plan performance tests or profiling for bottlenecks”

## Required Inputs

- Service overview (architecture, language/runtime, deployment model)
- Current telemetry stack (if any) and constraints
- Critical user journeys or business KPIs
- Traffic profile and latency/error targets
- Compliance or data handling constraints (PII, retention)

## Core Workflow

1. **Scope goals** - Confirm critical paths, SLIs/SLOs, and stakeholders.
   - Output: Monitoring goals and scope statement.
2. **Plan instrumentation** - Define logs, metrics, and traces to add.
   - Decision: If no tracing is feasible, prioritize logs + metrics with correlation IDs.
   - Output: Instrumentation backlog with owners and acceptance criteria.
3. **Select collection/storage** - Choose agents, pipelines, retention, and cardinality limits.
   - Decision: If managed services are mandated, align to vendor-specific exporters and limits.
   - Output: Telemetry architecture and data flow summary.
4. **Design dashboards** - Build RED/USE-based views and service KPIs.
   - Output: Dashboard spec (panels, queries, refresh, owners).
5. **Define alerting** - Set thresholds, burn-rate alerts, and paging policies.
   - Decision: If alert volume is high, switch to error budget or anomaly alerts.
   - Output: Alert policy and routing matrix.
6. **Performance & capacity** - Plan load tests, profiling, and capacity models.
   - Output: Test plan, profiling targets, and capacity assumptions.
7. **Verify & roll out** - Validate signals, run smoke checks, and document runbooks.
   - Output: Verification checklist and operational handoff notes.

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Logging | `references/structured-logging.md` | Pino, JSON logging |
| Metrics | `references/prometheus-metrics.md` | Counter, Histogram, Gauge |
| Tracing | `references/opentelemetry.md` | OpenTelemetry, spans |
| Alerting | `references/alerting-rules.md` | Prometheus alerts |
| Dashboards | `references/dashboards.md` | RED/USE method, Grafana |
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

## Constraints

### MUST DO
- Use structured logging (JSON)
- Include request IDs for correlation
- Set up alerts for critical paths
- Monitor business metrics, not just technical
- Use appropriate metric types (counter/gauge/histogram)
- Implement health check endpoints

### MUST NOT DO
- Log sensitive data (passwords, tokens, PII)
- Alert on every error (alert fatigue)
- Use string interpolation in logs (use structured fields)
- Skip correlation IDs in distributed systems

## Common Pitfalls

- High-cardinality labels that explode metric storage
- Alerts without ownership or runbook links
- Dashboards without clear users or decision intent
- Traces sampled too aggressively to diagnose latency spikes
- Missing retention policies or log redaction

## Knowledge Reference

Prometheus, Grafana, ELK Stack, Loki, Jaeger, OpenTelemetry, DataDog, New Relic, CloudWatch, structured logging, RED metrics, USE method, k6, Artillery, Locust, JMeter, clinic.js, pprof, py-spy, async-profiler, capacity planning

## Examples

**Example 1: Instrumentation plan**

Input: “Add observability to our Node.js API and define alerts for latency.”

Output:
- Goals: 95th percentile latency < 400ms; error rate < 1%
- Instrumentation: JSON logs with request_id, `http.server.duration` histogram, traces for `/checkout`
- Alerting: 5m burn-rate alert on latency, error budget alert on 4xx/5xx

**Example 2: Performance testing**

Input: “We need load tests to validate 2x traffic before launch.”

Output:
- k6 scenario: ramp 50 → 200 VUs over 10m, steady for 15m
- Targets: `/search`, `/checkout`, `/login`
- Pass criteria: p95 < 500ms, error rate < 0.5%

## Output Contract

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
