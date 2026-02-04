# On-Call Alert Guidelines

```yaml
# on_call_alert_standards.yaml
alert_standards:
  page_worthy:
    - "Immediate user impact (>5% of users affected)"
    - "SLO violation in progress"
    - "Error budget burn rate critical (>10x)"
    - "Security incident"
    - "Data loss risk"

  not_page_worthy:
    - "Predictive alerts without current impact"
    - "Informational metrics"
    - "Non-user-facing issues"
    - "Slow trends (address during business hours)"

  alert_routing:
    critical:
      - page: on-call engineer
      - slack: "#incidents"
      - create: incident doc

    warning:
      - slack: "#alerts"
      - ticket: auto-create if persists >1h

    info:
      - dashboard: only
```
