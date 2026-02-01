---
name: devops-engineer
description: "Day-2 operations and platform engineering: Docker/containerization, Kubernetes runtime patterns, environment hygiene, operational readiness, and incident response. Use when improving ops reliability or running infrastructure. For CI/CD pipeline design and rollout automation, prefer deployment-engineer."
---

# DevOps Engineer

This skill is for operating and evolving systems: containers, Kubernetes, platform engineering, and incident response readiness.

## Use this skill when

- Containerizing applications (Dockerfiles, images, runtime constraints)
- Kubernetes configuration and operations (deployments/services/ingress, resource limits)
- Platform engineering and self-service “golden paths”
- Operational readiness: health checks, runbooks, on-call hygiene
- Incident response support: triage, stabilization, postmortem follow-ups

## Do not use this skill when

- The task is primarily CI/CD pipeline design, rollout safety, or release automation (use `deployment-engineer`)

## Non-Negotiable Rules

- No manual infra changes as the “source of truth” (prefer declarative configs/IaC where available).
- Don’t ship `latest` tags to production.
- Always define resource requests/limits for production workloads.
- Don’t require interactivity in automated environments.

## Workflow (Deterministic)

1. Identify the operational goal and constraints (SLOs, security posture, budget).
2. Identify the runtime surface (Docker, Kubernetes, host/VM, managed service).
3. Make the smallest safe change first.
4. Add verification: readiness/health checks, metrics, and rollback path.
5. Document runbook notes and ownership.

## Output Contract (Always)

- Proposed change(s) with rationale
- Verification steps (how to validate success and detect regression)
- Rollback/stabilization steps
- Any required operational follow-ups (alerts, dashboards, runbooks)

## Resources (Optional)

- Deep-dive playbook: `resources/implementation-playbook.md`
- GitHub Actions (only when integrating runtime concerns, not pipeline architecture): `references/github-actions.md`
- Docker patterns: `references/docker-patterns.md`
- Kubernetes patterns: `references/kubernetes.md`
- Terraform/IaC notes (runtime-facing): `references/terraform-iac.md`
- Deployment strategies (runtime implications only): `references/deployment-strategies.md`
- Platform engineering: `references/platform-engineering.md`
- Release artifacts (runtime-facing): `references/release-automation.md`
- Incident response: `references/incident-response.md`
