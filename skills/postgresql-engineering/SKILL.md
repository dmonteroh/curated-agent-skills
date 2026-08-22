---
name: postgresql-engineering
description: "PostgreSQL-specific schema and data-layer engineering: DDL, data types, constraints, indexing, JSONB, partitioning, RLS, and safe schema evolution. Use when targeting Postgres specifically."
metadata:
  category: database
---
# PostgreSQL Engineering

Use this skill for Postgres-specific schema/data-layer decisions (not just SQL query authoring).

## Use this skill when

- Designing Postgres schemas, constraints, and indexing strategy
- Choosing Postgres data types (JSONB, arrays, enums, money/time types)
- Planning partitioning or RLS policies
- Shaping table storage for an update-heavy or insert-heavy write workload
- Deciding whether a Postgres extension is the right answer to a stated requirement
- Reviewing schema changes for safety and operational impact

## Do not use this skill when

- You are targeting a non-PostgreSQL database
- You only need query authoring/tuning
- You need DB-agnostic modeling guidance

## Workflow

1) Capture requirements
- Ask for entities, invariants, access paths, scale targets, and deployment constraints.
- If any of these are missing, pause and request the specific inputs.
- Output: Requirements summary + assumptions list.

2) Model schema + constraints
- Map entities to tables; map invariants to NOT NULL, UNIQUE, CHECK, and FK constraints.
- If an invariant cannot be enforced by constraints, call it out explicitly.
- If the invariant is "these ranges must not overlap" (rooms, shifts, price periods), enforce it with an `EXCLUDE USING gist (key WITH =, period WITH &&)` constraint rather than an application-level check.
- If two tables reference each other, make one FK `DEFERRABLE INITIALLY DEFERRED` so both rows can be written inside a single transaction.
- Output: Table/column list with constraints tied to each invariant.

3) Choose data types and storage
- Use Postgres-native types intentionally (TIMESTAMPTZ, NUMERIC, JSONB, enums).
- If global/opaque IDs are required, choose UUID; otherwise prefer BIGINT identity.
- If attributes are frequently filtered/sorted, model them as columns; if truly unstructured, use JSONB.
- Reject these types before any DDL is written, naming the replacement in the rationale: `timestamp` without time zone and `timetz` (use `timestamptz`), any precision spec such as `timestamptz(0)` (use bare `timestamptz`), `char(n)` and `varchar(n)` (use `text`, plus `CHECK (length(col) <= n)` where a hard limit is a real requirement), `money` (use `numeric`), `serial`/`bigserial` (use `generated always as identity`). A schema that ships any of them has not passed this step.
- If a table holds large text or binary values, decide its TOAST storage strategy rather than inheriting the default — `references/storage-and-workload.md`.
- Output: Data type decisions + rationale per column.

4) Design indexes for access paths
- Add indexes for join keys, common filters/sorts, and uniqueness requirements.
- If JSONB containment is a primary access pattern, add GIN indexes.
- Pick the index type from the access pattern instead of defaulting to B-tree: GiST for range and geometric types and for every `EXCLUDE` constraint; BRIN for very large tables whose physical row order already correlates with the column; GIN also serves arrays and full-text, not only JSONB. Covering, partial, and expression variants: `references/indexing-and-constraints.md`.
- Composite column order decides whether an index is usable at all — only a leftmost prefix can be matched, so put equality-filtered columns first and the range or sort column last.
- Output: Index list mapped to queries/access paths.

5) Plan operational features
- If data is time-sliced and large, consider partitioning; otherwise avoid it.
- If per-tenant or per-user access isolation is required, design RLS policies.
- Wrap any function call inside an RLS `USING`/`WITH CHECK` predicate in a scalar subquery — `USING ((SELECT current_user_id()) = user_id)`, not `USING (current_user_id() = user_id)` — so the planner evaluates it once per query instead of once per row scanned.
- If the write workload is heavily skewed toward updates or toward bulk inserts, choose the matching storage tactics: `references/storage-and-workload.md`.
- Output: Partitioning/RLS decision and configuration outline.

6) Plan safe schema evolution
- Use expand/contract for breaking changes; avoid long table rewrites.
- If creating large indexes, use CREATE INDEX CONCURRENTLY with a rollback plan.
- Output: Migration plan with rollout, rollback, and verification steps.

## Common pitfalls

- Missing indexes on foreign keys (Postgres does not add them automatically); `references/indexing-and-constraints.md` carries a catalog query that lists the unindexed ones.
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

## Output contract

Provide a report using this exact structure and ordering:

1) Requirements summary + assumptions
2) Schema proposal (tables/columns/constraints tied to invariants)
3) Data type decisions (with rationale)
4) Index plan (tied to access paths)
5) Operational features (partitioning/RLS if applicable)
6) Migration plan (rollout, rollback, verification)

## References

- Reference index: `references/README.md`
- Full Postgres playbook (types, indexing, JSONB, migrations): `references/playbook.md`
- Index types, composite ordering, and constraints beyond the basics: `references/indexing-and-constraints.md`
- Table storage types, TOAST, and update-/insert-heavy tactics: `references/storage-and-workload.md`
- Extension-to-use-case selection: `references/extensions.md`
