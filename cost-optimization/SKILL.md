---
name: cost-optimization
description: "Cloud FinOps and cost governance: tagging/chargeback, budgets/anomaly detection, rightsizing, commitment strategy (RIs/Savings Plans/CUDs), and unit-cost analysis. Produces a prioritized savings plan with verification gates. Not for cloud architecture or CI/CD."
category: devops
---

# Cost Optimization (Cloud FinOps)

This skill is about reducing cloud spend safely while maintaining reliability and performance.

## Use this skill when

- You need to reduce cloud spend (quick wins + 30/90-day program)
- You need tagging/label standards and cost allocation
- You need budgets, alerts, and anomaly detection
- You need rightsizing and commitment strategy (RIs/Savings Plans/CUDs)
- You want unit economics (cost per request/job/tenant)

## Refuses to do

- Cloud architecture/platform selection (use a cloud architect skill)
- CI/CD or deployment mechanics (use a deployment skill)
- Database-specific tuning and cost/perf tradeoffs (use a database cost/perf skill if available)

## Workflow (Deterministic)

1. Define scope + owner + time window (7/30/90 days).
2. Establish allocation: required tags/labels + coverage plan.
3. Identify top cost drivers (compute, storage, DB, egress, observability).
4. Produce quick wins (idle cleanup, egregious sizing, retention policies).
5. Produce structural wins (autoscaling, purchase commitments, data flow redesign).
6. Verify savings without regressions (SLOs + rollout/rollback).

## Output Contract (Always)

- Top cost drivers with owners and root causes
- A prioritized plan (quick wins + structural wins) with estimated savings ranges
- Risks and verification gates (performance/reliability)
- Tagging/governance recommendations

## Resources (Optional)

- End-to-end playbook: `resources/implementation-playbook.md`
- Tagging standard: `references/tagging-standards.md`
- FinOps guardrails: `references/finops-guardrails.md`
