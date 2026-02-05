---
name: sql-querying
description: Write correct, maintainable SQL queries (joins, CTEs, window functions) and reason about their results for OLTP or analytics tasks.
category: database
---

# SQL Querying

This skill is for writing and reasoning about SQL: correctness first, then performance, then readability.

## Required inputs

- Target database/dialect (and version if relevant)
- Tables, columns, and key relationships (PK/FK)
- Desired output shape (columns, filters, grouping, ordering)
- Sample data or edge cases, if available

## Use this skill when

- Writing complex queries (joins, grouping, CTEs, window functions)
- Refactoring queries for readability and correctness
- Reasoning about query outputs and edge cases (NULLs, duplicates, join cardinality)
- Doing query-level optimization with EXPLAIN

## Do not use this skill when

- You need DB-wide performance diagnosis (index strategy, lock contention, pool sizing)
- You need to design a schema/data model from scratch
- You need ORM-specific or query-builder-only guidance

## Trigger phrases

- "Write a SQL query to ..."
- "Why does this query return duplicates?"
- "Convert this report logic into a CTE/window function"
- "Explain what this SQL query returns"

## Workflow (Deterministic)

1. Confirm requirements and dialect.
   - Output: short requirement summary + open questions.
   - Decision: if required inputs are missing, ask questions and stop.
2. Draft the simplest correct query.
   - Output: draft SQL + brief shape explanation (joins/CTEs/windows).
3. Validate correctness against edge cases.
   - Output: checklist of NULL/duplicate/cardinality behaviors.
   - Decision: if results are wrong, revise joins/filters/aggregations and re-check.
4. Evaluate query-level performance.
   - Output: EXPLAIN guidance or expected plan changes.
   - Decision: if improvements require schema/index/system tuning, call it out as out of scope and request direction.
5. Finalize response.
   - Output: final SQL + reporting format in the Output Contract.

## Common pitfalls

- Filtering on a LEFT JOINed table in the WHERE clause (turns into INNER JOIN)
- Aggregations that ignore NULL handling or duplicate multiplicative joins
- Using `NOT IN` with NULL-able subqueries (prefer `NOT EXISTS`)
- Missing deterministic `ORDER BY` for top-N or pagination queries
- Time-based filters without clarifying time zones or inclusive/exclusive bounds

## Output Contract (Always)

- `Summary`: 1-2 sentences on approach.
- `Final SQL`: formatted query.
- `Correctness checks`: NULL handling, duplicate risk, cardinality assumptions.
- `Performance notes` (optional): EXPLAIN guidance and plan risks.
- `Assumptions & questions`: anything missing or ambiguous.
- `Reporting format`:

````
Summary: <short approach>
Final SQL:
```sql
<query>
```
Correctness checks:
- <checklist items>
Performance notes: <optional>
Assumptions & questions:
- <open questions>
````

## Examples

**Example 1: Rolling 7-day revenue**

User request:
"Show daily revenue with a 7-day rolling average for the last 30 days."

Response (formatted):

````text
Summary: Uses a window function to compute a 7-day rolling average per day.
Final SQL:
```sql
SELECT
  day,
  revenue,
  AVG(revenue) OVER (
    ORDER BY day
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rolling_7d_avg
FROM daily_sales
WHERE day >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY day;
```
Correctness checks:
- Rolling window uses ROWS frame to avoid grouping ties.
- Date filter is inclusive for the last 30 days.
Performance notes: n/a
Assumptions & questions:
- Confirm target timezone for `day` and `CURRENT_DATE`.
````

**Example 2: Customers with no completed orders**

User request:
"List customers who have never completed an order."

Response (formatted):

````text
Summary: Uses a `NOT EXISTS` anti-join to find customers with no completed orders.
Final SQL:
```sql
SELECT c.id, c.email
FROM customers c
WHERE NOT EXISTS (
  SELECT 1
  FROM orders o
  WHERE o.customer_id = c.id
    AND o.status = 'completed'
);
```
Correctness checks:
- `NOT EXISTS` avoids NULL pitfalls from `NOT IN`.
- Only `status = 'completed'` qualifies an order.
Performance notes: n/a
Assumptions & questions:
- Confirm whether cancelled or refunded orders should count.
````

## Trigger test

- "Write a SQL query that returns the top 3 products per category."
- "Explain what rows this join produces and how to fix duplicates."

## References (Optional)

- See `references/README.md` for indexed topics and summaries.
