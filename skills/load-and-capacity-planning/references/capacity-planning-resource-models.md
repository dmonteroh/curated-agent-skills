# Capacity Planning: Resource Models

Use these examples to estimate CPU, memory, and connection capacity needs.

## CPU Requirements

```javascript
// Current capacity
const currentRPS = 1000;
const currentCPU = 0.65;  // 65% utilization
const targetCPU = 0.70;   // Target 70% max

// Projected load
const projectedRPS = 2500;

// Required CPU capacity
const cpuScalingFactor = projectedRPS / currentRPS;
const requiredCPU = (currentCPU * cpuScalingFactor) / targetCPU;

console.log(`Current: ${currentRPS} RPS @ ${currentCPU * 100}% CPU`);
console.log(`Projected: ${projectedRPS} RPS requires ${requiredCPU.toFixed(2)}x CPU`);
```

## Memory Requirements

```javascript
// Memory per request (average)
const avgMemoryPerRequest = 2048;  // bytes
const concurrentRequests = 500;
const overhead = 1.3;  // 30% overhead for GC, OS, etc.

const requiredMemory = (avgMemoryPerRequest * concurrentRequests * overhead) / (1024 ** 3);
console.log(`Required memory: ${requiredMemory.toFixed(2)} GB`);
```

## Database Connections

```javascript
// Connections per instance
const connectionsPerInstance = 100;
const instances = 5;
const utilizationTarget = 0.75;

// Available connections
const totalConnections = connectionsPerInstance * instances;
const effectiveConnections = totalConnections * utilizationTarget;

// RPS capacity
const avgRequestsPerConnection = 10;
const maxRPS = effectiveConnections * avgRequestsPerConnection;

console.log(`Max sustainable RPS: ${maxRPS}`);
```
