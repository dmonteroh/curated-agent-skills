# GDPR Templates (Engineer-Friendly)

These templates are meant to be created/updated as living docs (ideally in `docs/privacy/` or your repo convention).

## 1) Data Inventory Template

```md
# Data Inventory

## Systems

| System | Owner | Purpose(s) | Environments | Data residency | Notes |
| --- | --- | --- | --- | --- | --- |

## Datasets

| Dataset | System | Contains (high level) | Data subjects | Lawful basis | Retention | Sharing/Recipients | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Field-level (optional)

| Field | Dataset | Category | Sensitive? | Source | Used for | Shared? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

## 2) DSAR Runbook Template

```md
# DSAR Runbook

## Scope

- In scope:
- Out of scope:

## Identity Verification

- Allowed verification methods:
- Reject/hold conditions:

## Request Types

- Access/export
- Rectification
- Erasure
- Restriction
- Objection

## Timelines

- Standard response deadline:
- Extension criteria and how to notify:

## Execution Steps (generic)

1) Intake + verify identity
2) Locate data across systems
3) Apply policy checks (legal holds, contractual obligations)
4) Execute (export/update/delete/restrict)
5) Verify completion + evidence
6) Respond to requester

## Evidence & Audit

- What to log:
- Where to store evidence:

## Edge Cases

- Multi-tenant systems:
- Linked accounts / shared devices:
- Data in backups:
```

## 3) Retention Schedule Template

```md
# Retention Schedule

| Data category | System/Dataset | Retention | Deletion mechanism | Legal basis / reason | Exceptions (legal hold, audit, etc.) |
| --- | --- | --- | --- | --- | --- |
```

## 4) Processor / Transfer Notes Template

```md
# Processors and Transfers (Notes)

| Vendor | Role (processor/subprocessor) | Data accessed | Purpose | Regions | Transfer mechanism notes | Contract/DPA location | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

## 5) Breach Readiness Runbook Template

```md
# Personal Data Breach Runbook

## Detection Signals

- Alerts/logs:
- User reports:

## Triage

- What happened?
- What data categories?
- How many subjects?
- Ongoing access/exfiltration risk?

## Containment

- Immediate steps:

## Notification Workflow

- Who decides notification?
- Who drafts notifications?
- Regulator notification timeline:
- Data subject notification criteria:

## Evidence Preservation

- Logs to preserve:
- Snapshots:
- Forensics:

## Post-incident

- Root cause:
- Remediations:
- Follow-up controls:
```

