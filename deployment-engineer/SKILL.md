---
name: deployment-engineer
description: "Design and implement CI/CD and deployment automation: pipeline stages, quality gates, config validation, progressive delivery, rollback/runbooks, and GitOps patterns. Use for release workflows and deployment safety. Not for cloud platform architecture or deep IaC modules."
category: devops
---

# Deployment Engineer

This skill is for shipping changes safely: pipelines, releases, progressive delivery, and operational guardrails.

## Use this skill when

- Designing or improving CI/CD pipelines and release workflows
- Adding rollout safety (canary/blue-green), automated rollbacks, and runbooks
- Adding config validation gates and environment drift checks
- Implementing GitOps patterns (ArgoCD/Flux) at the workflow level

## Do not use this skill when

- Cloud platform architecture (landing zones, network/IAM design)
- Deep Terraform/OpenTofu module design, state strategy, provider internals
- Deep FinOps cost optimization programs
- You only need to select cloud resources/services without deployment workflow changes

## Trigger phrases

- "build a CI/CD pipeline"
- "add canary or blue/green rollout"
- "define rollout/rollback plan"
- "add config validation gate"
- "GitOps deployment workflow"

## Workflow (Deterministic)

1. Capture inputs (repo/tooling, environments, release cadence, constraints, SLOs).
   - Output: input checklist and missing info questions.
2. Map environments and promotion path (dev -> staging -> prod).
   - Output: environment map with promotion rules.
3. Define quality gates and config validation.
   - Output: gate list with owners, signals, and fail criteria.
4. Choose rollout + rollback strategy.
   - If traffic shaping exists, prefer canary; otherwise prefer rolling/blue-green.
   - Output: rollout plan, rollback triggers, and stop conditions.
5. Design pipeline stages and approvals.
   - Output: stage diagram or ordered list with required artifacts.
6. Add observability hooks and runbook steps.
   - Output: deploy markers/metrics list and runbook checklist.
7. Validate in staging and document operational handoff.
   - Output: validation checklist and open risks.

## Common pitfalls to avoid

- Shipping without explicit rollback triggers or owners
- Allowing config drift between environments without checks
- Putting slow, flaky tests in early gates
- Using manual approvals without objective criteria
- Missing runbook steps for partial failures

## Examples

**Example request**
"We need a GitHub Actions pipeline with canary deploys and automatic rollback. Add config validation before deploy."

**Example response outline**
- Pipeline: PR checks -> build -> test -> validate-config -> deploy-staging -> canary-prod -> verify
- Rollout: 10% canary for 15 minutes; rollback on 5xx > threshold
- Config validation: schema + env diff checks in `validate-config`
- Runbook: deploy, pause, rollback, and troubleshooting steps

## Output format

Return these sections in order:
1. Summary
2. Pipeline Stages & Gates
3. Rollout & Rollback Plan
4. Config Validation Strategy
5. Runbook & Observability
6. Open Questions / Risks

## Output Contract (Always)

- Pipeline stage diagram (or bullet list) with gates and required artifacts
- Rollout/rollback plan and stop conditions
- Config validation strategy (what is validated and where)
- Runbook notes (how to deploy, rollback, and troubleshoot)
- Open questions when required inputs are missing

## References (Optional)

- `references/README.md`
