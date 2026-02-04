# Performance Testing: k6 Workflows

Use this reference for k6-based load testing patterns and test types.

## Load Testing with k6

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp-up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp-up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp-down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    errors: ['rate<0.1'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/products');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  }) || errorRate.add(1);

  sleep(1);
}
```

## Test Types (k6 Options)

### Load Test
```javascript
// Gradual ramp-up to expected production load
export const options = {
  stages: [
    { duration: '5m', target: 100 },
    { duration: '30m', target: 100 },
    { duration: '5m', target: 0 },
  ],
};
```

### Stress Test
```javascript
// Push beyond normal capacity to find breaking point
export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 200 },
    { duration: '5m', target: 300 },
    { duration: '5m', target: 400 },
    { duration: '2m', target: 0 },
  ],
};
```

### Spike Test
```javascript
// Sudden increase in load
export const options = {
  stages: [
    { duration: '1m', target: 100 },
    { duration: '30s', target: 1000 }, // Spike
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
};
```

### Soak Test
```javascript
// Extended duration at normal load
export const options = {
  stages: [
    { duration: '5m', target: 100 },
    { duration: '8h', target: 100 },  // Long duration
    { duration: '5m', target: 0 },
  ],
};
```
