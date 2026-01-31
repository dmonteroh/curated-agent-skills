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

For DB-wide indexing strategy, statistics, and systemic tuning, use `database-performance`.
