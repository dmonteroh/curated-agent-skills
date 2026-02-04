# Modeling Checklist

## Invariants

- What must be unique?
- What must exist before something else can exist?
- What must never be deleted (audit/ledger needs)?

## Keys

- Stable primary key choice per entity.
- Natural key vs surrogate key: decide and document why.

## Relationships

- Where do we enforce referential integrity?
- If we skip FKs, what is the compensating control (tests, jobs, constraints)?

## Indexing

- Identify the top queries and access paths.
- Index join keys and frequent filters/sorts.
- Avoid speculative indexes until you have evidence.

## Lifecycle

- Retention rules, archival, soft delete vs hard delete.
- GDPR and compliance implications.

