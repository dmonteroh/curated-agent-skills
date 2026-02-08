# Trigger Cases: postgresql-engineering

## Positive (should activate)
- prompt: "I need help with this: Designing Postgres schemas, constraints, and indexing strategy. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Choosing Postgres data types (JSONB, arrays, enums, money/time types). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You are targeting a non-PostgreSQL database. No planning, just implementation."
  expect_activate: no
