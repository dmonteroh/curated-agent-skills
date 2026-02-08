---
name: postgresql-engineering
description: "PostgreSQL-specific schema and data-layer engineering: DDL, data types, constraints, indexing, JSONB, partitioning, RLS, and safe schema evolution. Use when targeting Postgres specifically."
category: database
---
# PostgreSQL Engineering

Use this skill for Postgres-specific schema/data-layer decisions (not just SQL query authoring).

## Use this skill when

- Designing Postgres schemas, constraints, and indexing strategy
- Choosing Postgres data types (JSONB, arrays, enums, money/time types)
- Planning partitioning or RLS policies
- Reviewing schema changes for safety and operational impact

## Do not use this skill when

- You are targeting a non-PostgreSQL database
- You only need query authoring/tuning
- You need DB-agnostic modeling guidance

## Workflow (Deterministic)

1) Capture requirements
- Ask for entities, invariants, access paths, scale targets, and deployment constraints.
- If any of these are missing, pause and request the specific inputs.
- Output: Requirements summary + assumptions list.

2) Model schema + constraints
- Map entities to tables; map invariants to NOT NULL, UNIQUE, CHECK, and FK constraints.
- If an invariant cannot be enforced by constraints, call it out explicitly.
- Output: Table/column list with constraints tied to each invariant.

3) Choose data types and storage
- Use Postgres-native types intentionally (TIMESTAMPTZ, NUMERIC, JSONB, enums).
- If global/opaque IDs are required, choose UUID; otherwise prefer BIGINT identity.
- If attributes are frequently filtered/sorted, model them as columns; if truly unstructured, use JSONB.
- Output: Data type decisions + rationale per column.

4) Design indexes for access paths
- Add indexes for join keys, common filters/sorts, and uniqueness requirements.
- If JSONB containment is a primary access pattern, add GIN indexes.
- Output: Index list mapped to queries/access paths.

5) Plan operational features
- If data is time-sliced and large, consider partitioning; otherwise avoid it.
- If per-tenant or per-user access isolation is required, design RLS policies.
- Output: Partitioning/RLS decision and configuration outline.

6) Plan safe schema evolution
- Use expand/contract for breaking changes; avoid long table rewrites.
- If creating large indexes, use CREATE INDEX CONCURRENTLY with a rollback plan.
- Output: Migration plan with rollout, rollback, and verification steps.

## Common pitfalls

- Missing indexes on foreign keys (Postgres does not add them automatically).
- Using JSONB for fields that need frequent filtering or sorting.
- Adding NOT NULL columns with volatile defaults that rewrite large tables.
- Relying on UNIQUE with NULLs when single-null enforcement is required.

## Examples

**Example prompt**
"Design a Postgres schema for orders, users, and line items with a safe migration plan."

**Example response (abridged)**
1) Requirements summary + assumptions
- Entities: users, orders, line_items; access paths for user history and order lookup.
- Assumptions: moderate write load, quarterly schema changes.

2) Schema proposal
- `users`, `orders`, `line_items` with NOT NULL, UNIQUE, FK, and CHECK constraints tied to invariants.

3) Data type decisions
- BIGINT identity PKs, NUMERIC for money, TIMESTAMPTZ for event time.

4) Index plan
- `orders(user_id, created_at)`, `line_items(order_id)`.

5) Operational features
- No partitioning; RLS not required.

6) Migration plan
- Expand/contract steps with rollback and verification queries.

## Output Contract (Always)

Provide a report using this exact structure and ordering:

1) Requirements summary + assumptions
2) Schema proposal (tables/columns/constraints tied to invariants)
3) Data type decisions (with rationale)
4) Index plan (tied to access paths)
5) Operational features (partitioning/RLS if applicable)
6) Migration plan (rollout, rollback, verification)

## References (Optional)

- Reference index: `references/README.md`
- Full Postgres playbook (types, indexing, JSONB, migrations): `references/playbook.md`
