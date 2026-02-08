# Trigger Cases: code-explain

## Positive (should activate)
- prompt: "I need help with this: Explaining complex code, algorithms, or system behavior. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Creating onboarding walkthroughs or learning materials. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is to implement new features or refactors. No planning, just implementation."
  expect_activate: no
