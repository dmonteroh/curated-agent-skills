# Trigger Cases: database-architect

## Positive (should activate)
- prompt: "I need help with this: Choosing a database or storage pattern (relational, document, time-series, search). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing schemas, constraints, and indexes for real access patterns. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Only query tuning or a single slow query fix is needed. No planning, just implementation."
  expect_activate: no
