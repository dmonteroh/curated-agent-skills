---
name: sre-engineer
description: "Site Reliability Engineering for production systems: define SLIs/SLOs and error budgets, design alerting and runbooks, reduce toil with automation, and improve incident response. Use when you need reliability targets and operational practices (not just dashboards)."
category: observability
---
# SRE Engineer

This skill delivers *reliability management*: turning availability/latency goals into measurable SLIs/SLOs, actionable alerting, runbooks, and a sustainable improvement loop.

## Use this skill when

- Defining SLIs/SLOs and error budgets
- Designing alert strategy (burn-rate, paging vs ticketing) and runbooks
- Reducing toil via automation and "self-healing" routines
- Improving incident response (triage, stabilization, postmortems)
- Planning reliability work that balances feature velocity

**Activation cues**

- "Define SLOs/error budgets for this service"
- "We need paging rules tied to reliability targets"
- "Reduce on-call toil and automate mitigation"
- "Build an incident response + postmortem loop"
- "Turn reliability goals into concrete backlog items"

## Do not use this skill when

- You only need a dashboard or visualization without SLOs or alerting design
- You only need chaos experiment manifests without reliability targets
- You only need cloud platform architecture without operational practices

## Inputs to request

- Service/system name, environment, and owners
- Critical user journeys and traffic mix
- Current telemetry (metrics/logs/traces) and existing alerts
- Incident history or known failure modes
- Business or regulatory constraints on availability/latency
- Deployment cadence and dependency map
- On-call coverage and escalation expectations

## Constraints

- Keep the workflow self-contained; do not require other skills or tools.
- Avoid time-sensitive assumptions and external network dependencies.

## Workflow (Deterministic)

1. **Scope critical paths.**
   - Decision: if critical paths are unclear, ask for the top 3 journeys and traffic mix.
   - Output: ordered list of critical paths + assumptions.
2. **Define SLIs and measurement.**
   - Decision: if telemetry is missing, propose an instrumentation plan and provisional SLIs.
   - Output: SLI table (name, query/source, user impact).
3. **Set SLOs and error budgets.**
   - Decision: if business tolerance is unknown, provide 2–3 targets with tradeoffs and ask for a choice.
   - Output: SLO targets, window, and calculated error budgets.
4. **Design alerting + runbooks.**
   - Decision: if no on-call coverage exists, default to ticketing until coverage is defined.
   - Output: alert rules (page vs ticket) and required runbooks.
5. **Analyze toil and automation ROI.**
   - Decision: if toil data is missing, estimate from on-call logs and confirm with the user.
   - Output: toil inventory + automation candidates with ROI.
6. **Strengthen incident response loop.**
   - Decision: if postmortems are ad hoc, propose a lightweight template and follow-up tracker.
   - Output: incident response improvements and follow-up cadence.
7. **Deliver reliability backlog.**
   - Output: prioritized backlog with owners, effort, and impact.

## Common pitfalls

- Paging on causes instead of user-facing symptoms
- Choosing SLOs without evidence or business alignment
- Defining too many SLIs per critical path
- Alerting without clear runbook mitigations
- Automating responses without safe rollback

## Output Contract (Always)

Provide a response with the following sections in order:

1. **Summary** (1–3 sentences)
2. **SLO Proposal** (SLIs, targets, window, rationale)
3. **Error Budget Policy** (actions at healthy/warning/critical)
4. **Alerting + Runbooks** (page vs ticket, burn-rate alerts, runbook list)
5. **Toil + Automation** (top toil drivers, automation ROI)
6. **Incident Response Improvements** (process + metrics)
7. **Reliability Backlog** (ranked fixes + owners)
8. **Open Questions / Assumptions**

## Examples

**Example output snippet**

- Summary: Reliability plan for payments API focused on checkout latency and success rate.
- SLO Proposal: Availability ≥ 99.9% (30d); Latency p95 ≤ 400ms (30d); rationale included.
- Error Budget Policy: Healthy → normal releases; Warning → add reliability review; Critical → pause risky deploys.

## References

- Index: `references/README.md`
- SLIs/SLOs: `references/sli-definition-patterns.md`, `references/slo-calculations.md`
- Error budgets: `references/error-budget-fundamentals.md`, `references/burn-rate-alerting.md`, `references/error-budget-policy-template.md`
- Monitoring + alerting: `references/monitoring-golden-signals.md`, `references/alert-design-examples.md`, `references/runbook-template.md`
- Toil/automation: `references/toil-definition-inventory.md`, `references/self-healing-automation.md`, `references/runbook-automation.md`
- Incident response + chaos: `references/incident-response-framework.md`, `references/postmortem-template.md`, `references/chaos-experiment-design.md`
- Implementation playbook: `references/implementation-playbook.md`
