---
name: cost-optimization
description: "Cloud FinOps and cost governance: tagging/chargeback, budgets/anomaly detection, rightsizing, commitment strategy (RIs/Savings Plans/CUDs), and unit-cost analysis. Produces a prioritized savings plan with verification gates."
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

## Do not use this skill when

- You need cloud architecture/platform selection or migrations
- You need CI/CD or deployment mechanics
- You need database-specific tuning and cost/performance tradeoffs

## Trigger phrases

- "cut cloud spend" or "reduce AWS/GCP/Azure costs"
- "FinOps" or "cost governance"
- "rightsizing" or "reserved instance" or "savings plan"
- "unit cost" or "cost per request/tenant"

## Inputs to collect

- Billing scope (accounts/subscriptions/projects, envs, owners)
- Time window (last 7/30/90 days)
- Cost targets (budget, % reduction, unit-cost goal)
- Constraints (SLOs, compliance, procurement limits)
- Current tagging/labeling coverage and budget/alert setup

## Workflow (Deterministic)

1. Confirm scope, owners, and constraints.
   - Output: scoped summary with success criteria and missing inputs.
   - Decision: if scope/constraints are unclear, ask for the missing details before continuing.
2. Establish cost allocation baseline (tags/labels, budgets, anomaly alerts).
   - Output: required tags/labels list + current coverage gaps.
3. Identify top cost drivers by category and owner.
   - Output: top drivers table with root causes and affected services.
4. Build quick wins backlog (idle cleanup, egregious sizing, retention policies).
   - Output: prioritized quick wins with estimated savings ranges and risk level.
5. Build structural wins plan (autoscaling, commitment strategy, data flow changes).
   - Decision: only recommend commitments after stable utilization evidence.
   - Output: structural initiatives with prerequisites and timelines.
6. Define verification gates (performance, reliability, cost attribution).
   - Output: verification checklist and rollback steps.
7. Compile the final savings plan and reporting format.
   - Output: consolidated plan with owners, timelines, and verification gates.

## Common pitfalls

- Recommending commitments before usage stabilizes.
- Ignoring tag/label gaps that prevent attribution.
- Chasing small wins while top drivers stay untouched.
- Cutting observability without measuring impact on incident response.
- Skipping verification gates and rollback plans.

## Output Contract (Always)

- Top cost drivers with owners and root causes
- A prioritized plan (quick wins + structural wins) with estimated savings ranges
- Risks and verification gates (performance/reliability)
- Tagging/governance recommendations

## Reporting format

- Summary (scope, targets, constraints)
- Top cost drivers (category, owner, root cause)
- Savings plan (quick wins + structural wins with estimates)
- Risks + verification gates (SLOs, rollback)
- Tagging/governance actions

## Examples

**Example request**

"We need to cut our AWS bill by 20% in 60 days without hurting reliability. We have mixed prod and non-prod workloads and incomplete tagging."

**Example response (excerpt)**

- Scope: 3 accounts (prod/staging/dev), 60-day window, target 20% reduction
- Top drivers: EC2 on-demand in prod, CloudWatch logs, data egress from analytics
- Quick wins: shutdown non-prod nights/weekends, log retention to 14 days
- Structural wins: autoscaling for batch workers, Savings Plan after 30 days stable usage
- Verification: latency/error budgets, rollback plan for scaling changes

## Trigger test

- "Can you help us reduce cloud spend and set up FinOps guardrails?"
- "We need a rightsizing and Savings Plan strategy with verification steps."

## Resources (Optional)

- References index: `references/README.md`
- End-to-end playbook: `resources/implementation-playbook.md`
