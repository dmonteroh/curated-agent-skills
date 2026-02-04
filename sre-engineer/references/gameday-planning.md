# Game Day Planning

```yaml
# gameday_plan.yaml
gameday:
  date: "TBD"
  duration: "2 hours"
  participants:
    - SRE team
    - Backend engineers
    - On-call rotation

  objectives:
    - Test incident response procedures
    - Validate monitoring and alerting
    - Practice communication protocols
    - Identify gaps in runbooks

  scenarios:
    - scenario: "Database Primary Failure"
      inject: "Terminate primary database pod"
      expected: "Automatic failover to replica in <30s"

    - scenario: "API Service Overload"
      inject: "Generate 10x normal traffic"
      expected: "Rate limiting activates, no errors"

    - scenario: "Network Partition"
      inject: "Block traffic between API and database"
      expected: "Circuit breaker opens, graceful degradation"
```
