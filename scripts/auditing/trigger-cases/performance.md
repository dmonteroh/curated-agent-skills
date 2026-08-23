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

- prompt: "Our vector search sits at 400ms p99 and we need it under 100. Can we tune the index without quietly making the results worse?"
  expect_activate: yes

- prompt: "The nightly warehouse load runs six hours and we're still behind on the day's files. Make it faster, but I need proof nothing was dropped."
  expect_activate: yes

- prompt: "Checkout p95 has crept from 200ms to 900ms over the past month. Can you profile it and tell me where the time is actually going?"
  expect_activate: yes

- prompt: "This endpoint tops out around 300 RPS and falls over past that. What do we change to get throughput up?"
  expect_activate: yes

- prompt: "Since Tuesday's release the API feels a lot slower — looks like a perf regression. Can you confirm it against the previous build and find the cause?"
  expect_activate: yes

- prompt: "One report query against the orders table takes 40 seconds. Why is it so slow and what do we do about it?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is feature work with no performance goals. No planning, just implementation."
  expect_activate: no

- prompt: "Which embedding model should we use for the product catalogue?"
  expect_activate: no

- prompt: "Half of yesterday's files never landed in the warehouse table. Work out which ones failed and get them loaded."
  expect_activate: no

- prompt: "The cache is handing back records we deleted an hour ago. It's plain wrong — fix the invalidation, speed isn't the issue."
  expect_activate: no
