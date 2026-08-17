# Pattern: Retention Enforcement

Use this reference to define retention schedules and implement deletion workflows.

## Retention Rule Structure

| Rule ID | Data category | System/Dataset | Retention duration | Deletion mechanism | Legal basis | Owner |
| --- | --- | --- | --- | --- | --- | --- |

## Implementation Approaches

- Time-to-live (TTL) indexes or partition expiration.
- Scheduled deletion jobs with audit logging.
- Event-driven deletion on account closure or contract end.
- Soft-delete followed by hard-delete after a buffer window.
- Irreversible anonymization at end of retention instead of deletion, where the downstream use (typically analytics or aggregate reporting) survives losing the identifiers. This is a valid end-of-retention outcome only if re-identification is genuinely infeasible after the transform — including by joining the result against other data the organization holds. If any re-identification key is kept anywhere, the record is still personal data and the retention rule still applies to it unchanged.

## Exceptions and Holds

- Legal holds, fraud investigations, and statutory recordkeeping.
- Document the exception owner, rationale, and review date.
- Restrict access to held data and block downstream processing.

## Verification Checklist

- Deletion job coverage for all data stores (primary, analytics, archives).
- Evidence of deletion for sampled records.
- Backups and replicas have documented retention timelines.
