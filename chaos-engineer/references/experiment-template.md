# Chaos Experiment Template

Provides a fill-in template for documenting an experiment plan.

## Usage

1. Replace placeholders with the target system and hypothesis.
2. Confirm steady-state metrics and guardrails with owners.
3. Review blast radius and rollback triggers before execution.

## Verification

- Validate all steady-state queries return data.
- Confirm rollback triggers are measurable and actionable.
- Ensure experiment duration aligns with the environment limits.

```yaml
name: "Database Connection Pool Exhaustion"
hypothesis: "When the database connection pool is exhausted, the application will gracefully degrade and return 503 errors without cascading failures"

steady_state:
  metrics:
    - name: "Error Rate"
      threshold: "< 0.1%"
      source: "prometheus"
      query: "rate(http_requests_total{status=~'5..'}[5m])"
    - name: "Latency P99"
      threshold: "< 500ms"
      source: "datadog"
    - name: "Active Connections"
      threshold: "> 10"
      query: "pg_stat_activity_count"

blast_radius:
  environment: "staging"
  traffic_percentage: 10
  duration_seconds: 300
  max_error_rate: "5%"
  auto_rollback: true

injection:
  type: "resource_exhaustion"
  target: "database_connections"
  method: "connection_leak"
  parameters:
    leak_rate: 5
    max_leaked: 50

safety:
  rollback_triggers:
    - "error_rate > 5%"
    - "manual_kill_switch"
    - "duration_exceeded"
  rollback_time_limit_seconds: 30
  alerts:
    - slack: "#chaos-engineering"
    - pagerduty: "chaos-team"

success_criteria:
  - "Circuit breakers activate within 10s"
  - "503 errors returned (not 500)"
  - "No cascading failures to other services"
  - "System recovers within 60s of rollback"
```
