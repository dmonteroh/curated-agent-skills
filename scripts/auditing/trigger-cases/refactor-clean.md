# Trigger Cases: refactor-clean

## Positive (should activate)
- prompt: "I need help with this: Refactoring tangled or hard-to-maintain code. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Reducing duplication, complexity, or code smells. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: A small, targeted fix is all that is needed. No planning, just implementation."
  expect_activate: no
