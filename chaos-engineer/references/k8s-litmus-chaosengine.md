# Litmus ChaosEngine Example

Provides a Litmus ChaosEngine manifest for pod deletion, latency, and CPU hog.

## Prerequisites

- Litmus installed in the cluster.
- Service account `litmus-admin` configured with appropriate RBAC.

## Usage

1. Apply the ChaosEngine manifest in a non-production namespace.
2. Monitor experiment status and guardrails during execution.

## Verification

- Confirm ChaosEngine reaches `Complete` and app pods recover.

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: nginx-chaos
  namespace: default
spec:
  appinfo:
    appns: 'default'
    applabel: 'app=nginx'
    appkind: 'deployment'

  chaosServiceAccount: litmus-admin

  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '60'
            - name: CHAOS_INTERVAL
              value: '10'
            - name: FORCE
              value: 'true'
            - name: PODS_AFFECTED_PERC
              value: '50'

    - name: pod-network-latency
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '60'
            - name: NETWORK_LATENCY
              value: '2000'
            - name: JITTER
              value: '200'
            - name: CONTAINER_RUNTIME
              value: 'containerd'

    - name: pod-cpu-hog
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '60'
            - name: CPU_CORES
              value: '2'
            - name: PODS_AFFECTED_PERC
              value: '50'

  monitoring: true
  jobCleanUpPolicy: 'delete'
```
