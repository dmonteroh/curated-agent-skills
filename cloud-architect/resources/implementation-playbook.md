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

## Architecture Workflow (Use As A Deterministic Loop)

### 1) Define The Boundaries

- Identify the system boundary, external dependencies, and trust boundaries.
- Choose interaction style: sync HTTP, async events/queues, batch, streaming.

### 2) Pick The Platform Pattern

Choose one dominant pattern; avoid mixing unless justified.

- Serverless-first (Functions + managed eventing)
- Containers (Kubernetes / managed container services)
- VM-based (for legacy or strict requirements)

### 3) Landing Zone / Account & Subscription Layout

- Separate environments (at least prod vs non-prod).
- Use least-privilege identity boundaries.
- Define naming conventions and tagging strategy early.

### 4) Networking (Start Simple, Scale Correctly)

- VPC/VNet design: CIDR plan, subnets, NAT/egress strategy.
- Private connectivity: private endpoints, service endpoints, or PSC.
- Ingress: WAF + L7 load balancer / gateway.

### 5) Identity & Access

- Human access: SSO + MFA; break-glass accounts.
- Workload identity: short-lived credentials; avoid static access keys.
- RBAC model aligned to team structure (platform vs app vs read-only).

### 6) Data & State

- Database choice: managed DB first unless a requirement forbids it.
- Backups and PITR: define retention and restore testing schedule.
- Data lifecycle: retention, archival, deletion, legal hold requirements.

### 7) Reliability, DR, And Failure Mode Design

- Multi-AZ by default for stateful services.
- Define RPO/RTO and pick DR strategy (backup-restore, pilot light, warm standby, active-active).
- Run game days or failure injection for the most critical path.

### 8) Observability

- Define the golden signals: latency, traffic, errors, saturation.
- Metrics + logs + traces: make correlation IDs standard.
- Alerting: page on symptoms; ticket on causes.

### 9) Cost & Capacity

- Establish budget guardrails and cost allocation.
- Right-size; prefer autoscaling where possible.
- Separate cost experiments from production changes.

### 10) IaC + Change Management

- Make IaC the source of truth (Terraform/OpenTofu or cloud-native).
- Use plans/previews in CI.
- Avoid manual drift; document approved emergency procedures.

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

See the files in `cloud-architect/references/` for provider-specific checklists and multi-cloud notes.
