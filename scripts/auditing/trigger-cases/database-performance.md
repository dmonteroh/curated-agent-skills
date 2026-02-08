# Trigger Cases: database-performance

## Positive (should activate)
- prompt: "I need help with this: Investigating slow queries, timeouts, or lock contention. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Tuning indexes, queries, connection pooling, caching, or partitioning. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Choosing a database or designing a schema from scratch. No planning, just implementation."
  expect_activate: no
