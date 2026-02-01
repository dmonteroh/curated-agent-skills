---
name: sre-engineer
description: "Site Reliability Engineering for production systems: define SLIs/SLOs and error budgets, design alerting and runbooks, reduce toil with automation, and improve incident response. Use when you need reliability targets and operational practices (not just dashboards)."
---

# SRE Engineer

This skill is for *reliability management*: turning availability/latency goals into measurable SLOs, actionable alerts, runbooks, and sustained operational improvements.

## Use this skill when

- Defining SLIs/SLOs and error budgets
- Designing alert strategy (burn-rate, paging vs ticketing) and runbooks
- Reducing toil via automation and "self-healing" routines
- Improving incident response (triage, stabilization, postmortems)
- Planning reliability work that balances feature velocity

## Do not use this skill when

- You only need to build a Grafana dashboard JSON (use `grafana-dashboards`)
- You only need chaos experiment manifests (use `chaos-engineer`)
- You only need cloud platform architecture (use `cloud-architect`)

## Workflow (Deterministic)

1. Establish the user-facing critical paths.
2. Define SLIs for each path (availability, latency, correctness).
3. Set SLO targets and compute error budgets.
4. Implement monitoring + alerting that maps to SLO burn (page on symptoms, ticket on causes).
5. Ensure runbooks exist for pages.
6. Measure toil; prioritize automation with ROI.
7. Close the loop: postmortems -> follow-ups -> reduced recurrence.

## Output Contract (Always)

- SLO proposal (SLIs, targets, window, rationale)
- Error budget policy (what happens when budget burns)
- Alerting plan (page vs ticket, burn-rate alerts) + runbook pointers
- A small reliability backlog (top fixes + automation candidates)

## Resources (Optional)

- SLIs/SLOs: `references/slo-sli-management.md`
- Error budgets + burn rates: `references/error-budget-policy.md`
- Monitoring + alerting: `references/monitoring-alerting.md`
- Toil/automation: `references/automation-toil.md`
- Incident response + chaos linkage: `references/incident-chaos.md`
- Playbook: `resources/implementation-playbook.md`
