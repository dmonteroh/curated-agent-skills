---
name: cloud-architect
description: "Design cloud platform architecture (AWS/Azure/GCP): landing zones/accounts, networking, hybrid on-prem connectivity, identity/IAM boundaries, service selection, reliability/DR, and multi-region strategy. Produces architecture diagrams + risk/rollback plans. Does not own CI/CD or deep FinOps tactics."
metadata:
  category: devops
---
# Cloud Architect

## Use this skill when

- Designing a cloud system or migrating to cloud
- Choosing services and shaping the platform (networking, IAM, data, compute)
- Defining multi-region / DR strategy (RPO/RTO) and failure modes
- Establishing environment boundaries and a landing zone
- Connecting an on-premises datacenter, colo, or branch network to cloud (hybrid connectivity)

## Do not use this skill when

- The task is limited to CI/CD pipeline design or deployment automation
- The task is strictly IaC module mechanics or Terraform/OpenTofu state workflows
- The task is only secrets backend setup/rotation details
- The task is purely cost optimization without architecture changes
- The task is on-premises-only network engineering with no cloud side (LAN design, router/switch configuration, physical circuit procurement)
- A hybrid link exists and is failing right now — this skill designs the link and decides what to alert on; live read-only triage of a session or interface is a different job with a different output
- A device configuration is written and needs reviewing before it is pushed into a change window

## Required inputs

- Workload overview (users, traffic patterns, data volume, latency needs)
- Target cloud(s) and any constraints (residency, compliance, contractual)
- Existing systems or migrations in scope
- Availability and recovery objectives (SLOs, RPO/RTO targets)
- Security requirements (data classification, identity model, audit needs)

## Workflow

1. Clarify goals and constraints (SLOs, compliance, residency, budget guardrails).
   - Output: constraints list + success criteria.
2. Define boundaries (system boundary + trust boundaries + data classification).
   - Output: boundary summary + data classification table.
3. Select the dominant platform pattern (serverless vs containers vs VM-based).
   - Decision: If workload is spiky/event-driven and ops-light, prefer serverless; if portability/control dominates, prefer containers; if legacy/strict kernel needs, prefer VMs.
   - Decision: If the provider is not fixed, or the design must stay portable, map candidate compute/storage/data services across providers with `references/service-equivalence.md` before committing to one.
   - Output: chosen pattern + rationale + rejected options.
4. Design the landing zone + environment layout (prod vs non-prod, accounts/subscriptions/projects).
   - Output: environment map + isolation rationale.
5. Design networking (CIDR plan, ingress/egress, private connectivity, DNS).
   - Decision: If compliance requires private connectivity, include private endpoints/links; otherwise document public ingress with protections.
   - Decision: If any workload must reach an on-premises datacenter, pick the hybrid connectivity type (internet-routed VPN vs dedicated circuit) and the hub topology before CIDRs are frozen, and confirm no CIDR overlaps with on-premises: `references/hybrid-connectivity.md`. A dedicated circuit's lead time is ordered in discovery, not at build time.
   - Output: network diagram notes + CIDR plan (+ hybrid connectivity decision where on-premises is in scope).
6. Design identity (human + workload identity; least privilege; break-glass).
   - Output: IAM model summary + break-glass approach.
7. Design data/state (managed first; backups/PITR; lifecycle/retention).
   - Decision: If data residency or latency needs are strict, pin storage/DB regions and document replication limits.
   - Output: data services list + backup/retention plan.
8. Design reliability/DR (multi-AZ by default; RPO/RTO; test restores).
   - Decision: If RPO/RTO requires cross-region, pick DR tier (pilot light/warm standby/active-active) and justify.
   - Decision: If a hybrid link carries production traffic, require two paths terminating on different on-premises devices in different facilities, dynamic routing (BGP) rather than static routes, and a drill that proves failover. A single tunnel is not redundancy.
   - Output: DR strategy + target RPO/RTO.
9. Define observability requirements (golden signals, correlation IDs, alert boundaries).
   - Decision: If a hybrid link is in scope, add per-tunnel link-health signals (tunnel state, BGP session, loss, latency) to the alerting scope — application golden signals do not cover the link, and a degraded link reads as unexplained app latency: `references/hybrid-connectivity.md`.
   - Output: observability checklist + alerting scope.
10. Produce a phased implementation plan + verification gates.
   - Output: phased plan with verification criteria.

## Common pitfalls

- Mixing multiple platform patterns without a clear reason
- Ignoring IAM boundary design until late in the plan
- Selecting services before confirming data residency or compliance constraints
- Under-specifying RPO/RTO and restore validation

## Output contract

- Architecture summary (1-2 paragraphs) with explicit tradeoffs
- At least one diagram (logical; add network/data flow as needed)
- Risk register (top risks + mitigations)
- RPO/RTO and DR approach (if applicable)
- Implementation plan (phases + verification)
- Open questions (missing inputs or decisions)

## Examples

**Example prompt**
"Design the AWS architecture for a multi-tenant analytics platform with EU data residency and 99.9% availability."

**Example output (abridged)**
- Summary: Multi-tenant analytics platform on AWS, tenant-isolated schemas in a shared Aurora PostgreSQL cluster, S3 + Glue as the data lake, all resources pinned to eu-west-1/eu-central-1 for residency. Tradeoff: shared-cluster multi-tenancy over silo-per-tenant to control operating cost, accepting a noisy-neighbor risk mitigated by per-tenant connection pooling and Performance Insights.
- Architecture decisions: Compute — ECS Fargate over Lambda (ingestion load is steady, not spiky); EKS rejected (no in-house Kubernetes operating experience). Data — Aurora PostgreSQL over DynamoDB (workload needs ad hoc analytical joins).
- Diagram(s): logical diagram (API Gateway → Fargate → Aurora → S3/Glue → BI layer); a data-flow diagram tracing one tenant's request path through the tenant-isolation boundary.
- Risks and mitigations: cross-tenant data leakage via the shared cluster, mitigated with row-level security and per-tenant IAM roles; EU residency drift from a default multi-region bucket policy, mitigated with an SCP denying non-EU regions.
- RPO/RTO and DR strategy: RPO 15 minutes via Aurora continuous backup; RTO 1 hour via warm standby in eu-central-1; quarterly restore drill.
- Implementation plan + verification gates: Phase 0 discovery (2wk) → Phase 1 landing zone + IAM (2wk, gate: SCP denies non-EU regions) → Phase 2 data plane (3wk, gate: restore drill passes) → Phase 3 app plane (3wk, gate: load test at 2x peak) → Phase 4 cutover (1wk, gate: tenant smoke tests pass).
- Open questions: tenant count at launch (affects schema-per-tenant vs pooled-schema); whether any tenant requires residency outside the EU.

## Resources

- Deep-dive playbook + templates: `resources/implementation-playbook.md`
- Provider references index: `references/README.md`
