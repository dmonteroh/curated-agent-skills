# Trigger Cases: ui-design

## Positive (should activate)
- prompt: "I need help with this: Requirements are unclear and you need a UI brief + flow before implementation. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Defining component behaviors and states (loading/empty/error/disabled). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The user explicitly wants UI code implementation only. No planning, just implementation."
  expect_activate: no
