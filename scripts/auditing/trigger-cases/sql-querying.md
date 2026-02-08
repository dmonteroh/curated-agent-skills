# Trigger Cases: sql-querying

## Positive (should activate)
- prompt: "I need help with this: Writing complex queries (joins, grouping, CTEs, window functions). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Refactoring queries for readability and correctness. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You need DB-wide performance diagnosis (index strategy, lock contention, pool sizing). No planning, just implementation."
  expect_activate: no
