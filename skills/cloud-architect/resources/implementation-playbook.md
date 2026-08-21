# Cloud Architect - Implementation Playbook

This playbook is an optional deep-dive used when the task needs concrete deliverables (diagrams, IaC skeletons, checklists, runbooks). Keep the skill standalone: do not assume other skills exist.

## Default Deliverables

Pick the smallest set that satisfies the task.

- Architecture diagram(s): at least one logical view; add network / data flow views as needed.
- A short decision summary: what is being built, why, and the main tradeoffs.
- A risk register: top 3-7 risks + mitigations.
- An implementation plan: phases + verification steps.
- IaC approach: Terraform/OpenTofu modules (preferred) or cloud-native IaC.

## Discovery Checklist (Ask These First)

- Workload: request volume, latency, throughput, peak-to-average, data size, growth.
- SLOs: availability, latency percentiles, recovery objectives (RPO/RTO), durability.
- Security/compliance: data classification, encryption requirements, audit needs, residency.
- Deployment model: single cloud vs multi-cloud, regions, envs (dev/stage/prod), tenants.
- Operational constraints: team skillset, on-call maturity, budget targets, timeline.

## Additional Deep-Dive Steps

For steps 1-8 (boundaries, platform pattern, landing zone, networking, identity, data, reliability/DR, observability), follow SKILL.md's Workflow. This playbook adds:

### 9) Cost & Capacity

- Establish budget guardrails and cost allocation.
- Right-size; prefer autoscaling where possible.
- Separate cost experiments from production changes.

## Review Checklist (Pre-Implementation)

- Security
  - Encryption in transit and at rest accounted for.
  - Secrets management approach defined.
  - Threat model for the main trust boundaries.
- Reliability
  - Single points of failure identified and either removed or explicitly accepted.
  - Backups and restore verification plan exists.
- Operations
  - Runbooks for deploy/rollback and incident response.
  - Ownership/on-call clarified.
- Cost
  - Tags and budget alerts planned.
  - Major cost drivers called out with alternatives.

## Output Templates

### Architecture Decision Summary (Short)

- Decision: <what we are choosing>
- Drivers: <latency/cost/security/compliance/timeline>
- Options considered: <A/B/C>
- Chosen option: <A>
- Consequences: <1-5 bullets>
- Open questions: <what must be validated>

### Migration Plan (If Applicable)

- Phase 0: discovery + inventory
- Phase 1: foundations (landing zone, IAM, networking)
- Phase 2: data plane (databases, storage)
- Phase 3: app plane (compute, routing)
- Phase 4: cutover (dual-write, canary, rollback plan)
- Phase 5: decommission + cost cleanup

## Reference Notes

See the files in `references/` for provider-specific checklists and multi-cloud notes.
