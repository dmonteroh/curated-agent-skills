# Dashboards

## RED Method (Request-focused)

```
Rate     - Requests per second
Errors   - Failed requests per second
Duration - Response time distribution
```

```promql
# Rate
sum(rate(http_requests_total[5m]))

# Errors
sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
sum(rate(http_requests_total[5m]))

# Duration (p95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## USE Method (Resource-focused)

```
Utilization - % time resource is busy
Saturation  - Queue depth, backlog
Errors      - Error events
```

```promql
# CPU Utilization
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Saturation
node_memory_SwapTotal_bytes - node_memory_SwapFree_bytes

# Disk Errors
rate(node_disk_io_time_weighted_seconds_total[5m])
```

## Dashboard Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVICE OVERVIEW                         │
│  Request Rate │ Error Rate │ p50 Latency │ p99 Latency     │
├─────────────────────────────────────────────────────────────┤
│                    REQUEST METRICS                          │
│  [Graph: Requests/s by endpoint]                           │
│  [Graph: Error rate over time]                             │
├─────────────────────────────────────────────────────────────┤
│                    LATENCY METRICS                          │
│  [Heatmap: Latency distribution]                           │
│  [Graph: p50, p95, p99 over time]                          │
├─────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE                           │
│  CPU │ Memory │ Disk │ Network                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Panels

### Stat Panel (Single Value)

```promql
# Current RPS
sum(rate(http_requests_total[5m]))

# Error percentage
sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
sum(rate(http_requests_total[5m])) * 100
```

### Time Series

```promql
# Requests by status
sum by (status) (rate(http_requests_total[5m]))

# Latency percentiles
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### Table

```promql
# Top endpoints by error rate
topk(10,
  sum by (path) (rate(http_requests_total{status=~"5.."}[5m]))
  /
  sum by (path) (rate(http_requests_total[5m]))
)
```

### Node Graph (Service Dependency Topology)

Every panel above shows one service in isolation, which cannot answer "the checkout path is slow - which hop is it?". A node-graph panel draws services as nodes and calls as edges, weighted by request rate and coloured by error rate, so the failing hop is visible without opening one dashboard per service.

```promql
# Edges: request rate per caller -> callee pair
sum by (source_service, destination_service) (
  rate(http_requests_total[5m])
)

# Edge health: error rate for the same pairs
sum by (source_service, destination_service) (rate(http_requests_total{status=~"5.."}[5m]))
  /
sum by (source_service, destination_service) (rate(http_requests_total[5m]))
```

This panel is only buildable if the metric carries *both* ends of the call. Instrumentation that labels requests with the destination only (the common default) produces a list, not a graph. Two ways to get the caller label: record it server-side from a propagated caller identity header, or derive the edges from trace data instead, where parent/child spans already encode the topology.

Bound it before shipping it. A caller/callee pair label multiplies series count by the number of distinct callers, and it is a prime candidate for the cardinality problem this file's own queries avoid elsewhere - keep the pair label on a small set of coarse service identifiers (never per instance, per route, or per tenant), or drive the panel from a recording rule that pre-aggregates the pairs.

## Business Metrics Dashboard

```promql
# Orders per minute
sum(rate(orders_created_total[5m])) * 60

# Revenue (if tracked)
sum(increase(order_value_dollars_sum[1h]))

# Active users (gauge)
active_users_total
```

## Quick Reference

| Method | Focus | Metrics |
|--------|-------|---------|
| RED | Services | Rate, Errors, Duration |
| USE | Resources | Utilization, Saturation, Errors |

| Panel Type | Use Case |
|------------|----------|
| Stat | Single KPI |
| Time Series | Trends over time |
| Heatmap | Latency distribution |
| Table | Top N, details |
| Gauge | Current vs threshold |
| Node graph | Service dependency topology |
