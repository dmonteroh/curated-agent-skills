## Deployment Strategies

This reference was split into smaller, purpose-built files:

- `deployment-strategy-options.md`
- `deployment-rollbacks-verification.md`
- `deployment-metrics-canary.md`
      - name: acceptance-test
        type: pre-rollout
        url: http://test-runner/
      - name: load-test
        url: http://loadtester/
        timeout: 5s
        metadata:
          type: bash
          cmd: "hey -z 1m -q 10 http://api-canary:8080/"
```

## Shadow Deployment

```yaml
# Mirror traffic to shadow deployment
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api
spec:
  hosts:
    - api
  http:
    - match:
        - headers:
            x-test-version:
              exact: "v2"
      route:
        - destination:
            host: api
            subset: v2
      mirror:
        host: api
        subset: v2-shadow
      mirrorPercentage:
        value: 100
    - route:
        - destination:
            host: api
            subset: v1
```
