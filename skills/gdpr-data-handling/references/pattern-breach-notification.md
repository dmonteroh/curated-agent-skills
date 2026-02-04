# Pattern: Breach Notification

Use this reference to design incident workflows for personal data breaches.

## Triage Data Points

- What happened and when.
- Data categories affected (including special categories).
- Approximate number of data subjects.
- Ongoing risk of access or exfiltration.

## Notification Workflow

- Notify security and privacy owners immediately.
- Assess whether supervisory authority notification is required within 72 hours.
- If high risk to individuals, plan data subject notification with clear guidance.

## Evidence and Documentation

- Preserve relevant logs, alerts, and forensics snapshots.
- Record decisions, timelines, and mitigation steps.

## Minimum Breach Record Fields

| Field | Example |
| --- | --- |
| Incident ID | `BREACH-2024-004` |
| Detected at | ISO timestamp |
| Summary | `Unauthorized access to support tool` |
| Data categories | `contact info`, `account IDs` |
| Estimated subjects | Numeric estimate |
| Notification decision | `notify authority` / `no notification` |
| Mitigations | `revoked tokens`, `patched system` |
