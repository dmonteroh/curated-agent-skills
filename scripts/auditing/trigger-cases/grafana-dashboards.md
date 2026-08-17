# Trigger Cases: grafana-dashboards

## Positive (should activate)
- prompt: "I need help with this: A request asks to create or improve Grafana dashboards. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: A request asks to standardize dashboard layout for on-call usability. Can you guide me?"
  expect_activate: yes

- prompt: "We need a board for our RabbitMQ cluster — queue depth, consumer lag, unacked messages, the panels on-call actually stares at."
  expect_activate: yes

- prompt: "Put together the panels for our Elasticsearch cluster so whoever's on-call can see shard health and indexing rate at a glance."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is for end-to-end observability architecture beyond dashboards. No planning, just implementation."
  expect_activate: no
