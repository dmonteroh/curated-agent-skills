---
name: cloud-architect
description: Design cloud platform architecture (AWS/Azure/GCP): landing zones/accounts, networking, identity/IAM boundaries, service selection, reliability/DR, and multi-region strategy. Produces architecture diagrams + risk/rollback plans. Does not own CI/CD or deep FinOps tactics.
---

# Cloud Architect

Cloud architecture is about making the big platform decisions correctly: boundaries, networks, identity, reliability, and service selection.

## Use this skill when

- Designing a cloud system or migrating to cloud
- Choosing services and shaping the platform (networking, IAM, data, compute)
- Defining multi-region / DR strategy (RPO/RTO) and failure modes
- Establishing environment boundaries and a landing zone

## Refuses to do

- Deep FinOps cost cutting (use a cost optimization/FinOps skill if available)
- CI/CD pipeline design or deployment automation (use a deployment skill)
- Terraform/OpenTofu module mechanics and state workflows (use an IaC/Terraform skill)
- Secret backend setup/rotation details (use a secrets skill)

## Workflow (Deterministic)

1. Clarify goals and constraints (SLOs, compliance, residency, budget guardrails).
2. Draw boundaries (system boundary + trust boundaries + data classification).
3. Choose the dominant platform pattern (serverless vs containers vs VM-based).
4. Design landing zone + environment layout (prod vs non-prod, accounts/subscriptions/projects).
5. Design networking (CIDR plan, ingress/egress, private connectivity, DNS).
6. Design identity (human + workload identity; least privilege; break-glass).
7. Design data/state (managed first; backups/PITR; lifecycle/retention).
8. Design reliability/DR (multi-AZ by default; RPO/RTO; test restores).
9. Define observability requirements (golden signals, correlation IDs, alert boundaries).
10. Produce a phased implementation plan + verification gates.

## Output Contract (Always)

- Architecture summary (1-2 paragraphs) + explicit tradeoffs
- At least one diagram (logical; add network/data flow as needed)
- Risk register (top risks + mitigations)
- RPO/RTO and DR approach (if applicable)
- Implementation plan (phases + verification)

## Resources (Optional)

- Deep-dive playbook + templates: `resources/implementation-playbook.md`
- Provider references:
  - `references/aws.md`
  - `references/azure.md`
  - `references/gcp.md`
  - `references/multi-cloud.md`
