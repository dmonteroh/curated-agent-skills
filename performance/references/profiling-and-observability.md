# Profiling and Observability Reference

Use this reference to collect evidence for bottlenecks and establish baselines.

## Required inputs

- Target scope (service, endpoint, UI flow, batch job)
- Environment details (hardware, dataset size, config flags)
- Success metrics (latency percentiles, throughput, error rate, cost)

## Telemetry checklist

- Metrics: request latency, error rate, saturation (CPU, memory, I/O).
- Traces: top spans by duration, hot paths, fan-out patterns.
- Logs: slow queries, timeouts, retries, cache misses.
- Frontend: Core Web Vitals, bundle size, render timing.

Decision:
- If telemetry is missing, document the gap and propose the minimum instrumentation needed before optimizing.

## Profiling methods

- CPU: sampling profiler or flame graph with hot path ranking.
- Memory: heap snapshot or allocation profile with GC pressure notes.
- I/O: slow query logs, network timing, disk latency.
- Concurrency: thread or event-loop utilization and queue depth.

## Evidence to capture

- Baseline measurements with timestamps and environment notes.
- One or two representative traces or profile artifacts.
- Ranked bottlenecks with estimated contribution.

## Outputs

- Baseline summary table (metrics + environment).
- Bottleneck list with evidence links or summaries.
- Instrumentation TODOs (if any).
