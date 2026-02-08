# Trigger Cases: testing

## Positive (should activate)
- prompt: "I need help with this: Adding unit tests to existing code. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing integration/E2E testing strategy. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: There is no code or behavior defined to test. No planning, just implementation."
  expect_activate: no
