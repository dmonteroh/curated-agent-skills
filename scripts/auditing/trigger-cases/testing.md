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

## Negative (should not activate)
- prompt: "Please do this exactly now: There is no code or behavior defined to test. No planning, just implementation."
  expect_activate: no
