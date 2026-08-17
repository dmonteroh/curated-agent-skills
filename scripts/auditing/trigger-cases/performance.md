# Trigger Cases: performance

## Positive (should activate)
- prompt: "I need help with this: Diagnosing performance bottlenecks (backend/frontend/infra). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing load tests, capacity plans, performance budgets, or SLOs. Can you guide me?"
  expect_activate: yes

- prompt: "There are about four plausible ways to write this hot loop. Give it two hours max — try them, keep the numbers, and stop when it stops paying off."
  expect_activate: yes

- prompt: "The dashboard is quick but the numbers are up to ten minutes stale and users are noticing. How do we weigh freshness against what it costs to serve?"
  expect_activate: yes

- prompt: "A one-line change takes 90 seconds to rebuild and the suite runs 12 minutes. Can we measure that loop and cut it down?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is feature work with no performance goals. No planning, just implementation."
  expect_activate: no

- prompt: "The cache is handing back records we deleted an hour ago. It's plain wrong — fix the invalidation, speed isn't the issue."
  expect_activate: no
