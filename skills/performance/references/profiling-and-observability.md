# Profiling and Observability Reference

Use this reference to collect evidence for bottlenecks and establish baselines.

## Telemetry checklist

- Metrics: request latency, error rate, saturation (CPU, memory, I/O).
- Traces: top spans by duration, hot paths, fan-out patterns.
- Logs: slow queries, timeouts, retries, cache misses.
- Frontend: Core Web Vitals, bundle size, render timing.
- Freshness: age of the value served, cache hit rate, queue depth, upstream provider response time. Freshness age is a first-class metric, not a footnote to latency — a read path can get faster and less correct at the same time, and only these two measured together will show it.
- Feedback loop: cold build, incremental rebuild or hot reload, test-suite duration, type-check time, lint time, container image build. No runtime profiler reports any of these, so they degrade silently unless they are on the telemetry list.

Decision:
- If telemetry is missing, document the gap and propose the minimum instrumentation needed before optimizing.
- If distributed tracing is unavailable, write the hot path out by hand as a segment chain — triggering event, each hop, user-visible state — and measure each segment separately. It is a weaker artifact than a trace, but it still localizes the cost and it can be produced without new instrumentation.

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
