# Trigger Cases: grafana-dashboards

## Positive (should activate)
- prompt: "We need a board for our RabbitMQ cluster — queue depth, consumer lag, unacked messages, the panels on-call actually stares at."
  expect_activate: yes

- prompt: "Put together the panels for our Elasticsearch cluster so whoever's on-call can see shard health and indexing rate at a glance."
  expect_activate: yes

- prompt: "Can you build a Grafana dashboard for our checkout API that shows request rate, p95 latency, and 5xx error rate as live time series panels? Our data source is Prometheus and the metrics are http_requests_total and http_request_duration_seconds_bucket."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I need a Grafana dashboard for our Linux hosts using node_exporter metrics: CPU usage per core, memory used vs available, disk I/O, and network throughput. Please give me the dashboard JSON with a host variable dropdown and 10s auto-refresh."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Add a new row to our existing service-overview Grafana dashboard with gauges and stat panels for Redis memory usage, connected clients, and cache hit ratio, pulling from the redis_exporter data source."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Design an operations dashboard in Grafana that combines live application metrics from Prometheus with host metrics for each production server."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Create a Grafana dashboard with live time-series panels for API latency, request rate, error percentage, CPU, memory, disk usage, and network throughput."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "need live cpu and memory panels in grafana"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)

- prompt: "Write Prometheus alerting rules that page us when the checkout API p95 latency stays above 500ms for 5 minutes, and route them through Alertmanager to Slack."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Build a Metabase dashboard with bar charts of last quarter's sales by region from our Postgres warehouse."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a React component using Chart.js that renders a live-updating line chart from a websocket feed in our web app."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Configure Prometheus to scrape metrics from our services and Linux hosts; do not create dashboards yet."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Export last month's service latency and server-utilization metrics into a CSV report for the leadership team."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create a static executive slide deck with screenshots of service latency and server resource usage trends."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
