# Application Profiling: Database Queries

Use this reference for profiling database queries and identifying slow statements.

## PostgreSQL

```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 100;  -- Log queries > 100ms
SELECT pg_reload_conf();

-- Explain analyze
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 123
AND created_at > NOW() - INTERVAL '30 days';

-- Track slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## MySQL

```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.1;  -- 100ms

-- Explain query
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 123;

-- Performance schema
SELECT * FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;
```
