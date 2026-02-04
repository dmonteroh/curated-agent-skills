# Application Profiling: Node.js and Python

Use this reference for CPU, memory, and timing profiling in Node.js and Python services.

## Node.js Profiling

### CPU Profiling with clinic.js

```bash
# Install
npm install -g clinic

# CPU profiling
clinic doctor -- node app.js

# Flame graph
clinic flame -- node app.js

# Bubble profiling
clinic bubbleprof -- node app.js

# Generate report
clinic doctor --collect-only -- node app.js
clinic doctor --visualize-only PID.clinic-doctor
```

### Built-in Node.js Profiler

```javascript
// Start profiling
node --prof app.js

# Process the output
node --prof-process isolate-0x*.log > processed.txt

# Chrome DevTools
node --inspect app.js
# Open chrome://inspect
```

### Memory Profiling

```javascript
import v8 from 'v8';
import fs from 'fs';

// Heap snapshot
const snapshot = v8.writeHeapSnapshot();
console.log('Snapshot written to:', snapshot);

// Memory usage
const usage = process.memoryUsage();
console.log({
  rss: `${Math.round(usage.rss / 1024 / 1024)}MB`,
  heapTotal: `${Math.round(usage.heapTotal / 1024 / 1024)}MB`,
  heapUsed: `${Math.round(usage.heapUsed / 1024 / 1024)}MB`,
  external: `${Math.round(usage.external / 1024 / 1024)}MB`,
});
```

### Custom Performance Marks

```javascript
import { performance, PerformanceObserver } from 'perf_hooks';

// Mark start
performance.mark('operation-start');

// ... do work ...
await processOrder(orderId);

// Mark end
performance.mark('operation-end');

// Measure
performance.measure('operation', 'operation-start', 'operation-end');

// Observer
const obs = new PerformanceObserver((items) => {
  items.getEntries().forEach((entry) => {
    console.log(`${entry.name}: ${entry.duration}ms`);
  });
});
obs.observe({ entryTypes: ['measure'] });
```

## Python Profiling

### cProfile

```python
import cProfile
import pstats

# Profile a function
def main():
    # Your code here
    process_data()

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

### Line Profiler

```python
from line_profiler import LineProfiler

@profile
def expensive_function():
    # Code to profile
    result = []
    for i in range(10000):
        result.append(i ** 2)
    return result

# Run with: kernprof -l -v script.py
```

### Memory Profiler

```python
from memory_profiler import profile

@profile
def process_large_data():
    data = [i for i in range(1000000)]
    result = [x * 2 for x in data]
    return result

# Run with: python -m memory_profiler script.py
```

### py-spy

```bash
# CPU sampling (live process)
py-spy top --pid 12345

# Generate flame graph
py-spy record -o profile.svg --pid 12345

# Record for duration
py-spy record -o profile.svg --duration 60 -- python app.py
```
