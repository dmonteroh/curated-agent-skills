# Trigger Cases: database-migration-sql

## Positive (should activate)

- prompt: "I need to add a NOT NULL column `tier` with default 'free' to our `accounts` table in Postgres. It has about 400M rows and we can't take downtime. Can you write the SQL migration scripts by hand, doing it in safe steps?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Write raw SQL to rename the column `orders.cust_id` to `orders.customer_id` in production Postgres with zero downtime. Apps are running old and new code during deploy, so I need a compatible approach, not just ALTER TABLE RENAME."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I need to change `events.payload` from varchar(255) to text and add an index on `events(created_at, type)` on a live table with heavy writes. Please write the SQL scripts, using CREATE INDEX CONCURRENTLY or equivalent, plus a rollback script."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "add column to huge postgres table no downtime need sql"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Write a hand-authored, zero-downtime SQL migration to add a nullable `preferred_language` column to the production `customers` table, backfill it safely, and later enforce the intended default."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Draft an online schema-change migration for PostgreSQL that converts `users.email` to case-insensitive uniqueness without locking the table for normal traffic."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Write reversible SQL deployment scripts to migrate a production table from an integer primary key to bigint using an expand-contract approach with no service interruption."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Can you write an Alembic migration using the Python ORM to add a `nickname` column to the User model in our dev environment? Downtime is fine there."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a SQL query that finds the top 10 customers by total order value over the last 90 days, joining orders and customers."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Help me tune this slow Postgres query. Here's the EXPLAIN ANALYZE output. Which indexes should I consider?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Design the schema for a new multi-tenant billing system from scratch: tables, keys, and relationships. There's no existing data."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a SQL query that adds a calculated `total_spend` column to a report result without altering any tables."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Create a stored procedure that copies rows from `legacy_orders` to `orders_archive` every night."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
