# Trigger Cases: python

## Positive (should activate)
- prompt: "I need help with this: Building or refactoring Python 3.x services, CLIs, or libraries. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing async workflows or concurrency patterns. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is primarily about another runtime or language. No planning, just implementation."
  expect_activate: no
