# Technology Selection (Compact)

Pick the simplest thing that satisfies invariants and access patterns.

## Questions that decide the tech

- Are invariants strong and relational? (joins, constraints) -> relational DB.
- Is the workload primarily append + time range queries? -> time-series/partitioning.
- Is the main requirement fast full-text search? -> search engine (with source of truth elsewhere).
- Is low-latency key lookup the primary need? -> key-value (often as cache/secondary store).

## Operational tradeoffs to surface

- How hard is backup/restore/PITR?
- How do we do migrations safely?
- How do we handle multi-region/DR?
- How do we observe performance and capacity?

