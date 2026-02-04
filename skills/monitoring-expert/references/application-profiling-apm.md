# Application Profiling: APM Integration

Use this reference for adding targeted profiling or span detail through APM vendors.

## New Relic

```javascript
import newrelic from 'newrelic';

// Custom transaction
newrelic.startBackgroundTransaction('process-orders', async () => {
  const orders = await getOrders();

  // Custom segment
  await newrelic.startSegment('validate-orders', true, async () => {
    return validateOrders(orders);
  });
});

// Custom metrics
newrelic.recordMetric('Custom/OrderValue', orderTotal);
```

## DataDog APM

```javascript
import tracer from 'dd-trace';
tracer.init();

// Custom span
const span = tracer.startSpan('process.order', {
  resource: orderId,
  tags: {
    'order.total': orderTotal,
    'user.id': userId,
  },
});

try {
  await processOrder(orderId);
  span.setTag('status', 'success');
} catch (err) {
  span.setTag('error', err);
} finally {
  span.finish();
}
```
