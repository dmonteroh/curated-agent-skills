# SQL migration implementation playbook

Provides a concise checklist for planning and executing forward-only SQL migrations with minimal downtime. Use this playbook as a quick companion to the references.

## Scope

- Forward-only SQL migrations for PostgreSQL, MySQL, or SQL Server.
- Expand/contract patterns, safe backfills, and online index changes.
- Validation and rollback planning for production safety.

## Required inputs

- Engine and version.
- Migration runner and naming convention.
- Lock tolerance and maintenance window constraints.
- Estimated data volume and high-traffic tables.
- Rollback expectations (forward-only vs reversible).

## Workflow checklist

1) **Confirm constraints**
   - Capture engine/version, lock tolerance, and data size.
   - Identify any DDL limits (transactional DDL support, online index options).
2) **Select strategy (decision point)**
   - If large/high-traffic: expand/contract or blue/green.
   - If low risk: transactional DDL where supported.
3) **Draft migration SQL**
   - Split expand/contract into separate files.
   - Avoid concurrent index builds inside transactions.
4) **Plan backfill (decision point)**
   - Batch updates with a deterministic cursor.
   - Throttle between batches and track progress.
5) **Define validation queries**
   - Row counts, null checks, uniqueness checks, constraint validation.
6) **Document rollback plan**
   - Mark irreversible steps as forward-only.
   - Provide safe rollback SQL for additive changes.
7) **Execution checklist**
   - Verify prechecks, run migration, validate, monitor, and complete contract phase.

## Common pitfalls

- Running blocking DDL without checking lock behavior.
- Mixing concurrent index builds with transactions.
- Backfilling without batch sizing or throttling.
- Skipping validation queries or documenting rollback assumptions.

## Reference index

- `references/README.md` for detailed patterns, templates, and examples.
