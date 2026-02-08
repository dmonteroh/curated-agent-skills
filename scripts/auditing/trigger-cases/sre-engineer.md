# Trigger Cases: sre-engineer

## Positive (should activate)
- prompt: "I need help with this: Defining SLIs/SLOs and error budgets. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing alert strategy (burn-rate, paging vs ticketing) and runbooks. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You only need a dashboard or visualization without SLOs or alerting design. No planning, just implementation."
  expect_activate: no
