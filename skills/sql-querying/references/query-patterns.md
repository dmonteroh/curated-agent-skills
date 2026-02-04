# Query Patterns (High-Signal)

This file is a compact catalog of query-shaping patterns that improve correctness and maintainability.

## CTEs (Use For Readability, Not Always Performance)

CTEs can improve readability. In some databases/versions they may also act as optimization fences.

Pattern:

```sql
WITH filtered AS (
  SELECT id, user_id
  FROM orders
  WHERE status = 'completed'
)
SELECT user_id, COUNT(*)
FROM filtered
GROUP BY user_id;
```

## EXISTS / NOT EXISTS (Safer Than IN / NOT IN)

- Prefer `EXISTS` for presence checks.
- Avoid `NOT IN (...)` when the subquery can return NULLs.

```sql
-- Good
SELECT u.id
FROM users u
WHERE EXISTS (
  SELECT 1
  FROM orders o
  WHERE o.user_id = u.id
    AND o.status = 'completed'
);

-- Good
SELECT u.id
FROM users u
WHERE NOT EXISTS (
  SELECT 1
  FROM orders o
  WHERE o.user_id = u.id
);
```

## Anti-Join (Find rows in A with no match in B)

```sql
SELECT u.id, u.email
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;
```

## LATERAL / APPLY (Correlated subquery per row)

If your DB supports it (e.g., Postgres `LATERAL`), it’s a clean pattern for “top N per group”.

```sql
SELECT c.id, recent.order_date, recent.total
FROM customers c
CROSS JOIN LATERAL (
  SELECT order_date, total
  FROM orders o
  WHERE o.customer_id = c.id
  ORDER BY order_date DESC
  LIMIT 3
) recent;
```

## Window vs GROUP BY

- Use `GROUP BY` when you need one row per group.
- Use window functions when you need group metrics *without collapsing rows*.

## Recursive CTEs (Use Carefully)

- Use for hierarchies (org charts, bill-of-materials).
- Add cycle prevention.
- Add a max depth guard when possible.

## NULL Pitfalls

- `NULL` never equals `NULL`.
- Use `IS NULL` / `IS NOT NULL`.
- Use `COALESCE` deliberately (don’t hide data-quality issues).
