# Alerting Rules

## Prometheus Alert Rules

```yaml
# alerts.yml
groups:
  - name: application
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
          description: Error rate is {{ $value | humanizePercentage }}

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High latency detected
          description: 95th percentile latency is {{ $value }}s

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: Service {{ $labels.instance }} is down

  - name: infrastructure
    rules:
      - alert: HighMemoryUsage
        expr: |
          (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
          / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High memory usage on {{ $labels.instance }}

      - alert: HighCPUUsage
        expr: |
          100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: High CPU usage on {{ $labels.instance }}

      - alert: DiskSpaceLow
        expr: |
          (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: Disk space low on {{ $labels.instance }}
```

## Alert Design Principles

```yaml
# Good alert: Actionable, specific
- alert: DatabaseConnectionPoolExhausted
  expr: db_pool_available_connections == 0
  for: 2m
  annotations:
    runbook_url: https://wiki.example.com/runbooks/db-pool

# Bad alert: Too noisy, not actionable
- alert: AnyError
  expr: errors_total > 0  # Will always fire
```

## Baseline-Relative Regression Alerts

Every rule above is an *absolute* threshold: it fires when a metric leaves a fixed safe range. Absolute thresholds cannot see a regression that stays inside that range - p95 latency moving from 120ms to 300ms is a serious degradation and a `> 1s` rule stays silent through all of it. Add a second class of rule that compares the current value against a baseline captured before the change being watched.

The mechanism is three steps: capture a baseline at a named point (the deploy about to go out, the last release tag, the same window one week ago), keep that baseline addressable as a series, and express the alert as a ratio or delta against it rather than against a constant.

```yaml
# Recorded baseline: the deploy pipeline snapshots the metric before rollout,
# and the alert compares live traffic against that snapshot.
groups:
  - name: baseline-capture
    rules:
      - record: job:http_latency_p95:baseline
        expr: |
          histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

  - name: regression
    rules:
      - alert: LatencyRegressionVsBaseline
        expr: |
          histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
          > 2 * job:http_latency_p95:baseline
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: p95 latency is more than double the pre-deploy baseline
```

```promql
# Time-offset comparison: no capture step, compares against the same window
# before the deploy. Set the offset to the deploy time, not a fixed constant.
  sum(rate(http_requests_total{status=~"5.."}[5m]))
> 2 * sum(rate(http_requests_total{status=~"5.."}[5m] offset 1h))
```

The multipliers and deltas here (`2x`, `offset 1h`, `for: 10m`) are **chosen defaults for illustration, not measured values**. Set them from the service's own observed variance: a metric that routinely swings 3x between quiet and peak traffic will page constantly on a 2x rule.

What breaks these rules:

- A baseline captured during an incident encodes the incident as normal, and the alert then stays silent through the recovery it should have flagged. Capture only from a window known to be healthy, and re-capture deliberately after an intentional performance change so the new normal becomes the reference.
- Ratios are unstable at low traffic - a two-request sample doubles easily. Gate the rule with a minimum-volume condition (`and sum(rate(http_requests_total[5m])) > <floor>`) so it cannot fire on noise.
- A baseline-relative alert is meaningless without knowing which change it is relative to. Annotate the deploy in the dashboard and carry the release identifier in the alert annotation, or the responder cannot tell what to roll back.

Use both classes together: absolute thresholds guard the contract with users (an SLO breach is a breach regardless of yesterday's numbers), baseline-relative rules catch the regression a specific change introduced while it is still inside contract.

## Certificate and Credential Expiry Alerts

Expiry is a scheduled outage: the failure time is known in advance, so this alert exists to create lead time, not to detect a symptom. Alerting when the certificate has already expired is a post-mortem, not an alert.

```yaml
- alert: CertificateExpiringSoon
  expr: |
    (probe_ssl_earliest_cert_expiry - time()) / 86400 < 14
  labels:
    severity: warning
  annotations:
    summary: TLS certificate for {{ $labels.instance }} expires in {{ $value | printf "%.0f" }} days
    runbook_url: https://wiki.example.com/runbooks/cert-rotation

- alert: CertificateExpiryImminent
  expr: |
    (probe_ssl_earliest_cert_expiry - time()) / 86400 < 3
  labels:
    severity: critical
  annotations:
    summary: TLS certificate for {{ $labels.instance }} expires in {{ $value | printf "%.0f" }} days - rotate now
```

The 14-day and 3-day windows are **chosen defaults, not measured**. Derive the real ones from the rotation process itself: the warning window must be longer than automated renewal's full retry cycle, so that a firing warning means automation has already failed rather than simply not run yet; the critical window is the point past which only manual rotation still fits. A team whose rotation needs a change-approval board needs a wider window than one running fully automated renewal.

Cover every expiring credential, not only the public TLS endpoint: internal and mTLS workload certificates, the issuing CA (which expires far in the future and therefore falls out of everyone's attention), token-signing and JWT keys, and cloud or registry credentials with a fixed lifetime. Certificate metrics come from an exporter - `probe_ssl_earliest_cert_expiry` from the blackbox exporter probing an endpoint, or `certmanager_certificate_expiration_timestamp_seconds` where an issuer manages them - so each source has to be scraped before its certificates are covered.

Verify this rule differently from the others: an expiry alert that is silent looks exactly like one whose metric is never scraped. Query the expression once with the threshold inflated far past every real expiry (`< 3650`) and confirm it returns one series per certificate expected to be covered. Anything missing from that result is unmonitored, not healthy.

## Severity Levels

| Severity | Response | Example |
|----------|----------|---------|
| `critical` | Page immediately | Service down, data loss |
| `warning` | Investigate soon | High latency, low disk |
| `info` | Check in morning | Unusual traffic pattern |

## Alertmanager Configuration

```yaml
# alertmanager.yml
global:
  slack_api_url: 'https://hooks.slack.com/...'

route:
  receiver: 'slack-notifications'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#alerts'
        send_resolved: true

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'your-key'
```

## Quick Reference

| Field | Purpose |
|-------|---------|
| `expr` | PromQL query |
| `for` | Duration before firing |
| `labels` | Classification (severity) |
| `annotations` | Human-readable info |

| Threshold | Use |
|-----------|-----|
| Error rate > 5% | Critical |
| p95 latency > 1s | Warning |
| Disk < 10% | Critical |
| Memory > 90% | Warning |
