# Resilience Drills and Forensics

## Chaos Engineering

Requirements: Chaos Mesh installed and RBAC permissions to run experiments.

```yaml
# chaos-mesh: Pod failure test
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-failure-test
spec:
  action: pod-failure
  mode: one
  duration: "30s"
  selector:
    namespaces: [production]
    labelSelectors:
      app: api
  scheduler:
    cron: "@every 2h"
```

Verification: validate alerting fires and workloads recover within the expected window.

### Game Day Drill

Requirements: `kubectl`, `curl`, and access to incident channels.

```bash
#!/bin/bash
# Game Day: Database failover drill

echo "Game Day: Database failover"
slack-cli -d incidents "Starting failover drill"

# Simulate failure
kubectl delete pod postgres-0 -n production

# Monitor recovery
start=$(date +%s)
while ! kubectl get pod postgres-1 | grep Running; do
  sleep 5
done
duration=$(($(date +%s) - start))

echo "Failover: ${duration}s" >> results.md
curl -f https://api.example.com/health || echo "FAIL"
```

Verification: confirm failover completes and health checks return OK.

## Evidence Collection & Forensics

Requirements: `kubectl`, `git`, `psql`, and adequate permissions for logs and exec.

```bash
#!/bin/bash
# collect-evidence.sh - Preserve incident evidence

INCIDENT_ID=$1
EVIDENCE_DIR="incidents/${INCIDENT_ID}/evidence"
mkdir -p $EVIDENCE_DIR

# Preserve logs
kubectl logs -l app=api --all-containers --timestamps \
  --since=2h > $EVIDENCE_DIR/pod-logs.txt

# Capture current state
kubectl get all -n production -o yaml > $EVIDENCE_DIR/k8s-state.yaml
kubectl describe pods -n production > $EVIDENCE_DIR/pod-details.txt

# Network traces
kubectl exec -n production deploy/api -- \
  tcpdump -i any -w /tmp/capture.pcap -G 60 -W 5 &

# Memory/CPU snapshot
kubectl top pods -n production > $EVIDENCE_DIR/resource-usage.txt

# Git commit at time of incident
git log --since="2 hours ago" --oneline > $EVIDENCE_DIR/recent-commits.txt

# Database queries
psql -c "SELECT * FROM pg_stat_activity" > $EVIDENCE_DIR/db-activity.txt
```

Usage: run `./collect-evidence.sh INCIDENT-123` immediately after stabilizing service.

Verification: ensure artifacts are collected and stored in the incident record.
