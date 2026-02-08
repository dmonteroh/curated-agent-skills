# Trigger Cases: chaos-engineer

## Positive (should activate)
- prompt: "I need help with this: Validate resilience (timeouts/retries/circuit breakers/backpressure). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Produce a game day plan and runbook. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Steady-state signals cannot be defined because observability is missing. No planning, just implementation."
  expect_activate: no
