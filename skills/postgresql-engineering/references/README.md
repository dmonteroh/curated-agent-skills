# References Index

## PostgreSQL Engineering

- `playbook.md`: Detailed Postgres guidance on data types, constraints, indexing, JSONB, partitioning, and safe schema evolution, plus examples.
- `indexing-and-constraints.md`: Index-type taxonomy, composite column ordering, `EXCLUDE`/`DEFERRABLE`/`NULLS NOT DISTINCT` constraints, schema-enforced optimistic concurrency (`UNIQUE (entity_id, version)`), and a query listing unindexed foreign keys.
- `storage-and-workload.md`: Regular/`TEMPORARY`/`UNLOGGED` table choice, TOAST storage strategies, and update-heavy vs insert-heavy tactics.
- `extensions.md`: Which extension answers which requirement, and what it costs to depend on one.
