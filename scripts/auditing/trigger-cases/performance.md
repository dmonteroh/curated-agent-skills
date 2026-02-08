# Trigger Cases: performance

## Positive (should activate)
- prompt: "I need help with this: Diagnosing performance bottlenecks (backend/frontend/infra). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing load tests, capacity plans, performance budgets, or SLOs. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is feature work with no performance goals. No planning, just implementation."
  expect_activate: no
