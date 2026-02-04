# Platform Metrics and Adoption

## Platform Metrics

```yaml
# prometheus/platform-metrics.yaml
groups:
  - name: platform
    rules:
      - record: platform:self_service:rate
        expr: |
          sum(rate(platform_provision_automated[1h]))
          /
          sum(rate(platform_provision_total[1h]))

      - record: platform:provision:p95
        expr: |
          histogram_quantile(0.95,
            rate(platform_provision_duration_bucket[5m]))

      - record: platform:golden_path:adoption
        expr: |
          count(service{template="golden-path"})
          / count(service)
```

Verification: confirm metrics populate and dashboards reflect adoption trends.

## Adoption Strategy

```yaml
# platform-goals.yaml
goals:
  period_1:
    self_service_rate: 90%
    avg_provision_time: 5min
    developer_satisfaction: 4.5/5
    golden_path_adoption: 80%

tracking:
  weekly_provisioning: true
  team_feedback: true
  support_tickets: true
  training_completion: true
```

Verification: review weekly reporting and adjust goals based on feedback.

## Best Practices

- Design for self-service from day one
- Make golden paths the easiest option
- Measure developer satisfaction continuously
- Automate platform operations
- Provide excellent documentation
- Build APIs, not just tools
- Enable safe experimentation
- Maintain backward compatibility
- Treat platform as a product
- Gather and act on feedback
- Track adoption metrics regularly
- Invest in developer enablement
- Maintain SLOs for platform uptime
- Provide fast, helpful support
