# Levers and Risk Tiers

Map levers to cost drivers and classify risk.

## Compute

- Low risk: reduce idle connections; tune pool size to avoid forced scaling.
- Medium risk: downsize instance class with utilization headroom.
- High risk: change engine or major version for cost reasons.

## Storage and backups

- Low risk: prune obsolete snapshots within recovery policy.
- Medium risk: adjust retention/tiering with documented recovery sign-off.
- High risk: migrate storage class with unknown latency characteristics.

## IO and query cost

- Low risk: add missing indexes after measuring write overhead.
- Medium risk: rewrite expensive queries, validate p95 latency improvements.
- High risk: structural schema changes solely for cost.

## Replicas and HA

- Low risk: consolidate idle read replicas if read load permits.
- Medium risk: reduce replica count with explicit RPO/RTO approval.
- High risk: change HA topology or failover strategy.
