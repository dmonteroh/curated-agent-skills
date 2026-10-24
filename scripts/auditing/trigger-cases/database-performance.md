# Trigger Cases: database-performance

## Positive (should activate)

- prompt: "Our orders dashboard query went from 200ms to 12 seconds after last week's deploy. Can you pull the EXPLAIN ANALYZE output, figure out what changed, and fix it? Postgres 15, the slow query is in app/reports/orders_summary.sql."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "The nightly job that updates user_balances is deadlocking with the checkout service. Here are the deadlock logs. Work out which queries are conflicting and change the code so they stop blocking each other."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "pg_stat_statements shows this query eating 70% of our total DB time. Look at its plan, tell me why it's doing a seq scan on a 40M row table, and add whatever index or rewrite is needed."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "queries super slow on the users table fix it"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Customers are timing out during checkout because several MySQL queries appear to be waiting on each other. Diagnose the blocking and lock contention from query plans and monitoring data, and resolve it safely."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Our reporting queries are suddenly taking minutes instead of seconds. Analyze the execution plans, index usage, and runtime metrics, then tune the queries or indexes to restore performance."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Find the cause of the SQL Server deadlocks and long-running queries affecting the billing job. Use Query Store and execution plans to make the necessary query or schema changes."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Design a database schema for a multi-tenant SaaS app with users, organizations, and billing tables."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Convert this SQLite script to use SQLAlchemy models instead of raw SQL strings."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Our Python API endpoint is slow. Profile the application code with cProfile and find the hot loops. The database is fine."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Set up Grafana dashboards and alerts for Postgres metrics like connections, cache hit ratio, and replication lag. Nothing is currently slow."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Migrate our application from MySQL to PostgreSQL with minimal downtime."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Review database backup and restore procedures and test that we can recover from a regional outage."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Investigate why our Kafka consumers are blocked and lagging behind producers."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
