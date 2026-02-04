# SLO Review Checklist and Targets

## Review Checklist

1. **User-centric**: Measures user-facing impact.
2. **Achievable**: Feasible with current architecture.
3. **Measurable**: SLI is observable and trustworthy.
4. **Meaningful**: Violations require action.
5. **Documented**: Calculation is clear and agreed upon.
6. **Budgeted**: Error budget policy exists.

## Common Targets

```yaml
tier_1_critical:
  availability: 99.99%
  latency_p99: 100ms

tier_2_important:
  availability: 99.9%
  latency_p99: 500ms

tier_3_standard:
  availability: 99.5%
  latency_p99: 1000ms
```
