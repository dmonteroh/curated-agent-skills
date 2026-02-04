# Game Day Report Template

Provides a post-game report template.

## Usage

1. Populate metrics with actual values.
2. Capture action items with owners and due dates.
3. Store the report with artifacts and timelines.

## Verification

- Confirm action items include owners and priorities.
- Attach evidence for metrics and observations.

```markdown
# Game Day Report: Database Failover

**Date**: YYYY-MM-DD
**Participants**: 12
**Duration**: 2 hours
**Environment**: Staging

## Executive Summary

Ran a database failover game day to test high availability and application
resilience. Failover completed in 2.5 minutes (target: 2 min). Monitoring
gaps and process improvements were identified.

## Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Time to Detect | < 30s | 15s | PASS |
| Time to Respond | < 5min | 4min 20s | PASS |
| Time to Recover | < 2min | 2min 30s | FAIL |
| Alert Accuracy | 100% | 66% | FAIL |
| Zero Customer Impact | Yes | Yes | PASS |

## What Went Well

1. Response time met the target.
2. Runbooks were accurate and helpful.
3. Communication was clear and frequent.
4. No customer impact during any scenario.
5. Application auto-reconnect worked as expected.

## What Did Not Go Well

1. Missing alert for failover initiation.
2. Recovery exceeded target by 30s.
3. Connection pool exhaustion was not detected.
4. Dashboard lacked replica lag visibility.
5. Escalation contacts list was outdated.

## Surprises

1. Cache invalidation cascaded from DB failover.
2. Read replica had 45s replication lag.
3. Retry behavior was too aggressive during failover.
4. An undocumented workaround was used.

## Action Items

| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
| Add alert for RDS failover events | @sre-team | T+7d | P0 |
| Update dashboard with replica lag | @platform | T+9d | P1 |
| Document cache invalidation behavior | @dev-team | T+12d | P1 |
| Add connection pool monitoring | @sre-team | T+14d | P0 |
| Update escalation contact list | @manager | T+5d | P2 |
| Tune application retry backoff | @dev-team | T+19d | P1 |

## Lessons Learned

1. Monitoring gaps remain in replica visibility.
2. Cascading effects from DB changes require explicit tests.
3. Cross-training reduces response friction.
4. Runbooks need continuous updates.

## Next Game Day

**Proposed Date**: YYYY-MM-DD
**Scenario**: Multi-region failover
**Scope**: Production (with safeguards)

## Appendix

- Full timeline spreadsheet: [link]
- Screen recordings: [link]
- Metrics dashboard export: [link]
- Raw observation notes: [link]
```
