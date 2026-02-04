# Feature Flags and Progressive Delivery

## LaunchDarkly Integration

Requirements: LaunchDarkly SDK configured in the application.

```python
import launchdarkly

ld = launchdarkly.get()

def should_enable(user_id, feature_key):
    user = {"key": user_id, "custom": {"groups": get_groups(user_id)}}
    return ld.variation(feature_key, user, False)

# Usage
if should_enable(user.id, "new-payment-flow"):
    return new_payment_service.process(payment)
else:
    return legacy_payment_service.process(payment)
```

Verification: confirm the flag toggles behavior in a staging environment.

## Flagger Progressive Delivery

Requirements: Flagger installed with access to metrics and service mesh routing.

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: payment-service
spec:
  targetRef:
    kind: Deployment
    name: payment-service
  service:
    port: 8080
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
      - name: request-success-rate
        thresholdRange:
          min: 99
      - name: request-duration
        thresholdRange:
          max: 500
    webhooks:
      - name: load-test
        url: http://flagger-loadtester/
        metadata:
          cmd: "hey -z 1m -q 10 http://payment-canary/"
```

Verification: watch the canary rollout and confirm rollback on metric regression.
