# Optimization Tactics by Layer

Use this reference to propose measurable fixes after profiling.

## Database

- Validate query plans and add missing indexes.
- Fix N+1 patterns and reduce round trips.
- Tune connection pools and timeouts.
- Consider read replicas or caching for read-heavy paths.

## Backend services

- Reduce algorithmic complexity on hot paths.
- Batch or debounce expensive operations.
- Add caching with explicit invalidation rules.
- Attach freshness metadata to cached values, so the age of a served value is readable at the point of use rather than inferred from the TTL. Invalidation rules say when a value *becomes* wrong; freshness metadata says how old the value a caller just received actually is.
- Split hot and cold paths, so the latency-critical path carries only the work it needs and everything else moves off it.
- Apply backpressure at the ingress before a queue grows unbounded, rather than scaling the consumer after it already has. Scaling the consumer treats the symptom and raises the cost ceiling; backpressure bounds the failure.
- Remove synchronous I/O or excessive serialization.

## Frontend

- Reduce bundle size and critical path assets.
- Lazy-load non-critical code and media.
- Optimize render cost and avoid layout thrash.
- Use caching headers and CDN-friendly assets.

## Infrastructure

- Right-size instances and set sane resource limits.
- Reduce network hops with locality or edge caching.
- Enable compression where it is safe and useful.
- Validate autoscaling thresholds with load tests.

## Decision points

- If a change impacts user-visible behavior, require a rollout plan and rollback strategy.
- If a fix adds operational complexity, document ownership and monitoring needs.
- If a fix improves latency by serving older data, treat it as a freshness regression until someone accepts the trade explicitly. It is the same family of error as buying latency by dropping required validation: the cost is real, it has just moved to a metric the dashboard is not showing.
- If a cached or streamed path is optimized, add canaries for stale data, degraded upstream providers, and bad cache state. Without them the first signal of a staleness failure is a user reporting wrong numbers on a dashboard that reports healthy latency.

## Outputs

- Proposed fix list with estimated impact and risk.
- Measurement plan for each change.
