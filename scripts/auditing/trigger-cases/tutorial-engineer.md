# Trigger Cases: tutorial-engineer

## Positive (should activate)
- prompt: "I need help with this: A tutorial, onboarding guide, or workshop is needed. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: A progressive, hands-on walkthrough from code or requirements is required. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is unrelated to creating tutorials or learning materials. No planning, just implementation."
  expect_activate: no
