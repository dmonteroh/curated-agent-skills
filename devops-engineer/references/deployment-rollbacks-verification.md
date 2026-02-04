# Deployment Rollbacks and Verification

## Rollback Procedures

### Kubernetes Rollback
Requirements: `kubectl` with access to the target cluster.

```bash
# View rollout history
kubectl rollout history deployment/app

# Rollback to previous
kubectl rollout undo deployment/app

# Rollback to specific revision
kubectl rollout undo deployment/app --to-revision=2

# Check status
kubectl rollout status deployment/app
```

Verification: confirm the rollout completes and health checks return green.

### ArgoCD Rollback
Requirements: `argocd` CLI authenticated to the ArgoCD instance.

```bash
argocd app rollback app-prod --revision=123
```

Verification: `argocd app get app-prod` shows a healthy sync status.

### Terraform Rollback
Requirements: `terraform` and access to the state backend.

```bash
# Identify previous state
terraform state list

# Restore previous configuration and apply
git checkout HEAD~1 -- main.tf
terraform apply
```

Verification: validate state drift is resolved and critical services are healthy.

## Pre-deployment Checklist

- [ ] Database migrations are backward compatible
- [ ] Feature flags for new functionality
- [ ] Monitoring dashboards updated
- [ ] Alert thresholds reviewed
- [ ] Rollback procedure documented
- [ ] Staging tested and approved
- [ ] Team notified of deployment window

## Post-deployment Verification

Requirements: `kubectl`, `curl`, and access to logs/metrics.

```bash
# Check pod status
kubectl get pods -l app=app

# Check logs for errors
kubectl logs -l app=app --tail=100 | grep -i error

# Verify endpoints
curl -f https://app.example.com/health
```

Verification: validate error rate, latency, and resource utilization against the agreed SLOs.
