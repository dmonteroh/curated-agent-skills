---
name: database-cost-optimization
description: Reduce database infrastructure spend safely by analyzing cost drivers, right-sizing compute/storage/replicas, and proposing verified rollback-ready changes without compromising reliability.
category: database
---

# database-cost-optimization

Reduce database spend while keeping performance and reliability intact.

## Use this skill when

- Right-sizing database instances, storage, or connection pools.
- Reducing backup/retention costs with clear recovery requirements.
- Evaluating read replicas, HA posture, or IO provisioning costs.
- Investigating costly queries driving CPU or IO spend.

## Do not use this skill when

- The system is in active incident response.
- No cost or utilization signals are available and none can be estimated.

## Trigger phrases

- "reduce database cost"
- "rightsize the database"
- "cut storage or backup spend"
- "too many replicas"
- "high database IO cost"

## Required inputs

- Database engine and deployment model (managed/self-hosted, region).
- Current topology (primary/replicas, storage class, backup retention).
- At least one signal: cost allocation, utilization metrics, or query profile.
- Reliability requirements (RPO/RTO, HA/SLA, peak windows).

If any required inputs are missing, ask for them before proceeding.

## Workflow

1) Confirm goals and constraints.
   - Output: target savings range, non-negotiable reliability constraints.

2) Build a baseline from available signals.
   - Output: baseline table with cost, utilization, storage growth, and peak load.
   - Decision: if baseline data is insufficient to estimate impact, request more data and pause.

3) Identify primary cost drivers.
   - Output: ranked list of compute, storage, IO, and replica drivers with evidence.

4) Generate candidate levers by risk tier.
   - Output: low/medium/high-risk candidate actions tied to a driver.
   - Decision: if a lever affects RPO/RTO or peak traffic, mark as high-risk and require rollout gating.

5) Estimate savings and risk for each lever.
   - Output: savings range, assumptions, and risk classification per change.

6) Define rollout and verification gates.
   - Output: staged rollout plan, metrics to watch, rollback criteria.

7) Deliver the final report.
   - Output: recommendations with savings, risks, and verification steps.

## Common pitfalls

- Downscaling without validating peak utilization and burst patterns.
- Reducing retention without mapping legal or recovery requirements.
- Removing replicas without confirming read traffic and failover needs.
- Optimizing queries without verifying index/storage impact.

## Examples

**Trigger test**
- "We need to cut our Postgres costs by 20% without risking latency."
- "Our database storage bill is exploding; help reduce it safely."

**Example output (excerpt)**
```
DB Cost Optimization Report
Baseline: $18.2k/mo, CPU p95 42%, storage +9%/mo
Top drivers: oversized primary, unused read replica, long retention
Recommendation 1: downsize primary (savings $2.5k–$3.2k, medium risk)
Verification: canary 10%, watch p95 latency < 50ms, rollback if > 65ms
```

## Output contract

Provide a report with these sections and keep the format consistent:

```
DB Cost Optimization Report

Context:
- Goal:
- Constraints:

Baseline:
- Monthly cost:
- Utilization summary:
- Storage growth:
- Peak window:

Cost Drivers (ranked):
- Driver: evidence

Recommendations:
1) Change:
   Driver:
   Expected savings (range):
   Risk level:
   Verification gates:
   Rollback plan:
   Assumptions:

Open Questions:
- ...

Next Steps:
- ...
```

## References

See `references/README.md` for detailed checklists and lever guidance.
