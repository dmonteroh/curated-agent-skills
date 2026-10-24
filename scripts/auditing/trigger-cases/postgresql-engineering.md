# Trigger Cases: postgresql-engineering

## Positive (should activate)
- prompt: "This Postgres table gets updated constantly and it bloats within days even with autovacuum running. Is there anything to change about how the rows are stored?"
  expect_activate: yes

- prompt: "We bulk-load 50 million rows into Postgres every night and it crawls. The table carries six indexes and a big JSON blob per row."
  expect_activate: yes

- prompt: "Someone on the team suggested adding pgvector for our similarity search. Is pulling in an extension the right answer here?"
  expect_activate: yes

- prompt: "need partitioned events table postgres by month plus gin index on payload"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "I'm building a multi-tenant SaaS app on Postgres 16. Can you design the schema for orgs, users, projects, and audit events? I want a JSONB settings column on projects with a CHECK constraint on required keys, audit_events partitioned monthly by created_at, and row-level security so each tenant only sees its own rows based on a session variable."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Design the tables for a healthcare appointments system in PostgreSQL. Patients should only be able to read their own records, and clinicians only those of patients assigned to them. Write the CREATE TABLE statements, RLS policies with roles, FK and exclusion constraints to prevent double-booking a provider, and a JSONB column for intake form answers with a GIN index."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Design a PostgreSQL schema for a multi-tenant SaaS app with normalized tables, appropriate B-tree and GIN indexes, foreign keys and check constraints, JSONB metadata, monthly partitions for audit logs, and row-level security policies by tenant."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Build the table design and migration SQL for a PostgreSQL analytics platform. Include primary/foreign keys, unique and exclusion constraints where useful, GIN indexes on JSONB event properties, partitions by event date, and RLS policies for workspace isolation."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Can you migrate my MySQL 8 schema to SQLite for local testing? It has a few JSON columns and foreign keys that I need to keep working."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Help me design a MongoDB schema for a blog with comments, tags, and user profiles, including which fields to embed versus reference."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Design a MySQL database schema for a marketplace, including tables, indexes, constraints, and sharding recommendations."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "This query on my existing Postgres events table is slow: SELECT * FROM events WHERE payload->>'type' = 'click' AND created_at > now() - interval '7 days'. Can you explain the EXPLAIN ANALYZE output I pasted and suggest how to speed it up without changing the schema?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Design JSON schemas and validation rules for the API payloads our PostgreSQL service accepts."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Set up PostgreSQL replication, backups, and high-availability failover for our production cluster."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Optimize the existing PostgreSQL queries in our reporting service using EXPLAIN ANALYZE and rewrite slow joins."
  expect_activate: no
  tags: [generated, gen:codex]
