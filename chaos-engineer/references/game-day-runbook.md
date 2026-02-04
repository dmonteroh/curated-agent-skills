# Game Day Runbook Template

Provides a step-by-step runbook for executing a game day exercise.

## Usage

1. Replace scenario details with the planned game day steps.
2. Assign observers and responders to each scenario.
3. Use the checklist during execution to capture timing and decisions.

## Verification

- Confirm the environment is healthy before starting.
- Validate rollback commands are accessible.
- Ensure observers capture timestamps and outcomes.

```markdown
# Database Failover Game Day Runbook

**Date**: YYYY-MM-DD
**Duration**: 2 hours
**Environment**: Staging

## Pre-Game Checklist (T-30 min)

- [ ] Verify all participants joined war room
- [ ] Confirm monitoring dashboards accessible
- [ ] Test rollback procedures work
- [ ] Announce game day start in #engineering
- [ ] Verify staging environment healthy
- [ ] Set up screen recording for timeline
- [ ] Prepare incident timeline spreadsheet

## Timeline

### T+0 - Introduction (10 min)
- Facilitator explains objectives
- Review scenarios and success criteria
- Confirm roles and communication channels
- Remind everyone: this is a learning exercise

### T+10m - Scenario 1: Primary DB Failure (30 min)

**T+0** - Inject failure
```bash
aws rds reboot-db-instance \
  --db-instance-identifier staging-primary \
  --force-failover
```

**Expected Timeline**:
- T+0: Reboot initiated
- T+30s: Primary becomes unavailable
- T+60s: DNS updated to standby
- T+90s: Application reconnects
- T+120s: Full recovery

**Observer Tasks**:
- [ ] Record exact time of failure injection
- [ ] Monitor application error logs
- [ ] Track alert notifications
- [ ] Document team response actions
- [ ] Screenshot dashboard states

**Questions to Answer**:
- How long until first alert?
- Did application auto-reconnect?
- Were customers impacted?
- What manual interventions needed?

### T+40m - Debrief Scenario 1 (10 min)
- What went well?
- What could improve?
- Any surprises?
- Action items identified

### T+50m - Scenario 2: Network Partition (20 min)

**T+0** - Inject failure
```bash
# Block database security group ingress
aws ec2 revoke-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 5432 \
  --cidr 10.0.0.0/16
```

**Expected Behavior**:
- Connection timeouts occur
- Circuit breaker opens
- Read-only mode activates
- Clear error messages shown

**Observer Tasks**:
- [ ] Monitor circuit breaker state
- [ ] Verify read-replica failover
- [ ] Check user-facing error messages
- [ ] Track degraded service duration

### T+70m - Debrief Scenario 2 (10 min)

### T+80m - Scenario 3: Surprise! (20 min)

**Facilitator Note**: Don't announce this scenario details beforehand.
Test true incident response capability.

**Hidden Scenario**: Combination failure
1. Database connection pool leak
2. Simultaneous cache invalidation

```python
# Connection leak simulator
import psycopg2
connections = []
for i in range(100):
    conn = psycopg2.connect(DATABASE_URL)
    connections.append(conn)
```

**Observer Tasks**:
- [ ] How long to identify root cause?
- [ ] Communication effectiveness
- [ ] Cross-team coordination
- [ ] Escalation decisions

### T+100m - Final Debrief & Wrap-up (20 min)

**Debrief Questions**:
1. What worked well?
2. What didn't work?
3. What surprised us?
4. What are our top 3 action items?
5. When should we run this again?

## Post-Game Checklist

- [ ] Restore all services to normal state
- [ ] Verify no lingering issues
- [ ] Collect all observer notes
- [ ] Export metrics and dashboards
- [ ] Schedule post-mortem meeting
- [ ] Send thank-you to participants
- [ ] Create action item tickets
- [ ] Update runbooks based on learnings
```
