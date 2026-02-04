# Error Budget Policy Template

```yaml
# error_budget_policy.yaml
service: payment-api
slo:
  target: 99.9%
  measurement_window: 30 days

policy:
  actions:
    - threshold: 100%
      state: normal_operations
      actions:
        - "Continue feature development"
        - "Deploy during business hours"
        - "Standard change review process"

    - threshold: 50%
      state: careful_operations
      actions:
        - "Increase code review rigor"
        - "Require senior engineer approval for deploys"
        - "Conduct pre-deployment risk assessment"
        - "Enhanced monitoring during deploys"

    - threshold: 25%
      state: restricted_operations
      actions:
        - "Halt non-critical feature work"
        - "Focus on reliability improvements"
        - "Require leadership approval for deployments"
        - "Deploy only critical bug fixes"
        - "Daily error budget review meetings"

    - threshold: 0%
      state: feature_freeze
      actions:
        - "Immediate feature freeze"
        - "Deploy only emergency fixes"
        - "All hands reliability review"
        - "Mandatory postmortem for all incidents"
        - "Weekly executive review until recovered"

  exceptions:
    - type: security_patch
      approval: security_team
      allowed: true

    - type: critical_business_requirement
      approval: leadership + product_lead
      allowed: true
      requires_review: true
```
