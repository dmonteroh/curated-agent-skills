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

## Concurrency control

- Can two writers touch the same entity at the same time? If they cannot, record that and move on.
- Where they can, choose optimistic or pessimistic control deliberately, and put the choice in the schema rather than leaving it to application code that a second caller can bypass.

Optimistic control, expressed as schema: give each entity a monotonically increasing `version`, have the writer read the current version, and write at the version it expects to produce. A `UNIQUE (entity_id, version)` constraint makes the database the arbiter — two writers that read the same version both attempt the same pair, and exactly one commits.

```sql
CREATE TABLE order_events (
  event_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id    UUID        NOT NULL,
  version     BIGINT      NOT NULL,
  payload     JSONB       NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT order_events_version_unique UNIQUE (order_id, version)
);
```

The write path: read the current maximum version for the entity, compare it against the version the caller expected, insert at `expected + 1`. The loser of a race gets a constraint violation, not a lost update, and either retries against the new state or surfaces the conflict to its caller. Decide which of those two it is at design time — a silent retry loop on a conflict that represents a genuine business collision hides the collision.

This generalizes past event streams to any append-only or versioned entity table (document revisions, ledger entries, audit rows), and needs no external lock service or advisory lock.

Verification: run two writers concurrently from the same expected version against a test table. Exactly one insert must fail. If both succeed, the constraint is missing or is declared on the wrong columns.

## Lifecycle

- Retention rules, archival, soft delete vs hard delete.
- GDPR and compliance implications.

