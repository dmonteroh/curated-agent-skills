# Capacity Planning: Scaling Strategies

Use this reference for capacity calculations and autoscaling configuration examples.

## Horizontal Scaling Calculator

```javascript
function calculateInstances(targetRPS, instanceCapacity, bufferPercent = 20) {
  // Account for buffer
  const effectiveCapacity = instanceCapacity * (1 - bufferPercent / 100);

  // Calculate required instances
  const requiredInstances = Math.ceil(targetRPS / effectiveCapacity);

  // Account for availability zones
  const minInstancesPerAZ = 2;
  const zones = 3;
  const minTotal = minInstancesPerAZ * zones;

  return Math.max(requiredInstances, minTotal);
}

console.log(calculateInstances(5000, 1000));  // 7 instances
```

## Auto-scaling Configuration

### Kubernetes HPA

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
        - type: Pods
          value: 4
          periodSeconds: 30
      selectPolicy: Max
```

### AWS Auto Scaling

```json
{
  "AutoScalingGroupName": "app-asg",
  "MinSize": 3,
  "MaxSize": 20,
  "DesiredCapacity": 5,
  "TargetTrackingScalingPolicies": [
    {
      "TargetValue": 70.0,
      "PredefinedMetricSpecification": {
        "PredefinedMetricType": "ASGAverageCPUUtilization"
      },
      "ScaleInCooldown": 300,
      "ScaleOutCooldown": 60
    },
    {
      "TargetValue": 1000.0,
      "CustomizedMetricSpecification": {
        "MetricName": "RequestCountPerTarget",
        "Namespace": "AWS/ApplicationELB",
        "Statistic": "Sum"
      }
    }
  ]
}
```
