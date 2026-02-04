# Deployment Metrics and Automated Canary

## Deployment Metrics (DORA)

Track four key metrics and align targets with team goals:

- **Deployment Frequency**
- **Lead Time for Changes**
- **Change Failure Rate**
- **MTTR**

```yaml
# Prometheus metrics for DORA tracking
- record: deployment:frequency:1d
  expr: count_over_time(deployment_completed[1d])

- record: deployment:lead_time:p95
  expr: histogram_quantile(0.95,
    rate(commit_to_deploy_seconds_bucket[1h]))

- record: deployment:failure_rate
  expr: |
    sum(rate(deployment_failed[1h]))
    / sum(rate(deployment_total[1h]))
```

Verification: ensure the metrics populate with real release data and alert on regressions.

## Automated Canary with Flagger

Requirements: Flagger installed and integrated with a service mesh (e.g., Istio).

```yaml
# Flagger: automated canary with rollback
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: api
spec:
  provider: istio
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  progressDeadlineSeconds: 60
  service:
    port: 8080
    trafficPolicy:
      tls:
        mode: ISTIO_MUTUAL
  analysis:
    interval: 30s
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
      - name: error-rate
        templateRef:
          name: error-rate
        thresholdRange:
          max: 1
      - name: latency
        templateRef:
          name: latency
        thresholdRange:
          max: 500
```

Verification: watch the canary progression and confirm rollback triggers when metrics exceed thresholds.
