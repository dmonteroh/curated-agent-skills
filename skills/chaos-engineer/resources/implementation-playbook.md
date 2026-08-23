# Chaos Engineer - Implementation Playbook

Use this playbook to run safe, repeatable chaos experiments with clear hypotheses and controlled blast radius.

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
objective: <what the experiment should learn>
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

Use these references when concrete manifests/tools/examples are needed:

- `references/README.md`
- `references/experiment-template.md`
- `references/game-day-runbook.md`
- `references/infra-quick-reference.md`
- `references/k8s-litmus-chaosengine.md`
- `references/chaos-tools-quick-reference.md`
