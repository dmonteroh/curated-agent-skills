---
name: cloud-architect
description: "Design cloud platform architecture (AWS/Azure/GCP): landing zones/accounts, networking, identity/IAM boundaries, service selection, reliability/DR, and multi-region strategy. Produces architecture diagrams + risk/rollback plans. Does not own CI/CD or deep FinOps tactics."
metadata:
  category: devops
---
# Cloud Architect

Provides guidance for designing cloud platform architecture: boundaries, networks, identity, reliability, and service selection.

## Use this skill when

- Designing a cloud system or migrating to cloud
- Choosing services and shaping the platform (networking, IAM, data, compute)
- Defining multi-region / DR strategy (RPO/RTO) and failure modes
- Establishing environment boundaries and a landing zone

## Do not use this skill when

- The task is limited to CI/CD pipeline design or deployment automation
- The task is strictly IaC module mechanics or Terraform/OpenTofu state workflows
- The task is only secrets backend setup/rotation details
- The task is purely cost optimization without architecture changes

## Required inputs

- Workload overview (users, traffic patterns, data volume, latency needs)
- Target cloud(s) and any constraints (residency, compliance, contractual)
- Existing systems or migrations in scope
- Availability and recovery objectives (SLOs, RPO/RTO targets)
- Security requirements (data classification, identity model, audit needs)

## Workflow (Deterministic)

1. Clarifies goals and constraints (SLOs, compliance, residency, budget guardrails).
   - Output: constraints list + success criteria.
2. Defines boundaries (system boundary + trust boundaries + data classification).
   - Output: boundary summary + data classification table.
3. Selects the dominant platform pattern (serverless vs containers vs VM-based).
   - Decision: If workload is spiky/event-driven and ops-light, prefer serverless; if portability/control dominates, prefer containers; if legacy/strict kernel needs, prefer VMs.
   - Output: chosen pattern + rationale + rejected options.
4. Designs landing zone + environment layout (prod vs non-prod, accounts/subscriptions/projects).
   - Output: environment map + isolation rationale.
5. Designs networking (CIDR plan, ingress/egress, private connectivity, DNS).
   - Decision: If compliance requires private connectivity, include private endpoints/links; otherwise document public ingress with protections.
   - Output: network diagram notes + CIDR plan.
6. Designs identity (human + workload identity; least privilege; break-glass).
   - Output: IAM model summary + break-glass approach.
7. Designs data/state (managed first; backups/PITR; lifecycle/retention).
   - Decision: If data residency or latency needs are strict, pin storage/DB regions and document replication limits.
   - Output: data services list + backup/retention plan.
8. Designs reliability/DR (multi-AZ by default; RPO/RTO; test restores).
   - Decision: If RPO/RTO requires cross-region, pick DR tier (pilot light/warm standby/active-active) and justify.
   - Output: DR strategy + target RPO/RTO.
9. Defines observability requirements (golden signals, correlation IDs, alert boundaries).
   - Output: observability checklist + alerting scope.
10. Produces a phased implementation plan + verification gates.
   - Output: phased plan with verification criteria.

## Common pitfalls to avoid

- Mixing multiple platform patterns without a clear reason
- Ignoring IAM boundary design until late in the plan
- Selecting services before confirming data residency or compliance constraints
- Under-specifying RPO/RTO and restore validation

## Output Contract (Always)

- Architecture summary (1-2 paragraphs) with explicit tradeoffs
- At least one diagram (logical; add network/data flow as needed)
- Risk register (top risks + mitigations)
- RPO/RTO and DR approach (if applicable)
- Implementation plan (phases + verification)
- Open questions (missing inputs or decisions)

## Reporting format

- Summary
- Architecture decisions (options + chosen)
- Diagram(s)
- Risks and mitigations
- RPO/RTO and DR strategy
- Implementation plan + verification gates
- Open questions

## Examples

**Example prompt**
"Design the AWS architecture for a multi-tenant analytics platform with EU data residency and 99.9% availability."

**Example output (abridged)**
- Summary: <1-2 paragraphs>
- Architecture decisions: <options, chosen, tradeoffs>
- Diagram(s): <logical + data flow>
- Risks and mitigations: <top risks>
- RPO/RTO and DR strategy: <targets and tier>
- Implementation plan + verification gates: <phased plan>
- Open questions: <unknowns>

## Resources (Optional)

- Deep-dive playbook + templates: `resources/implementation-playbook.md`
- Provider references index: `references/README.md`
