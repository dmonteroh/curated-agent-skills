# Capacity Planning: Budgets and Cost Optimization

Use this reference for performance budgets and sizing cost tradeoffs.

## Performance Budgets

```javascript
const performanceBudget = {
  // Page load budgets
  ttfb: 200,          // Time to First Byte (ms)
  fcp: 1000,          // First Contentful Paint (ms)
  lcp: 2500,          // Largest Contentful Paint (ms)

  // API budgets
  apiP50: 100,        // 50th percentile (ms)
  apiP95: 500,        // 95th percentile (ms)
  apiP99: 1000,       // 99th percentile (ms)

  // Resource budgets
  jsBundle: 200,      // JavaScript bundle size (KB)
  cssBundle: 50,      // CSS bundle size (KB)
  images: 500,        // Total images (KB)

  // Infrastructure budgets
  cpuUtilization: 70,     // Max % during normal load
  memoryUtilization: 80,  // Max % during normal load
  errorRate: 0.01,        // Max 1% error rate
};

function checkBudget(actual, budget, metric) {
  if (actual > budget) {
    console.warn(`Budget exceeded for ${metric}: ${actual} > ${budget}`);
    return false;
  }
  return true;
}
```

## Cost Optimization

### Instance Sizing

```javascript
function optimizeInstanceSize(workload) {
  const instances = [
    { type: 't3.small', vcpu: 2, memory: 2, cost: 0.0208 },
    { type: 't3.medium', vcpu: 2, memory: 4, cost: 0.0416 },
    { type: 't3.large', vcpu: 2, memory: 8, cost: 0.0832 },
    { type: 'm5.large', vcpu: 2, memory: 8, cost: 0.096 },
    { type: 'm5.xlarge', vcpu: 4, memory: 16, cost: 0.192 },
  ];

  const filtered = instances.filter(i =>
    i.vcpu >= workload.requiredVCPU &&
    i.memory >= workload.requiredMemory
  );

  // Sort by cost efficiency
  return filtered.sort((a, b) => {
    const scoreA = (a.vcpu * a.memory) / a.cost;
    const scoreB = (b.vcpu * b.memory) / b.cost;
    return scoreB - scoreA;
  })[0];
}

const recommendation = optimizeInstanceSize({
  requiredVCPU: 2,
  requiredMemory: 4,
});

console.log('Recommended instance:', recommendation);
```
