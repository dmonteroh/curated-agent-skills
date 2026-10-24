# Performance Testing: Scenarios and Metrics

Use this reference to define metrics, custom measurements, and user journey scenarios.

## Performance Metrics to Track

```javascript
// k6 custom metrics
import { Counter, Trend, Gauge } from 'k6/metrics';

const checkoutDuration = new Trend('checkout_duration');
const cartSize = new Gauge('cart_size');
const orderCounter = new Counter('orders_created');

export default function () {
  const startTime = Date.now();

  const res = http.post('https://api.example.com/checkout', payload);

  checkoutDuration.add(Date.now() - startTime);
  orderCounter.add(1);
  cartSize.add(payload.items.length);
}
```

## Test Scenario Design

```javascript
// Realistic user journey
import { scenario } from 'k6/execution';

export const options = {
  scenarios: {
    browser_users: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '5m', target: 100 },
        { duration: '10m', target: 100 },
      ],
      gracefulRampDown: '30s',
    },
    api_users: {
      executor: 'constant-arrival-rate',
      rate: 50,
      timeUnit: '1s',
      duration: '15m',
      preAllocatedVUs: 100,
    },
  },
};

export default function () {
  // Homepage
  http.get('https://example.com/');
  sleep(Math.random() * 3);

  // Search
  http.get('https://example.com/search?q=laptop');
  sleep(Math.random() * 5);

  // Product page
  http.get('https://example.com/products/123');
  sleep(Math.random() * 10);

  // Add to cart (30% conversion)
  if (Math.random() < 0.3) {
    http.post('https://example.com/cart', { productId: 123 });
  }
}
```

## Quick Reference

| Test Type | Purpose | Duration |
|-----------|---------|----------|
| Load | Normal capacity | 30m - 2h |
| Stress | Find limits | 1h - 4h |
| Spike | Sudden traffic | 15m - 30m |
| Soak | Memory leaks | 4h - 24h |

| Tool | Language | Best For |
|------|----------|----------|
| k6 | JavaScript | API testing, CI/CD |
| Artillery | YAML/JS | Simple scenarios |
| Locust | Python | Complex scenarios |
| JMeter | GUI/XML | Legacy systems |

| Metric | Target |
|--------|--------|
| p95 latency | < 500ms |
| p99 latency | < 1s |
| Error rate | < 1% |
| RPS | 10x normal |
