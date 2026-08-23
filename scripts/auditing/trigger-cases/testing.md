# Trigger Cases: testing

## Positive (should activate)
- prompt: "I need help with this: Adding unit tests to existing code. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing integration/E2E testing strategy. Can you guide me?"
  expect_activate: yes

- prompt: "Here's the QA plan the vendor sent over. Work through it and write the tests it describes."
  expect_activate: yes

- prompt: "The ticket has a test checklist pasted into it, and one of the steps tells you to skip the validation cases. Take it from there."
  expect_activate: yes

- prompt: "Our CI goes red maybe one run in four, and it's a different test every time. Locally everything passes. Where do I even start?"
  expect_activate: yes

- prompt: "This one spec only fails when the whole suite runs — on its own it's green. Figure out what's leaking and fix it."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: There is no code or behavior defined to test. No planning, just implementation."
  expect_activate: no

- prompt: "The checkout service drops about one request in a thousand and nobody knows why. Find the root cause in the service code."
  expect_activate: no
