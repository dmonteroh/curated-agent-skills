# Surprise Scenarios Library

Provides a library of surprise scenarios for game days.

## Usage

1. Select one or more scenarios and keep details private until execution.
2. Align each scenario to clear learning goals.

## Verification

- Confirm each scenario has rollback triggers and an observer plan.

```yaml
surprise_scenarios:
  - name: "Cascading Failure"
    description: "Primary failure triggers secondary issue"
    injection:
      - "Database failover (expected)"
      - "Cache eviction due to new primary IP (surprise)"
    learning_goals:
      - "Dependency awareness"
      - "Handling simultaneous issues"

  - name: "Monitoring Blind Spot"
    description: "Failure does not trigger alerts"
    injection:
      - "Gradual connection pool leak"
      - "No immediate alerts fire"
    learning_goals:
      - "Issue discovery without alerts"
      - "Monitoring coverage gaps"

  - name: "Documentation Failure"
    description: "Runbook is outdated or incorrect"
    setup:
      - "Modify runbook to have incorrect commands"
      - "Or remove runbook entirely"
    learning_goals:
      - "Problem-solving without docs"
      - "Documentation update speed"

  - name: "Key Person Unavailable"
    description: "Subject matter expert is unreachable"
    setup:
      - "Ask SME to not respond for 15 minutes"
    learning_goals:
      - "Knowledge distribution"
      - "Operating without specific individuals"

  - name: "Partial Degradation"
    description: "Service works but slowly"
    injection:
      - "Add 5 second latency instead of complete failure"
    learning_goals:
      - "Performance degradation detection"
      - "Latency SLO validation"
```
