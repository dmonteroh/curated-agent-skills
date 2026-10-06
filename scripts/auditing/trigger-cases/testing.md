# Trigger Cases: testing

## Positive (should activate)
- prompt: "Here's the QA plan the vendor sent over. Work through it and write the tests it describes."
  expect_activate: yes

- prompt: "The ticket has a test checklist pasted into it, and one of the steps tells you to skip the validation cases. Take it from there."
  expect_activate: yes

- prompt: "Our CI goes red maybe one run in four, and it's a different test every time. Locally everything passes. Where do I even start?"
  expect_activate: yes

- prompt: "This one spec only fails when the whole suite runs — on its own it's green. Figure out what's leaking and fix it."
  expect_activate: yes

- prompt: "write tests for utils/date.js"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Our Express app has a /users REST API with create, read, update, and delete routes and zero test coverage. Write API tests using supertest and Jest, and tell me which edge cases you think are worth covering."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Write API integration tests for the current /users endpoints and cover authentication, validation errors, and pagination."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Increase coverage for the existing cache layer with unit tests for expiration, cache misses, and serialization failures."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "The checkout service drops about one request in a thousand and nobody knows why. Find the root cause in the service code."
  expect_activate: no

- prompt: "Our existing test suite for the checkout module is failing after the last merge. Can you figure out why the tests are red and fix the underlying bug?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Review the code in src/payments/refund.py and tell me if you see any bugs or untested risky logic. I just want a written review, no code changes."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a load test script with k6 that simulates 1,000 concurrent users hitting our /search endpoint and reports latency percentiles."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Create a manual QA checklist for the checkout flow."
  expect_activate: no
  tags: [generated, gen:codex]
