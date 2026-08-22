# SRE Engineer - Implementation Playbook

Use this playbook when you need a deterministic SRE deliverable set (SLOs, error budget policies, alerting/runbooks, and an automation plan).

## Inputs

- Service/system name + environment.
- Critical user journeys.
- Current telemetry (metrics/logs/traces) and incident history.
- Expected load profile and dependencies.

## Workflow Detail

For SLI/SLO definition, error budget policy, alerting, runbooks, toil automation, and the incident response loop, follow SKILL.md's Workflow steps 2-7. This playbook adds:

- Prefer a small number of SLOs per critical path (1-3).
- Page on symptoms (SLO burn, availability/latency). Ticket on causes (resource utilization, noisy errors).
- Minimum runbook contents: what the alert means, immediate mitigations (rollback, scale, disable feature), how to confirm recovery, escalation contacts and links.
- Prioritize toil automation by ROI: time saved x frequency / difficulty.
