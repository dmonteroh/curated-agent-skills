# Application Profiling: Quick Reference

Use these tables to choose tooling and interpret profiling signals.

## Tooling Summary

| Tool | Language | Type |
|------|----------|------|
| clinic.js | Node.js | CPU, Event loop |
| Chrome DevTools | Node.js | CPU, Memory |
| cProfile | Python | CPU |
| py-spy | Python | CPU (sampling) |
| pprof | Go | CPU, Memory, Goroutines |
| VisualVM | Java | CPU, Memory, Threads |
| async-profiler | Java | CPU, Allocation |

## Signal Interpretation

| Metric | What to Look For |
|--------|------------------|
| CPU time | Hot functions, tight loops |
| Memory | Large allocations, leaks |
| I/O wait | Blocking operations |
| GC time | Excessive collections |
| Thread count | Thread pool saturation |

| Problem | Symptom |
|---------|---------|
| CPU bound | High CPU usage, slow processing |
| Memory leak | Growing memory, eventual crash |
| I/O bound | Low CPU, high wait time |
| Lock contention | Idle threads, poor scaling |
