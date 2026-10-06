# Trigger Cases: sre-engineer

## Positive (should activate)
- prompt: "Half of every on-call shift goes on restarting stuck workers and draining queues by hand. Can we get that automated and mitigated without a human?"
  expect_activate: yes

- prompt: "We handle incidents completely ad hoc and never follow up afterwards. Help us build a real incident response and postmortem loop."
  expect_activate: yes

- prompt: "Leadership wants 'better reliability' this quarter. Turn that into concrete backlog items with owners we can actually schedule."
  expect_activate: yes

- prompt: "need slos and error budget for our api plus alerts and runbook"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Our checkout API has been getting more traffic and the execs keep asking 'how reliable is it?' I need to define SLIs and SLOs for it, figure out an error budget, and set up burn-rate alerts plus a runbook for the on-call. Latency p99 and availability are what customers care about. Can you help me lay this out?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Product wants 100% uptime for our search service. I need to push back with a proper error budget policy: what happens when we burn through the budget, who decides to freeze releases, and how we measure it. Help me draft the SLO doc and the policy."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Our on-call is drowning in noisy pages. I want to rebuild alerting around SLOs for our order-processing pipeline: decide the acceptable failure rate, alert only on budget burn, write runbooks for the top three failure modes, and set up an incident commander rotation and blameless review practice."
  expect_activate: yes
  tags: [generated, gen:claude]

## Negative (should not activate)

- prompt: "Our checkout API p99 latency spiked to 4 seconds after yesterday's deploy. Can you look through the code in this repo and find what's causing the slowdown?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a Terraform module that provisions a multi-AZ Postgres cluster with automatic failover for our orders database."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Set up a Grafana dashboard showing CPU, memory and request rate for each pod in our payments namespace."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Run a chaos engineering experiment that kills random pods in staging so we can see how the checkout service handles failure."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Reduce cloud costs for our API platform by identifying oversized infrastructure, setting budgets, and alerting when monthly spend exceeds projections."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Improve application performance by profiling slow endpoints, optimizing database queries, and setting a latency benchmark for the next release."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create a customer-support escalation workflow for outage reports, including ticket routing, response templates, and stakeholder communications."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Track our deployment success rate and require releases to roll back if more than 2% of canary requests fail."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
