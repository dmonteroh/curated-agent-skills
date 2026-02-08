# Trigger Cases: ui-visual-validator

## Positive (should activate)
- prompt: "I need help with this: Confirming a UI change is actually correct (not just 'different'). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Catching visual regressions before merge/release. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Designing a UI or exploring new layouts. No planning, just implementation."
  expect_activate: no
