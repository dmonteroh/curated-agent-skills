# Pattern: Data Subject Requests (DSAR)

Use this reference when designing or reviewing DSAR workflows, tooling, and evidence capture.

## DSAR Workflow (Access, Erasure, Rectification, Portability)

1) Intake + identity verification
- Output: verified requester record and intake log.

2) Classify request type and scope
- Decision: if scope is unclear, request clarification and pause SLA clock.
- Output: request type, scope, and deadline.

3) Locate data sources
- Output: system list with retrieval/delete methods and owners.

4) Check exceptions and legal holds
- Decision: if legal obligation applies, document retention and restrict processing.
- Output: exception list with reasons and approvals.

5) Execute request actions
- Output: export package or deletion/rectification confirmations per system.

6) Package response and evidence
- Output: response summary, delivery method, audit log, and evidence archive.

## Data Source Inventory Fields

| System | Owner | Data categories | Retrieval method | Deletion method | Exceptions |
| --- | --- | --- | --- | --- | --- |

## Access Export Package Checklist

- Data categories + raw values (where legally permitted)
- Processing purposes and lawful bases
- Retention rules and remaining duration
- Recipients/third parties (if any)
- Request metadata: timestamps, scope, verification method

## Erasure Handling Notes

- Backups: document delayed deletion timelines and access restrictions.
- Shared records: remove identifiers when full deletion is not feasible.
- Legal holds: retain only what is required and log the justification.

## Minimum DSAR Audit Log Fields

| Field | Example |
| --- | --- |
| Request ID | `DSAR-2024-0012` |
| Request type | `access` / `erasure` / `rectification` / `portability` |
| Verified by | `email + MFA` |
| Submitted at | ISO timestamp |
| Deadline | ISO timestamp |
| Status history | `submitted -> processing -> completed` |
| Exceptions | `legal obligation - tax records` |
