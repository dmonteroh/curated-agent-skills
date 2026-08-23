---
name: cloud-architect
description: "Designs cloud platform architecture (AWS/Azure/GCP) when a system is being designed for cloud, migrated to it, or connected to on-premises networks: landing zones/accounts, networking, hybrid on-prem connectivity, identity/IAM boundaries, service selection, reliability/DR, and multi-region strategy. Produces architecture diagrams + risk/rollback plans. Does not own CI/CD or deep FinOps tactics."
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

## Output contract

- Architecture summary (1-2 paragraphs) with explicit tradeoffs
- At least one diagram (logical; add network/data flow as needed)
- Risk register (top risks + mitigations)
- RPO/RTO and DR approach (if applicable)
- Implementation plan (phases + verification)
- Open questions (missing inputs or decisions)

## Examples

**Example prompt**
"We are moving analytics and production reporting to Azure. The factory-floor control systems stay on-premises, and the cloud workloads need reliable, low-latency access to them."

**Example output (abridged)**
- Summary: Hub-and-spoke landing zone in the region nearest the plant, one hybrid termination into the hub, per-environment spokes behind it. Control systems stay on-premises behind an integration tier the cloud reads from and never reaches through. Tradeoff: a dedicated circuit over VPN-only, accepting materially higher recurring cost for latency that does not vary with internet conditions, because production reporting depends on this link.
- Architecture decisions: Connectivity — dedicated circuit primary with VPN backup; VPN-only rejected (jitter on a link reporting depends on). Compute — managed PaaS over containers (steady telemetry ingestion, not spiky). The rejected option and its driver are recorded, because reversing the connectivity choice means re-provisioning.
- Diagram(s): logical diagram (on-premises integration tier → two paths → hub → analytics/reporting spokes); a network diagram showing both paths and where each one terminates on-premises.
- Risks and mitigations: a degraded link reads as unexplained application latency, mitigated with per-tunnel link health (tunnel state, BGP session, loss, latency) alerted separately from the application golden signals and never aggregated, because an aggregate hides the loss of redundancy; a single comms room at the plant defeats facility diversity, recorded as accepted residual risk rather than claimed as redundancy.
- RPO/RTO and DR strategy: RPO 15 minutes, RTO 4 hours for reporting, warm standby in the paired region. On the link itself: two paths terminating on different on-premises devices in different facilities, BGP on both, because a static route cannot fail over.
- Implementation plan + verification gates: Phase 0 discovery — order the circuit here rather than at build time, because its lead time is weeks and owns the critical path, and confirm the CIDR plan does not overlap the on-premises estate before the order goes in (gate: order placed, zero overlap) → Phase 1 landing zone + connectivity (gate: drain one path deliberately, traffic moves, advertised prefixes and MTU validated) → Phase 2 data plane (gate: restore drill passes) → Phase 3 reporting (gate: output reconciles with the existing on-premises reports).
- Open questions: measured peak throughput per source; whether the plant has a second physical entry point.

Writing "Phase 1: stand up the landing zone and the circuit" is the common form of this plan and the wrong one: it puts a multi-week procurement inside a build phase and discovers the lead time after the schedule is committed.

## Resources

- Deep-dive playbook + templates: `resources/implementation-playbook.md`
- Provider references index: `references/README.md`
