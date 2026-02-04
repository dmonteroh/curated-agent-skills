# Platform Operations and APIs

## Custom Backstage Plugin

Requirements: Backstage frontend project with plugin scaffolding.

```typescript
// plugins/platform-stats/PlatformMetrics.tsx
import React from 'react';
import { InfoCard, Progress } from '@backstage/core-components';

export const PlatformMetrics = () => {
  const metrics = {
    selfServiceRate: 92,
    avgProvisionTime: '3.5min',
    uptime: '99.95%',
    satisfaction: 4.6
  };

  return (
    <InfoCard title="Platform Health">
      <Progress value={metrics.selfServiceRate} label="Self-Service" />
      <p>Provision Time: {metrics.avgProvisionTime}</p>
      <p>Uptime: {metrics.uptime}</p>
      <p>Satisfaction: {metrics.satisfaction}/5</p>
    </InfoCard>
  );
};
```

Verification: render the plugin in a test environment and confirm data wiring.

## Cost Allocation

```yaml
# kubecost/allocation.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cost-allocation
data:
  allocation.json: |
    {
      "defaultLabels": {
        "team": "team",
        "service": "app",
        "environment": "env"
      },
      "shareNamespaces": ["kube-system"],
      "shareCost": "weighted"
    }
```

Verification: confirm allocation reports show the expected labels.

## Platform APIs

```python
# Platform API for self-service provisioning
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ServiceRequest(BaseModel):
    name: str
    environment: str
    language: str
    database: bool = False

@app.post("/api/v1/services")
async def create_service(request: ServiceRequest):
    task = platform.provision_service(
        name=request.name,
        env=request.environment,
        template=f"golden-path-{request.language}"
    )
    return {"task_id": task.id, "status": "provisioning"}

@app.get("/api/v1/services/{name}/status")
async def service_status(name: str):
    return {
        "status": "running",
        "url": f"https://{name}.example.com",
        "health": "healthy",
        "cost_mtd": "$142.50"
    }
```

Verification: run an integration test to ensure provisioning requests complete.

## Multi-Tenant Architecture

```yaml
# Policy: Resource quotas per tenant
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: team-payments
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    persistentvolumeclaims: "10"
    services.loadbalancers: "2"
---
# RBAC: Namespace admin
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: team-admin
  namespace: team-payments
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: namespace-admin
subjects:
  - kind: Group
    name: team-payments
```

Verification: ensure tenant workloads cannot exceed quotas and RBAC access is scoped.

## CLI Tool Example

Requirements: `kubectl`, `curl`, and `jq` installed, plus a configured `PLATFORM_API`.

```bash
#!/bin/bash
# platform-cli - Self-service CLI

platform() {
  case $1 in
    create)
      curl -X POST $PLATFORM_API/services \
        -d "{\"name\":\"$2\",\"env\":\"$3\",\"language\":\"$4\"}"
      ;;
    status)
      curl $PLATFORM_API/services/$2/status | jq
      ;;
    logs)
      kubectl logs -l app=$2 -n ${3:-staging} --tail=100
      ;;
    cost)
      curl $PLATFORM_API/services/$2/cost?period=mtd
      ;;
  esac
}
```

Usage: `platform create payments-service prod nodejs`

Verification: confirm the service shows `running` and logs are accessible.
