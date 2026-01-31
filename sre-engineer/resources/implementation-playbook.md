# SRE Engineer - Implementation Playbook

Use this playbook when you need a deterministic SRE deliverable set (SLOs, error budget policies, alerting/runbooks, and an automation plan).

## Inputs

- Service/system name + environment.
- Critical user journeys.
- Current telemetry (metrics/logs/traces) and incident history.
- Expected load profile and dependencies.

## Step 1: Define SLIs

Pick SLIs that represent *user impact*.

Common:

- Availability: proportion of successful requests/events.
- Latency: p95/p99 under a threshold.
- Correctness: business-level success (payments completed, sessions established).

## Step 2: Set SLOs

- Prefer a small number of SLOs per critical path (1-3).
- Pick a window (often 28/30 days) and justify the target.

## Step 3: Error Budget Policy

Define what happens as budget burns.

- Healthy: normal feature velocity.
- Warning: increase review rigor; focus on reliability bugs.
- Critical/exhausted: freeze risky releases; pay down reliability issues.

## Step 4: Alerting Strategy

- Page on symptoms (SLO burn, availability/latency).
- Ticket on causes (resource utilization, noisy errors).
- Every page must have a runbook.

## Step 5: Runbooks

Minimum runbook contents:

- What does the alert mean?
- Immediate mitigations (rollback, scale, disable feature)
- How to confirm recovery
- Escalation contacts and links

## Step 6: Toil & Automation

- Create a toil inventory.
- Prioritize by ROI: time saved x frequency / difficulty.
- Automate recurring mitigations and make them safe-by-default.

## Step 7: Continuous Improvement Loop

- For every incident: blameless postmortem + follow-ups.
- Track recurrence rate and MTTR.
- Keep an explicit reliability backlog.
