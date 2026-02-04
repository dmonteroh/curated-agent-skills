# Prometheus Queries for Error Budgets

```promql
# Calculate 30-day availability SLI
sum(rate(http_requests_total{status=~"2..", job="api"}[30d]))
/
sum(rate(http_requests_total{job="api"}[30d]))

# Calculate error budget consumption
1 - (
  sum(rate(http_requests_total{status=~"2..", job="api"}[30d]))
  /
  sum(rate(http_requests_total{job="api"}[30d]))
)

# Calculate remaining error budget (for 99.9% SLO)
(0.001 - (1 - (
  sum(rate(http_requests_total{status=~"2..", job="api"}[30d]))
  /
  sum(rate(http_requests_total{job="api"}[30d]))
))) / 0.001

# Burn rate (normalized to 1.0 = sustainable)
(1 - (
  sum(rate(http_requests_total{status=~"2..", job="api"}[1h]))
  /
  sum(rate(http_requests_total{job="api"}[1h]))
)) / 0.001
```
