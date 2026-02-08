# Trigger Cases: monitoring-expert

## Positive (should activate)
- prompt: "Requirements are unclear and we need help comparing options before implementation."
  expect_activate: yes

- prompt: "Requirements are unclear and we need help comparing options before implementation."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is only for a single vendor UI walkthrough with no implementation decisions. No planning, just implementation."
  expect_activate: no
