# Trigger Cases: tech-debt

## Positive (should activate)
- prompt: "I need help with this: Dev velocity is slowing, bug rate is increasing, or on-call is painful. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: A debt audit and prioritized cleanup roadmap are required. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is only for a local refactor of a single module. No planning, just implementation."
  expect_activate: no
