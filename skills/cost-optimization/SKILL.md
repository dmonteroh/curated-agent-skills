---
name: cost-optimization
description: "Cloud FinOps cost governance for reducing cloud spend while maintaining reliability. Use when teams need tagging/chargeback, budgets/anomaly detection, rightsizing, commitment strategy (RIs/Savings Plans/CUDs), or unit-cost analysis. Produces a prioritized savings plan with verification gates."
category: devops
---
# Cost Optimization (Cloud FinOps)

Provides a deterministic workflow to reduce cloud spend safely while maintaining reliability and performance.

## Use this skill when

- A team needs to reduce cloud spend (quick wins + longer-term program)
- A team needs tagging/label standards and cost allocation
- A team needs budgets, alerts, and anomaly detection
- A team needs rightsizing and commitment strategy (RIs/Savings Plans/CUDs)
- A team wants unit economics (cost per request/job/tenant)

## Do not use this skill when

- The request is for cloud architecture/platform selection or migrations
- The request is for CI/CD or deployment mechanics
- The request is for database-specific tuning and cost/performance tradeoffs

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
   - Decision: if tag coverage is too low to attribute costs, define the tagging remediation plan before optimization.
3. Identify top cost drivers by category and owner.
   - Output: top drivers table with root causes and affected services.
   - Decision: if billing data is unavailable, request a cost export or dashboard access before continuing.
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

## Resources (Optional)

- References index: `references/README.md`
- End-to-end playbook: `resources/implementation-playbook.md`
