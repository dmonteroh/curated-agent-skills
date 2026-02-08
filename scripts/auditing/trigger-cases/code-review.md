# Trigger Cases: code-review

## Positive (should activate)
- prompt: "I need help with this: Reviewing pull requests, diffs, or local changes. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Establishing code review standards for a team. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: There are no code changes to review. No planning, just implementation."
  expect_activate: no
