# Deployment Strategy Options

## Strategy Comparison

| Strategy | Use When | Rollback | Risk |
|----------|----------|----------|------|
| **Rolling** | Standard updates, mixed versions acceptable | Automatic via health checks | Low |
| **Blue-Green** | Zero downtime, instant rollback needed | Switch traffic to old env | Medium |
| **Canary** | Risk mitigation, gradual rollout | Scale down canary | Low |
| **Recreate** | Stateful apps, breaking changes | Redeploy previous version | High |

## Rolling Deployment (Kubernetes)

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%        # Max pods above desired
      maxUnavailable: 25%  # Max pods unavailable
```

## Blue-Green with Ingress

```yaml
# Blue deployment (current)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
  labels:
    version: blue
---
# Green deployment (new)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
  labels:
    version: green
---
# Service pointing to active version
apiVersion: v1
kind: Service
metadata:
  name: app
spec:
  selector:
    version: blue  # Switch to 'green' for cutover
```

## Canary with Istio

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app
spec:
  hosts:
    - app
  http:
    - match:
        - headers:
            canary:
              exact: "true"
      route:
        - destination:
            host: app-canary
    - route:
        - destination:
            host: app-stable
          weight: 90
        - destination:
            host: app-canary
          weight: 10
```
