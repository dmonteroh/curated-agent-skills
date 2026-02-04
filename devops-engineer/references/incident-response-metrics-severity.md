# Incident Response Metrics and Severity

## Response Metrics

- **MTTD** (Mean Time to Detect)
- **MTTA** (Mean Time to Acknowledge)
- **MTTR** (Mean Time to Resolve)
- **MTBF** (Mean Time Between Failures)

Use these as baselines and align targets with service SLOs and on-call capacity.

## Severity Levels

| Level | Impact | Response | Example |
|-------|--------|----------|---------|
| SEV1 | Complete outage | Immediate | Database down, payment failed |
| SEV2 | Major degradation | 15 min | API latency >5s, 50% errors |
| SEV3 | Minor degradation | 1 hour | Non-critical feature broken |
| SEV4 | Low impact | Business hours | UI glitch, logging issues |
