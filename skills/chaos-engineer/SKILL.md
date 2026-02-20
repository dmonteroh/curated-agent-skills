---
name: chaos-engineer
description: "Design and run safe chaos experiments (failure injection + game days) to validate resilience and reduce blast radius. Produces hypotheses, steady-state signals, rollback gates, and experiment specs. Use when resilience is uncertain or before high-risk changes."
metadata:
  category: observability
---
# Chaos Engineer

Provides controlled failure injection with explicit hypotheses, safety gates, and learnings turned into remediation work.

## Use this skill when

- Validate resilience (timeouts/retries/circuit breakers/backpressure)
- Produce a game day plan and runbook
- Produce a failure injection experiment spec (staging/canary/prod)
- Reduce blast radius or improve recovery (MTTR)

## Do not use this skill when

- Steady-state signals cannot be defined because observability is missing
- The change is low-risk and easily reversible

## Required inputs

- System scope and critical path (services, dependencies, owners)
- Failure mode to test (latency, packet loss, dependency outage, resource exhaustion)
- Environments available and allowable blast radius
- Observability sources for steady state (metrics, logs, traces)
- Rollback mechanisms and on-call/communications expectations

If any required inputs are missing, the agent requests them before proceeding.

## Safety Rules (Non-Negotiable)

- Define steady state metrics before injecting failure.
- Start small and isolate blast radius.
- Have a kill switch + rollback triggers.
- Run one variable at a time until maturity is proven.

## Workflow (Deterministic)

1. Map critical paths and dependencies.
   - Output: scoped system map + dependency list.
2. Define hypothesis, steady state signals, and guardrails.
   - Output: hypothesis statement + steady state metrics + guardrail thresholds.
   - Decision: if steady state metrics cannot be defined, stop and request observability gaps.
3. Select failure mode and blast radius.
   - Output: failure injection spec (mode, target, environment, % traffic, duration).
   - Decision: if production is in scope and rollback/kill switch is missing, stop and require one.
4. Define safety plan and rollback workflow.
   - Output: rollback triggers, kill switch steps, communications plan.
5. Execute and monitor.
   - Output: execution log with ordered steps, guardrail observations, and stop/continue decision.
   - Decision: if any guardrail breaches, rollback immediately.
6. Capture findings and remediation.
   - Output: findings summary + prioritized remediation tickets.

## Common pitfalls

- Injecting failures without steady state metrics or clear SLOs.
- Expanding blast radius before validating smaller scopes.
- Missing rollback automation or unclear ownership during execution.
- Treating a chaos experiment as a load test without hypotheses.

## Output Contract (Always)

- Experiment spec (hypothesis, steady state, blast radius, safety/rollback, success criteria)
- Execution plan (steps + stop conditions)
- Findings + remediation actions

Reporting format (use this in the final response):

```
## Chaos Experiment Report
- Scope:
- Hypothesis:
- Steady State Signals:
- Guardrails:
- Failure Injection:
- Blast Radius:
- Rollback Plan:
- Execution Steps:
- Stop Conditions:
- Findings:
- Remediation Actions:
```

## Examples

**Example input**
- Goal: Validate retry behavior when the payment gateway is unavailable.
- Scope: Checkout service + gateway client.
- Environment: Staging only.
- Failure mode: 100% gateway timeout for 5 minutes.

**Example output (abbreviated)**
```
## Chaos Experiment Report
- Scope: Checkout service + payment gateway client
- Hypothesis: When the gateway times out, retries activate and users receive a friendly failure within 2s.
- Steady State Signals: Error rate < 0.1%, P95 latency < 400ms
- Guardrails: Error rate > 2%, latency > 800ms
- Failure Injection: Force gateway timeout responses
- Blast Radius: Staging, 100% traffic, 5 minutes
- Rollback Plan: Disable fault injection flag; verify error rate normalizes
- Execution Steps: Pre-check steady state, enable flag, monitor, disable
- Stop Conditions: Guardrail breach or manual kill switch
- Findings: Retries succeeded, user errors returned cleanly
- Remediation Actions: Add circuit breaker metrics dashboard
```

## Resources (Optional)

- End-to-end playbook + templates: `resources/implementation-playbook.md`
- Reference index: `references/README.md`
