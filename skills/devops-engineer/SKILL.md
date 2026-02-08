---
name: devops-engineer
description: "Operate and evolve runtime infrastructure for reliability, containerization, Kubernetes operations, platform engineering, and operational readiness. Use for runtime reliability, deployment execution, or incident response prep; not for CI/CD pipeline architecture or release automation design."
category: devops
---
# DevOps Engineer

Provides operational guidance for runtime platforms and day-2 reliability.

## Use this skill when

- Containerizing applications (Dockerfile/image/runtime constraints)
- Operating Kubernetes workloads (deployments/services/ingress, probes, resource limits)
- Building platform engineering “golden paths” and self-service templates
- Improving operational readiness (health checks, runbooks, on-call hygiene)
- Managing deployment execution, verification, or rollback tied to runtime reliability
- Supporting incident response readiness or stabilization

## Do not use this skill when

- The task is primarily CI/CD pipeline architecture, build systems, or release automation design
- The task is purely application feature work with no runtime/ops impact

## Required inputs

- Service/workload name and environment
- Runtime surface (Docker, Kubernetes, VM, managed service)
- Current deploy/rollback mechanism
- Constraints (SLOs, security posture, budget)
- Change request or target outcome

## Non-negotiable rules

- No manual infra changes as the source of truth; prefer declarative configs/IaC.
- Do not ship `latest` tags to production.
- Always define resource requests/limits for production workloads.
- Avoid interactive steps in automated environments.

## Workflow (Deterministic)

1. Confirm scope and required inputs.
   - Decision: If the request is mainly CI/CD pipeline architecture or app feature work, state this skill is not applicable and ask for runtime-specific needs.
   - Output: scope confirmation, missing inputs list.
2. Clarify the operational goal and constraints.
   - Output: one-paragraph goal statement and constraints list.
3. Identify the runtime surface and ownership.
   - Decision: If Kubernetes, plan manifest changes; if Docker/VM, plan image/runtime changes.
   - Output: selected runtime path and owners.
4. Propose the smallest safe change.
   - Decision: If risk is high, propose phased rollout or canary with rollback guardrails.
   - Output: change list with risk notes.
5. Add verification and rollback steps.
   - Output: concrete validation steps, metrics to watch, rollback procedure.
6. Update operational artifacts.
   - Output: runbook updates, alert/dashboard follow-ups, ownership notes.

## Common pitfalls

- Changing runtime settings without updating runbooks or alerts
- Missing probes or resource limits in production
- Assuming rollback exists without testing or documenting it
- Editing runtime state manually instead of updating declarative configs

## Examples

**Example 1: Containerization hardening**
Input: "Make the API container slimmer and safer for prod."
Output:
- Summary: tighten base image, non-root user, pinned tag.
- Proposed changes: multi-stage build, drop dev deps, add USER.
- Verification: run image scan, validate startup and health checks.
- Rollback: revert image tag, redeploy previous digest.
- Follow-ups: document image build constraints in runbook.

**Example 2: Kubernetes readiness**
Input: "Our service keeps failing readiness checks after deploy."
Output:
- Summary: align readiness probes with startup behavior.
- Proposed changes: adjust probe path/timeouts, add startup probe.
- Verification: watch rollout status, monitor readiness success rate.
- Rollback: rollback deployment revision and restore probe config.
- Follow-ups: update runbook with probe guidance.

## Output Contract (Always)

Report in this format:

```
## Summary
## Proposed Changes
## Verification
## Rollback
## Follow-ups
```

## References

- `references/README.md`
