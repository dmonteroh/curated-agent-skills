# Incident Response Runbook

```yaml
# incident_response.yaml
incident_response:
  detection:
    - "Acknowledge alert in paging system"
    - "Join incident response channel"
    - "Create incident doc from template"
    - "Assess severity (SEV1-4)"

  sev1_response:
    - "Page on-call lead + backup"
    - "Notify leadership immediately"
    - "Start war room"
    - "Assign incident commander"
    - "Assign communication lead"
    - "Post status update every 15 minutes"

  sev2_response:
    - "Page on-call engineer"
    - "Notify team lead"
    - "Create incident channel"
    - "Post status update every 30 minutes"

  roles:
    incident_commander:
      - "Coordinate response efforts"
      - "Make decisions quickly"
      - "Delegate tasks"
      - "Communicate with stakeholders"

    communication_lead:
      - "Post regular status updates"
      - "Notify affected customers"
      - "Update status page"
      - "Summarize timeline"

    on_call_engineer:
      - "Investigate root cause"
      - "Implement fixes"
      - "Verify resolution"
      - "Document actions taken"

  resolution:
    - "Verify metrics returned to normal"
    - "Monitor for 30 minutes"
    - "Post final status update"
    - "Schedule postmortem within 48 hours"
    - "Close incident"
```
