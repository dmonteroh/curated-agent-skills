---
name: chaos-engineer
description: Design and run safe chaos experiments (failure injection + game days) to validate resilience and reduce blast radius. Produces hypotheses, steady-state signals, rollback gates, and experiment specs. Use when resilience is uncertain or before high-risk changes.
---

# Chaos Engineer

Chaos engineering is *controlled failure injection* with explicit hypotheses, safety gates, and learnings turned into remediation work.

## Use this skill when

- You want to validate resilience (timeouts/retries/circuit breakers/backpressure)
- You need a game day plan and runbook
- You need a failure injection experiment spec (staging/canary/prod)
- You need to reduce blast radius or improve recovery (MTTR)

## Do not use this skill when

- You are still missing basic observability (you can’t define steady state)
- The change is low-risk and easily reversible

## Safety Rules (Non-Negotiable)

- Define steady state metrics before injecting failure.
- Start small and isolate blast radius.
- Have a kill switch + rollback triggers.
- Run one variable at a time until maturity is proven.

## Workflow (Deterministic)

1. Map critical paths and dependencies.
2. Define hypothesis + steady state + guardrails.
3. Choose blast radius (env, scope, % traffic, duration).
4. Define rollback triggers and a kill switch.
5. Execute, observe, stop on guardrails.
6. Document findings and convert into fixes.

## Output Contract (Always)

- Experiment spec (hypothesis, steady state, blast radius, safety/rollback, success criteria)
- Execution plan (steps + stop conditions)
- Findings + remediation actions

## Resources (Optional)

- End-to-end playbook + templates: `resources/implementation-playbook.md`
- Experiment design deep dive: `references/experiment-design.md`
- Game day facilitation: `references/game-days.md`
- Infra failure patterns: `references/infrastructure-chaos.md`
- Kubernetes experiments: `references/kubernetes-chaos.md`
- Tools and automation patterns: `references/chaos-tools.md`
