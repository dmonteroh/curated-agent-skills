# Trigger Cases: monitoring-expert

## Positive (should activate)
- prompt: "Requirements are unclear and we need help comparing options before implementation."
  expect_activate: yes

- prompt: "Requirements are unclear and we need help comparing options before implementation."
  expect_activate: yes

- prompt: "I want to be paged when a release makes p99 worse than it was right before that deploy, not when it crosses some fixed number."
  expect_activate: yes

- prompt: "We got woken at 3am because an internal mTLS certificate expired. What should we have had in place to see that coming weeks earlier?"
  expect_activate: yes

- prompt: "This Node service went to production with no instrumentation whatsoever. Can you help me add monitoring to it?"
  expect_activate: yes

- prompt: "We're flying blind whenever something breaks — I want proper logs, metrics, traces and alerts on this API."
  expect_activate: yes

- prompt: "I want to stand up Prometheus and Grafana, ship logs to Loki and traces to Jaeger, and instrument the services with OpenTelemetry. How should that pipeline be wired?"
  expect_activate: yes

- prompt: "Our alerts fire constantly and the team has stopped reading them. Can you design an alerting strategy tied to our SLO and SLA targets instead?"
  expect_activate: yes

- prompt: "Before the launch we need a load-testing plan and some profiling to find where the bottlenecks are. Where do we start?"
  expect_activate: yes

- prompt: "add alerts and metrics to the api"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)
- prompt: "After each deploy just curl the health URL a few times and tell me whether the site is up."
  expect_activate: no

- prompt: "Write a postmortem document for last Tuesday's outage using the incident timeline I pasted, including root cause and action items."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Migrate our CI pipeline from Jenkins to GitHub Actions, keeping the same build, test, and deploy stages."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Add a console.log and a try/catch around this function so I can see what value is coming in while I debug locally."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Build an analytics dashboard feature in our product that shows customers their own usage metrics and event history."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Build an internal admin dashboard that lets support agents search customer orders and issue refunds."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Upgrade the payment service from Node 18 to Node 22 and resolve any compatibility failures."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create a CI check that fails pull requests when services do not include enough unit-test coverage."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
