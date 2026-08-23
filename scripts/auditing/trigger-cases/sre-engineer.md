# Trigger Cases: sre-engineer

## Positive (should activate)
- prompt: "I need help with this: Defining SLIs/SLOs and error budgets. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing alert strategy (burn-rate, paging vs ticketing) and runbooks. Can you guide me?"
  expect_activate: yes

- prompt: "Half of every on-call shift goes on restarting stuck workers and draining queues by hand. Can we get that automated and mitigated without a human?"
  expect_activate: yes

- prompt: "We handle incidents completely ad hoc and never follow up afterwards. Help us build a real incident response and postmortem loop."
  expect_activate: yes

- prompt: "Leadership wants 'better reliability' this quarter. Turn that into concrete backlog items with owners we can actually schedule."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You only need a dashboard or visualization without SLOs or alerting design. No planning, just implementation."
  expect_activate: no
