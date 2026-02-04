# Golden Signals Monitoring

Monitor the four golden signals for every service.

```yaml
# prometheus_rules.yaml
groups:
  - name: golden_signals
    interval: 30s
    rules:
      - record: service:http_request_duration_seconds:p50
        expr: |
          histogram_quantile(0.50,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
          )

      - record: service:http_request_duration_seconds:p95
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
          )

      - record: service:http_request_duration_seconds:p99
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
          )

      - record: service:http_requests:rate5m
        expr: |
          sum(rate(http_requests_total[5m])) by (service)

      - record: service:http_requests:error_rate5m
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
          /
          sum(rate(http_requests_total[5m])) by (service)

      - record: service:cpu_utilization
        expr: |
          avg(rate(container_cpu_usage_seconds_total[5m])) by (service)

      - record: service:memory_utilization
        expr: |
          avg(container_memory_working_set_bytes / container_spec_memory_limit_bytes)
          by (service)
```
