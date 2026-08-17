---
name: devops-engineer
description: "Operate and evolve runtime infrastructure for reliability, containerization, Kubernetes operations, platform engineering, and operational readiness. Use for runtime reliability, deployment execution, or incident response prep; not for CI/CD pipeline architecture or release automation design."
metadata:
  category: devops
---
# DevOps Engineer

Provides operational guidance for runtime platforms and day-2 reliability.

## Use this skill when

- Containerizing applications (Dockerfile/image/runtime constraints)
- Operating Kubernetes workloads (deployments/services/ingress, probes, resource limits)
- Granting or withholding control-plane API access for a workload, and sizing its permissions
- Protecting a workload against voluntary disruption (node drains, maintenance) as distinct from deploys
- Building platform engineering “golden paths” and self-service templates
- Improving operational readiness (health checks, runbooks, on-call hygiene)
- Managing deployment execution, verification, or rollback tied to runtime reliability
- Running a tool that mutates a project (installer, scaffolder, migration runner) inside a container so it cannot touch the real checkout
- Deciding what a containerized run is allowed to claim about behavior on other host platforms
- Supporting incident response readiness or stabilization

## Do not use this skill when

- The task is primarily CI/CD pipeline architecture, build systems, or release automation design
- The task is purely application feature work with no runtime/ops impact
- The task is designing what a test asserts, rather than the runtime confinement the test executes in

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

## Decision points

- **A probe is chosen by its remediation, not by its name.** Each probe type does something different when it fails: one kills a container that is taking too long to start, one restarts a container that is already running, one only removes the pod from the service's endpoints while leaving it alive. Pick the probe whose failure action is the remediation the situation actually calls for — a hung process needs the restart, a dependency that reconnects in a moment needs endpoint removal, because restarting a healthy process over a transient downstream blip converts a brief degradation into a crash loop. Point the endpoint-removal probe at a *different* endpoint from the restart probe: readiness may legitimately fail on a downstream, liveness must not. Each probe's tolerance is `failureThreshold × periodSeconds`, so configure it as an explicit time budget derived from the workload's observed startup and hang behavior, rather than padding a single initial delay — a long fixed delay used in place of a startup probe is an arbitrary wait and a race, not a budget. Decision table and worked arithmetic: `references/kubernetes-workload-safety.md`.
- **Control-plane API access defaults to off.** Most workloads never call the orchestrator's API, so the safe default is no credential at all: a dedicated service account with token automounting disabled — set on the account and again at the pod, because either alone can be undone by the other — and no role or binding of any kind. Escalate only on demonstrated need: when a workload genuinely watches or edits cluster objects, enable the token and grant the minimum — namespace-scoped role rather than cluster-scoped, only the verbs the code actually calls, and access pinned to specific named objects wherever the API supports it. Binding a cluster-admin role to an application service account is the failure this rule exists to prevent, and it is invisible until something is compromised. Both patterns in full: `references/kubernetes-workload-safety.md`.
- **Voluntary disruption is a different event from a deploy, and needs its own floor.** Rollout parameters govern what a deployment does to a workload; they say nothing about what a node drain, an autoscaler scale-down, or a maintenance window does. A critical workload needs an explicit disruption budget so those events cannot take it below a serving floor — and that floor must be above zero, since a budget of zero permits exactly what the budget was created to prevent. Checklist and the related workload-shape traps: `references/kubernetes-workload-safety.md`.
- **A tool that mutates a project gets a disposable copy, never the checkout.** Exercising an installer, scaffolder, or migration runner against the real working tree makes the test's blast radius the repository, and a partial run leaves the damage in place. Run it in a container configured so that mutation outside a scratch area is structurally impossible rather than merely discouraged: source mounted read-only and copied into a writable scratch workspace, no network and no host credentials by default, dropped capabilities over a read-only root filesystem, and a dry run as the default mode. Then assert the refusals, not just the successes — a harness that has never been shown to reject a write outside its workspace has not demonstrated the confinement. Full contract: `references/container-isolation-contract.md`.
- **A Linux container does not validate macOS or Windows behavior.** Containers share the host's Linux kernel: macOS cannot run as a container at all, and Windows containers require a Windows engine. Platform-independent logic can be proven in a container, but host-specific paths, command shims, argument quoting, and filesystem semantics require a native runner per operating system. This is a claim-discipline rule — it constrains what a passing run may be reported as proving. State the platform the evidence covers instead of letting one green Linux job stand in for a matrix. Detail: `references/container-isolation-contract.md`.

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
- Probe budget: size the startup allowance as `failureThreshold × periodSeconds` against the workload's measured cold start; point readiness at a dependency-checking endpoint and liveness at one that does not check dependencies.
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
