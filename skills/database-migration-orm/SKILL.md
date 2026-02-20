---
name: database-migration-orm
description: "Plan and execute ORM-managed database migrations (Prisma/TypeORM/Sequelize/EF) with zero-downtime patterns, safe backfills, and rollback discipline. Use only for ORM migration tooling (not raw SQL-file migration workflows)."
metadata:
  category: database
---
# Database Migration (ORM)

Scope: ORM-driven migrations only. For raw SQL migration workflows, use a separate raw SQL migration process.

## Use this skill when

- Creating or reviewing ORM migrations (schema + data transforms)
- Planning safe, staged rollouts (expand/contract) with backfills
- Debugging migration failures, drift, or inconsistent environments

## Do not use this skill when

- The project uses forward-only SQL migration files as the primary mechanism
- The task is only query tuning or general performance analysis

## Required inputs

- ORM tool and version, plus migration runner constraints
- Database engine/version and online DDL capabilities
- Change type (schema only, data backfill, or mixed)
- Data volume and acceptable lock/downtime window
- Deployment model (single app, multi-service, version skew tolerance)
- Rollback tolerance and irreversible operations (if any)

## Workflow (Deterministic)

1) Confirm context and constraints
- Capture ORM tool, DB engine/version, change type, and downtime limits.
- Output: a one-paragraph migration context summary.

2) Select rollout strategy (decision points)
- If zero-downtime is required, use expand/contract with backward compatibility.
- If data backfill is large, run a batched job outside the migration runner.
- If the change is irreversible, flag it as forward-only.
- Output: strategy outline with explicit gates and decision rationale.

3) Draft migration artifacts
- Define schema changes (expand step) and data backfill mechanics.
- Specify application read/write toggles or dual-write windows.
- Output: artifact list (migration files, backfill job plan, app toggle steps).

4) Safety checks and rollback plan
- Analyze locks, timeouts, long transactions, and migration ordering.
- Describe rollback/repair steps for each stage and what is not reversible.
- Output: rollback matrix with reversible vs forward-only items.

5) Verification and runbook
- Rehearse on staging or production-like datasets when possible.
- Track backfill progress, error rates, and schema drift checks.
- Output: verification checklist + runbook steps for production execution.

## Common pitfalls

- Running large backfills inside a single migration transaction
- Dropping columns before all services stop using them
- Missing backward compatibility during rollout (reads/writes)
- Adding default values that rewrite large tables without planning
- Skipping rollback clarity for forward-only operations

## Output Contract (Always)

- Migration context summary (ORM, DB, constraints)
- Rollout strategy (expand/backfill/contract with gates)
- Artifact list (migrations, backfill job, app toggle steps)
- Rollback matrix (reversible vs forward-only)
- Verification checklist (tests, rehearsal, monitoring)

## Reporting Format (Use This)

1. **Migration Context**
2. **Strategy & Decision Points**
3. **Artifacts & Execution Steps**
4. **Rollback Matrix**
5. **Verification & Monitoring**

## Examples

**Example prompt**
"We use Prisma and need to add a non-null `status` column with a backfill. We cannot take downtime. What is the migration plan and rollback?"

**Example response outline**
1. Migration Context: Prisma, Postgres, zero-downtime, large table.
2. Strategy & Decision Points: expand/contract, batched backfill job.
3. Artifacts & Execution Steps: add nullable column, deploy dual-write, backfill batches, enforce NOT NULL, drop old logic.
4. Rollback Matrix: revert schema changes, pause backfill, restore old code paths.
5. Verification & Monitoring: staging rehearsal, backfill progress metrics, post-cutover checks.

## Resources (Optional)

- References index: `references/README.md`
