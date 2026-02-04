# Alert Design Examples

Good alerts are actionable, not just informative.

```yaml
# alerts.yaml
groups:
  - name: slo_alerts
    rules:
      - alert: ErrorBudgetBurnRateFast
        expr: |
          (
            service:http_requests:error_rate5m > (14.4 * 0.001)
            and
            service:http_requests:error_rate1h > (14.4 * 0.001)
          )
        for: 2m
        labels:
          severity: critical
          slo: availability
        annotations:
          summary: "Fast error budget burn on {{ $labels.service }}"
          description: |
            Service {{ $labels.service }} is burning error budget at 14.4x rate.
            At this rate, 30-day budget will exhaust in 2 days.

            RUNBOOK: https://runbooks.example.com/error-budget-burn

      - alert: ErrorBudgetBurnRateSlow
        expr: |
          (
            service:http_requests:error_rate6h > (6 * 0.001)
            and
            service:http_requests:error_rate1d > (6 * 0.001)
          )
        for: 15m
        labels:
          severity: warning
          slo: availability
        annotations:
          summary: "Slow error budget burn on {{ $labels.service }}"
          description: |
            Service {{ $labels.service }} is burning error budget at 6x rate.

            RUNBOOK: https://runbooks.example.com/error-budget-burn

      - alert: LatencySLOViolation
        expr: |
          service:http_request_duration_seconds:p99 > 0.5
        for: 5m
        labels:
          severity: warning
          slo: latency
        annotations:
          summary: "P99 latency exceeds 500ms on {{ $labels.service }}"
          description: |
            P99 latency is {{ $value }}s, exceeding 500ms threshold.

            RUNBOOK: https://runbooks.example.com/high-latency

      - alert: HighMemoryUtilization
        expr: |
          service:memory_utilization > 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.service }}"
          description: |
            Memory utilization is {{ $value | humanizePercentage }}.

            RUNBOOK: https://runbooks.example.com/high-memory
```
