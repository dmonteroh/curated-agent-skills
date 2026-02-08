# Trigger Cases: doc-generate

## Positive (should activate)
- prompt: "I need help with this: Generating API docs, architecture docs, onboarding guides, or runbooks from code. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Standardizing documentation structure across a repo. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is only for a one-off explanation of a single snippet. No planning, just implementation."
  expect_activate: no
