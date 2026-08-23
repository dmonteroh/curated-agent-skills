# Trigger Cases: postgresql-engineering

## Positive (should activate)
- prompt: "I need help with this: Designing Postgres schemas, constraints, and indexing strategy. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Choosing Postgres data types (JSONB, arrays, enums, money/time types). Can you guide me?"
  expect_activate: yes

- prompt: "This Postgres table gets updated constantly and it bloats within days even with autovacuum running. Is there anything to change about how the rows are stored?"
  expect_activate: yes

- prompt: "We bulk-load 50 million rows into Postgres every night and it crawls. The table carries six indexes and a big JSON blob per row."
  expect_activate: yes

- prompt: "Someone on the team suggested adding pgvector for our similarity search. Is pulling in an extension the right answer here?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You are targeting a non-PostgreSQL database. No planning, just implementation."
  expect_activate: no
