# Assessment Checklist

Use this checklist to build a baseline before proposing changes.

## Cost baseline

- Monthly database spend (current and prior month if available).
- Cost allocation labels/tags or account attribution.
- Any committed-use discounts or reserved instances already applied.

## Utilization baseline

- CPU and memory percentiles (p50/p95) with peak windows.
- IO metrics (IOPS, latency, throughput) and storage growth rate.
- Connection counts and pool configuration.
- Top queries by total time and by mean latency.

## Reliability requirements

- RPO/RTO expectations.
- Required number of replicas or read throughput targets.
- Backup retention and legal/regulatory constraints.
