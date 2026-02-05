# Cost Optimization - Implementation Playbook

Use this playbook when you need a concrete cost-reduction plan, a cost review ritual, or governance mechanics that stick.

## Inputs (Collect Before Recommending Changes)

- Billing scope: accounts/subscriptions/projects, environments, and owners.
- Time window: last 7/30/90 days, plus any known release events.
- KPI targets: absolute budget, % reduction, or unit economics (cost per request/tenant).
- Constraints: performance/SLOs, compliance, procurement limits, reserved capacity commitments.

## Deliverables (Pick What Fits)

- Top cost drivers list with owners and expected savings.
- Short-term action plan (quick wins), plus longer-term program (structural wins).
- Tagging/labeling policy + coverage plan.
- A "stop the bleed" checklist for incident-level cost spikes.
- Verification checklist (ensure savings without regressions).

## Workflow

### 1) Establish Visibility (Initial)

- Define required tags/labels and owners.
- Ensure cost allocation works at the dimension you need (team/service/env/tenant).
- Set budgets and alerts (including anomaly detection if available).

### 2) Identify The Big Rocks (Baseline)

Ask: which *category* dominates?

- Compute
- Storage
- Databases
- Data transfer / egress
- Observability (logs/metrics/traces)
- Managed services (queues, serverless, search)

### 3) Quick Wins (Short-Term)

- Turn off idle resources (especially non-prod).
- Delete orphaned resources (disks, snapshots, IPs, load balancers).
- Fix egregious sizing (4x+ over-provisioned instances).
- Apply lifecycle policies for logs and object storage.
- Reduce high-cardinality metrics and noisy logs.

### 4) Structural Wins (Long-Term)

- Autoscaling for variable workloads.
- Commit to capacity only after utilization evidence.
- Data flow redesign to reduce cross-zone/region chatter.
- Move to managed services where ops overhead is the hidden cost.
- Introduce unit-cost metrics (cost per request/job/tenant).

### 5) Verify And Lock In

- Performance regression checks (latency/error rates/saturation).
- Reliability checks (backups/restore, failover behavior).
- Cost checks (show deltas, validate billing categories, confirm tag attribution).
- Document the change and add a recurring review.

## Output Templates

### Cost Driver Summary

- Scope: <accounts/projects/envs>
- Window: <date range>
- Top 5 drivers:
  - <driver> - <cost> - owner: <team> - why: <root cause>
- Recommended actions:
  - <action> - expected savings: <range> - risk: <low/med/high> - verification: <how>

### Quick Wins Backlog (Example Columns)

- Item
- Owner
- Est. savings
- Risk
- Prereqs
- Verification
- Status

## Tagging Standards

See `references/tagging-standards.md`.
