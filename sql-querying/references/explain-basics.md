# EXPLAIN Basics

Use `EXPLAIN` (or your DB equivalent) to validate whether query changes actually improve the plan.

## Postgres

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;
```

High-signal checks:

- Does it do a seq scan on a huge table?
- Are row estimates wildly off? (stats issues)
- Are you accidentally multiplying rows via joins?

If improvements require indexing strategy, statistics maintenance, or systemic tuning, call it out as out of scope and request direction.
