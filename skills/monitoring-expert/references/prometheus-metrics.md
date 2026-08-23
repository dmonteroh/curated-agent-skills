# Prometheus Metrics

## Metric Types

```typescript
import { Registry, Counter, Histogram, Gauge, Summary } from 'prom-client';

const register = new Registry();

// Counter - cumulative, only increases
const httpRequests = new Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'path', 'status'],
  registers: [register],
});

// Histogram - distribution with buckets
const httpDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'path'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 5],
  registers: [register],
});

// Gauge - point-in-time value, can go up/down
const activeConnections = new Gauge({
  name: 'active_connections',
  help: 'Number of active connections',
  registers: [register],
});

// Summary - similar to histogram with percentiles
const responseSummary = new Summary({
  name: 'http_response_size_bytes',
  help: 'HTTP response size',
  percentiles: [0.5, 0.9, 0.99],
  registers: [register],
});
```

## HTTP Middleware

```typescript
app.use((req, res, next) => {
  const end = httpDuration.startTimer({
    method: req.method,
    path: req.route?.path || req.path,
  });

  res.on('finish', () => {
    httpRequests.inc({
      method: req.method,
      path: req.route?.path || req.path,
      status: res.statusCode,
    });
    end();
  });

  next();
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.send(await register.metrics());
});
```

## Business Metrics

```typescript
// Orders
const ordersCreated = new Counter({
  name: 'orders_created_total',
  help: 'Total orders created',
  labelNames: ['status', 'payment_method'],
});

const orderValue = new Histogram({
  name: 'order_value_dollars',
  help: 'Order value in dollars',
  buckets: [10, 50, 100, 500, 1000],
});

// Usage
ordersCreated.inc({ status: 'completed', payment_method: 'card' });
orderValue.observe(order.total);
```

## Exemplars (Metric to Trace Correlation)

An exemplar attaches a trace ID to one individual observation inside a histogram bucket. The panel showing p99 latency then carries clickable points that resolve to a concrete trace of a slow request, instead of leaving the responder to search the tracing backend by service and time window - a search that mostly returns requests that were fine.

```typescript
// prom-client v15+: exemplars are opt-in per metric.
const httpDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'path'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 5],
  enableExemplars: true,
  registers: [register],
});

httpDuration.observe({
  labels: { method: req.method, path: req.route?.path },
  value: durationSeconds,
  exemplarLabels: { traceId: activeSpan.spanContext().traceId },
});
```

```python
# prometheus_client: exemplar is a keyword on the observation itself.
# Exemplar label values are strings and are length-capped, so format the
# trace ID as hex rather than passing the raw integer.
trace_id = format(trace.get_current_span().get_span_context().trace_id, '032x')
http_duration.labels(method=method, path=path).observe(
    duration_seconds,
    exemplar={'trace_id': trace_id}
)
```

Wrong version, and it is the failure this technique exists to replace:

```typescript
// Trace ID as a label - one new time series per request. This is the
// cardinality explosion, not correlation.
httpRequests.inc({ method: req.method, path: req.path, trace_id: traceId });
```

Exemplars are stored out of band, alongside the series rather than as part of its identity, so a unique trace ID per observation adds no series. That is the whole reason the technique is safe and a label is not.

Three things must all be true or the exemplar never appears:

- The metric is a histogram (or counter) with exemplar support enabled, as above.
- The scrape negotiates OpenMetrics and the Prometheus server has exemplar storage enabled - default-off in Prometheus, exposed as a feature flag.
- The metrics data source knows how to resolve a trace ID into a link against the tracing backend. An exemplar nobody can click is storage with no consumer.

Sampling interacts with this directly: an exemplar pointing at a trace the sampler dropped is a dead link. Where exemplars are the intended debugging path, keep error and slow-path traces sampled at a higher rate than the baseline so the exemplars attached to the interesting buckets still resolve.

## Default Metrics

```typescript
import { collectDefaultMetrics } from 'prom-client';

// Collect Node.js metrics (memory, CPU, etc.)
collectDefaultMetrics({ register });
```

## Python (prometheus_client)

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

http_requests = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'path', 'status']
)

http_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'path']
)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Quick Reference

| Type | Use Case | Example |
|------|----------|---------|
| Counter | Cumulative totals | Requests, errors |
| Gauge | Current value | Active users, queue size |
| Histogram | Distributions | Response times |
| Summary | Percentiles | Similar to histogram |

| Naming | Convention |
|--------|------------|
| Unit suffix | `_seconds`, `_bytes`, `_total` |
| Base unit | Use seconds, bytes (not ms, KB) |
| Prefix | App/service name |
