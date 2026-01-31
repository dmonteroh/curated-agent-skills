---
name: database-cost-optimization
description: Reduce database-related infrastructure spend safely (instances, storage, replicas, IO) without breaking reliability or performance. Focuses on DB cost drivers, rightsizing, retention/tiering, and cost/perf tradeoffs. Works standalone.
---

# database-cost-optimization

Reduce database spend without making production worse.

## Use this skill when

- Rightsizing database instances and connection pools.
- Reducing storage and backup costs (retention, tiering, compression).
- Evaluating replica counts, HA posture, and cost/perf tradeoffs.
- Identifying expensive query patterns that drive CPU/IO cost.

## Do not use this skill when

- You cannot access any cost/utilization signals and cannot estimate impact.
- The system is in active incident response.

## Context
The user needs to optimize database costs without compromising performance or reliability. Focus on actionable recommendations with measurable savings and explicit risk/rollback.

## Instructions

1) Gather signals (at least one of):
- billing/cost allocation
- DB metrics (CPU/IO/storage/connection counts)
- top queries and query latency

2) Identify top cost drivers:
- compute (CPU/memory class sizing)
- storage + backups
- IO / provisioned throughput
- replicas / HA topology

3) Propose changes with:
- expected savings (range is fine)
- risk assessment (reliability/perf/data loss risk)
- rollback path and verification gates

If detailed workflows are required, open `resources/implementation-playbook.md`.

## Safety

- Validate changes in staging before production rollout.
- Ensure backups and rollback paths before resizing or retention changes.

## Resources

- `resources/implementation-playbook.md` for detailed cost/perf levers and checklists.
