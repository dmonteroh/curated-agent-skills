# Alert Runbook Template

Every alert must link to a runbook with clear remediation steps.

```markdown
# Runbook: Error Budget Burn Rate

## Alert: ErrorBudgetBurnRateFast

### Description
The service is consuming error budget faster than sustainable rate.
At current rate, the 30-day error budget will be exhausted within 2 days.

### Severity: Critical

### Impact
- Users experiencing elevated error rates
- Risk of SLO violation and feature freeze
- Potential customer impact

### Triage Steps

1. **Check current error rate**
   ```promql
   rate(http_requests_total{status=~"5..", service="api"}[5m])
   ```

2. **Identify error types**
   ```bash
   kubectl logs -l app=api --tail=100 | grep ERROR
   ```

3. **Check recent deployments**
   ```bash
   kubectl rollout history deployment/api
   ```

4. **Review dependencies**
   - Database health
   - External API status
   - Infrastructure issues

### Remediation

**If caused by recent deployment:**
```bash
kubectl rollout undo deployment/api
kubectl rollout status deployment/api
```

**If database issue:**
```bash
kubectl exec -it postgres-0 -- psql -c "SELECT count(*) FROM pg_stat_activity;"
kubectl exec -it postgres-0 -- psql -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

**If traffic spike:**
```bash
kubectl scale deployment/api --replicas=10
kubectl apply -f rate-limit-config.yaml
```

### Communication

**Slack template:**
```
:fire: INCIDENT: Error budget burn rate critical

Service: api
Error rate: [X]%
Impact: [describe user impact]
ETA: [when will it be resolved]

Incident doc: [link]
```

### Prevention
- Add integration tests for this failure mode
- Implement circuit breaker for external dependencies
- Add capacity planning for traffic spikes
```
