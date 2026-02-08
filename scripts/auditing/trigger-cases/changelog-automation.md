# Trigger Cases: changelog-automation

## Positive (should activate)
- prompt: "I need help with this: Setting up automated changelog generation. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Implementing conventional commits. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The project has no release process or versioning. No planning, just implementation."
  expect_activate: no
