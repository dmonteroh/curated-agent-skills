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

## Outputs

- Proposed fix list with estimated impact and risk.
- Measurement plan for each change.
