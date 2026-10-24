# Trigger Cases: chaos-engineer

## Positive (should activate)

- prompt: "Help me design a game day for our Postgres primary/replica setup in prod. We want to kill the primary, inject 300ms latency between the app and the replica, and verify failover works within our 30s RTO. Include a kill switch and rollback steps."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "We're about to claim 99.95% availability to a customer. I need a plan to actually prove our production system survives losing a Redis node and a 5% packet loss between services. Lay out the experiments, abort thresholds, and a safe way to stop them mid-run."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Can you plan an AWS Fault Injection Service experiment that terminates a random EC2 instance in our prod autoscaling group and adds network delay to the database subnet? I need stop conditions tied to CloudWatch alarms and a staged rollout from 1% of traffic upward."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "need to kill nodes and add latency in prod safely can you plan it"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Design a game day to validate that our Kubernetes platform survives node failures and packet loss between the API and database layers. Include guardrails, monitoring, abort thresholds, and a safe way to stop every experiment immediately."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Build a staged failure-injection test plan for production that proves our failover works during service crashes and degraded network conditions. Specify blast radius, hypotheses, metrics, stop conditions, and cleanup procedures."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Our server keeps crashing in production every few hours. Help me debug the logs and find out why the process gets killed, probably OOM."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Explain what the Chaos Monkey is and where the idea of chaos engineering came from. I'm just curious about the history, not planning anything."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a load test plan with k6 that ramps our checkout API from 100 to 5,000 requests per second so we can find the throughput ceiling and p99 latency under normal conditions."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you investigate why users experienced network delay and intermittent server failures this morning, then recommend a fix?"
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Create a load-testing plan that ramps checkout traffic to 20,000 requests per second and reports latency, error rate, and capacity limits."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Set up synthetic monitoring that continuously checks login, checkout, and API health from several geographic locations."
  expect_activate: no
  tags: [generated, gen:codex]
