# Capacity Planning: Alerts and Reference

Use this reference for capacity-related alerts and planning heuristics.

## Capacity Alerts

```yaml
# Prometheus alerting rules
groups:
  - name: capacity
    rules:
      - alert: HighCPUPrediction
        expr: |
          predict_linear(
            node_cpu_seconds_total{mode="idle"}[1h],
            3600 * 24 * 7  # 7 days ahead
          ) < 0.2
        for: 1h
        annotations:
          summary: CPU capacity will be exhausted in 7 days

      - alert: DiskSpaceProjection
        expr: |
          predict_linear(
            node_filesystem_avail_bytes[7d],
            3600 * 24 * 30
          ) < 1e9  # Less than 1GB in 30 days
        annotations:
          summary: Disk space will run out in 30 days

      - alert: DatabaseConnectionsNearLimit
        expr: |
          pg_stat_database_numbackends / pg_settings_max_connections > 0.8
        for: 10m
        annotations:
          summary: Database connections at 80% capacity

      - alert: ScalingRecommendation
        expr: |
          rate(http_requests_total[5m]) >
          (instance_capacity * instance_count * 0.7)
        annotations:
          summary: Consider scaling up - traffic approaching capacity
```

## Quick Reference

| Metric | Buffer | Reasoning |
|--------|--------|-----------|
| CPU | 30% | Headroom for spikes |
| Memory | 20% | GC and OS overhead |
| Connections | 25% | Connection churn |
| Storage | 40% | Growth + snapshots |

| Planning Horizon | Update Frequency |
|------------------|------------------|
| 3 months | Weekly |
| 6 months | Bi-weekly |
| 12 months | Monthly |

| Scaling Trigger | Action |
|-----------------|--------|
| 70% CPU | Start planning |
| 80% CPU | Scale up |
| 90% CPU | Emergency scaling |
| 60% CPU for 24h | Scale down |
