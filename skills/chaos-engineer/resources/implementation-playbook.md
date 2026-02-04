# Chaos Engineer - Implementation Playbook

Use this playbook to run safe, repeatable chaos experiments with clear hypotheses and controlled blast radius.

## Golden Rules

- Start in non-prod. Earn the right to run in prod.
- One variable at a time (until the system and team are mature).
- Define a steady state metric set before injecting failure.
- Have a kill switch and rollback plan before starting.

## Inputs (Collect First)

- System overview + critical user journeys.
- Dependencies (DB/cache/queues/external APIs) and known failure modes.
- Observability readiness: dashboards/alerts/log correlation.
- Environment: staging/canary/prod, traffic level, time window.
- Safety controls: feature flags, rate limiting, circuit breakers, deploy rollback.

## Experiment Workflow (Deterministic)

1) Define hypothesis
- "Given <steady state>, when <failure>, then <expected behavior>, measured by <signals>."

2) Define steady state
- Latency (p95/p99), error rate, saturation, throughput.
- Business KPI if relevant (successful checkouts, sign-ins).

3) Define blast radius
- Environment, service scope, % of traffic/pods, duration.

4) Define safety & rollback
- Kill switch.
- Automatic rollback triggers (SLO burn, error spikes, saturation).
- Rollback time limit target (e.g., 30s-2m depending on system).

5) Execute
- Start small (1 pod, 1 instance, 1% traffic).
- Observe and record; stop if rollback triggers fire.

6) Learn & remediate
- Write findings: what failed, why, and what to fix.
- Turn remediations into trackable tasks.

## Experiment Types (Pick One)

- Latency injection (dependency/network)
- Packet loss / jitter
- Dependency outage / blackhole
- Resource exhaustion (CPU/memory/disk)
- Pod kill / node drain
- Zone failure simulation (only after lower-level maturity)

## Output Template (Experiment Spec)

```yaml
name: <short-name>
objective: <what we want to learn>
hypothesis: <given/when/then>

steady_state:
  time_window: <e.g. 30m baseline>
  metrics:
    - name: <metric>
      query: <promql/etc>
      threshold: <guardrail>

blast_radius:
  environment: <staging|canary|prod>
  scope: <service/pods/instances>
  traffic_percent: <0-100>
  duration_seconds: <n>

injection:
  type: <latency|packet_loss|pod_kill|cpu_hog|...>
  target: <dependency/service>
  parameters: {}

safety:
  kill_switch: <how to stop>
  rollback_triggers:
    - <guardrail>
  rollback_time_limit_seconds: <n>

success_criteria:
  - <expected behavior>

results:
  observed: <notes>
  issues_found:
    - <issue>
  actions:
    - <fix>
```

## Reference Files

Use these when you need concrete manifests/tools/examples:

- `references/experiment-design.md`
- `references/game-days.md`
- `references/infrastructure-chaos.md`
- `references/kubernetes-chaos.md`
- `references/chaos-tools.md`
