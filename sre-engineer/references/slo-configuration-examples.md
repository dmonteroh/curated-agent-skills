# SLO Configuration Examples

```yaml
# slo_config.yaml
apiVersion: sre/v1
kind: ServiceLevelObjective
metadata:
  service: payment-api
  environment: production
spec:
  slos:
    - name: availability
      description: "Users can successfully complete payment requests"
      sli:
        metric: http_requests_total
        query: |
          sum(rate(http_requests_total{status=~"2..|4..", service="payment-api"}[30d]))
          /
          sum(rate(http_requests_total{service="payment-api"}[30d]))
      target: 0.999
      window: 30d

    - name: latency
      description: "Payment requests complete quickly"
      sli:
        metric: http_request_duration_seconds
        query: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket{service="payment-api"}[30d]))
            by (le)
          ) < 0.5
      target: 0.99
      window: 30d
```
