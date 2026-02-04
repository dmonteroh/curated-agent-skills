# Incident Runbooks and Postmortems

## Runbook Template

```markdown
# Runbook: High API Error Rate

## Symptoms
- Alert: `api_error_rate > 0.05`
- Dashboard: https://grafana.example.com/d/api-errors

## Impact
Users cannot complete purchases (~$X per minute)

## Triage
1. Check dashboard for affected endpoints
2. Check recent deployments: `kubectl rollout history deployment/api`
3. Check dependencies: database, redis, external APIs

## Resolution

### Option 1: Rollback
kubectl rollout undo deployment/api -n production

### Option 2: Scale Up
kubectl scale deployment/api --replicas=10 -n production

### Option 3: Fix Config
kubectl set env deployment/api DB_POOL_SIZE=50 -n production

## Verification
- [ ] Error rate <1%
- [ ] P95 latency <500ms
- [ ] Health checks passing

## Communication
- Update status page
- Notify #incidents
- Post if user-facing
```

Requirements: `kubectl` access to the target cluster.

Verification: confirm the runbook steps stabilize the error rate and latency.

## Postmortem Template

```markdown
# Postmortem: API Outage - YYYY-MM-DD

**Date**: YYYY-MM-DD
**Duration**: HH:MM (UTC)
**Severity**: SEV1
**Impact**: Summary of user/business impact

## Summary
Short description of what failed and why.

## Timeline (UTC)
- HH:MM - Alert fired
- HH:MM - Incident declared SEV1
- HH:MM - Rollback initiated
- HH:MM - Root cause identified
- HH:MM - Mitigation applied
- HH:MM - Resolved

## Root Cause
Explain the primary contributing factor(s).

## Impact
- % of requests affected
- Number of users affected
- Key business impact

## Action Items
| Action | Owner | Due Date |
|--------|-------|----------|
| Example action | Team | YYYY-MM-DD |

## Lessons Learned
- What worked well
- What needs improvement
```
