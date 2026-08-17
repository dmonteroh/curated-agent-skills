---
name: deployment-engineer
description: "Design and implement CI/CD and deployment automation: pipeline stages, quality gates, config validation, progressive delivery, rollback/runbooks, and GitOps patterns. Use for release workflows and deployment safety. Not for cloud platform architecture or deep IaC modules."
metadata:
  category: devops
---
# Deployment Engineer

Provides guidance for shipping changes safely with pipelines, releases, progressive delivery, and operational guardrails.
Produces deployment workflow recommendations without requiring other skills.

## Use this skill when

- Designing or improving CI/CD pipelines and release workflows
- Adding rollout safety (canary/blue-green), automated rollbacks, and runbooks
- Adding config validation gates and environment drift checks
- Implementing GitOps patterns (ArgoCD/Flux) at the workflow level
- Defining release-readiness gates that separate hard blockers from overridable warnings (e.g., stale reviews, an unbumped changelog)
- Defining what a gate does when its signal is missing rather than failing, so a pipeline cannot stall unowned
- Sequencing a schema change across releases so a code rollback is not blocked by a migration that already applied

## Do not use this skill when

- Cloud platform architecture (landing zones, network/IAM design)
- Deep Terraform/OpenTofu module design, state strategy, provider internals
- Deep FinOps cost optimization programs
- You only need to select cloud resources/services without deployment workflow changes
- The question is data-model or query design rather than how a schema change is sequenced and rolled back across releases

## Required inputs

- Repo/tooling context (CI system, deployment tooling, runtime platform)
- Environments and promotion path
- Release cadence and change windows
- SLOs or error budget constraints
- Constraints (compliance, approvals, security requirements)

## Workflow (Deterministic)

1. Capture inputs (repo/tooling, environments, release cadence, constraints, SLOs).
   - Output: input checklist and missing info questions.
   - If inputs are missing, stop and list questions before proceeding.
2. Map environments and promotion path (dev -> staging -> prod).
   - Output: environment map with promotion rules.
3. Define quality gates and config validation.
   - If a gate consumes a health signal, require an endpoint that verifies downstream dependencies rather than a liveness ping (see Decision points).
   - Output: gate list with owners, signals, and fail criteria — split into blockers and warnings, each with a stated undecided path (see Decision points).
4. Choose rollout + rollback strategy.
   - If traffic shaping exists, prefer canary; otherwise prefer rolling/blue-green.
   - If the release carries a schema change, plan its expand/contract sequence before the rollout (see Decision points).
   - Output: rollout plan, rollback triggers, and stop conditions — scale canary depth to diff scope (see Decision points).
5. Design pipeline stages and approvals.
   - Output: stage diagram or ordered list with required artifacts.
6. Add observability hooks and runbook steps.
   - Output: deploy markers/metrics list and runbook checklist.
7. Validate in staging and document operational handoff.
   - Output: validation checklist and open risks.

## Decision points

- **Every gate has three outcomes: pass, fail, and undecided.** A gate written as pass/fail has an unhandled state, and in that state the pipeline does not fail — it hangs, silently, owned by nobody. Two instances of the same bug: a metric-driven promotion gate whose query returns no data (metric renamed, exporter down) stays inconclusive, so the rollout neither promotes nor aborts; and an approval gate with no assigned approver waits forever while notifying no one. For every gate, define what happens when the signal is *absent* as a case distinct from the signal failing — bound how long the gate may stay undecided (a count of inconclusive evaluations, or a wall-clock ceiling), decide whether hitting that bound means fail-closed or escalate to a named human, and validate at design time that every approval gate resolves to a non-empty, reachable approver set rather than discovering an empty reviewer list during a release. This is a property of the gate definition, not of any one CI product, and it is a different axis from the blocker/warning split below: that split sorts gates that did decide, this one covers the gate that never decides at all. Whatever bound is chosen is a chosen default with no derivation behind it — state it as one. Depth, including the design-time gate audit: `references/promotion-gates.md`.
- **A promotion gate must check readiness, not liveness, and must wait under a ceiling.** A shallow `/ping` returns 200 while the database, cache or queue is unreachable, so a health gate built on it passes a deploy that is already broken — this is the most common way a green pipeline ships an unhealthy service. The endpoint a promotion gate polls must verify its actual downstream dependencies and return a non-2xx when any of them is down, and it must be a different endpoint from the one that decides whether to restart the process: readiness may legitimately fail on a dependency, liveness must not. Pair the deep check with a bounded wait — poll at a fixed interval, pass on the first healthy response, fail the deploy at a stated maximum — so a slow-starting service is not misread as a failed one and a never-starting one does not hold the pipeline open indefinitely. Derive the interval and the ceiling from the service's observed startup time; another service's poll count is a guess, not a measurement. Depth: `references/promotion-gates.md`.
- **A rollback that only moves code back is not a rollback.** Rolling the service back to its previous version while the new schema stays applied produces schema/code mismatch errors: the deploy is reported as rolled back and the service is still broken. Plan the data side with the code side. Make every schema change additive and backward-compatible, staged as expand → migrate → contract across separate releases — one release adds the new structure, a later release deploys code that backfills and reads it, and only a release after that removes the old structure, once no deployed version still references it. The number of releases follows from that sequence; it is not a tuned constant. Keep the undo script versioned alongside its forward migration rather than written under incident pressure, and never run a destructive change (dropping a column, adding a NOT NULL constraint) until the old code version is retired from *every* environment, not just production. Mechanics and the rollback-plan checklist: `references/pipeline-design.md`.
- **Review staleness is not just a commit count.** An approval describes a specific diff; every commit landed on top of it erodes how much of that approval still applies. Judge staleness on two axes: how many commits landed since approval, and whether any of them is a fix, a refactor, a rewrite, an overhaul, or touches many files — that second, semantic test overrides the count, because one substantial commit can invalidate a review that a dozen trivial ones would not, since the review was done against code that no longer describes what is about to ship. Treat a stale review as a warning (see below), never a silent pass and never an automatic hard block. Commit-count bands and a specific file-count cutoff are workable starting points but are chosen defaults with no independent derivation, not measured thresholds — tune both per repo and label them as defaults if you state them. Depth and a worked example: `references/release-readiness-gates.md`.
- **Canary depth scales with diff scope, not a fixed policy.** A fixed verification depth wastes time re-checking a docs-only change end to end and under-verifies a frontend change by treating it like a config tweak. Skip verification for docs-only changes, smoke-test config-only changes, add error-log and performance checks for backend-only changes, and run full verification (including a rendered/visual check) for anything touching the frontend or mixing scopes. The diff-to-scope classification is repo-specific; the scope-to-depth mapping is the reusable part. Mapping table: `references/release-readiness-gates.md`.
- **Config changes invalidate an earned dry-run pass.** A passed validation run only proves the deployment is safe against the configuration that was active when it ran — earned trust does not automatically carry forward when the infrastructure description itself changes underneath it. Fingerprint the deploy configuration after a confirmed passing run; when a later run's fingerprint no longer matches, re-run the full dry run instead of reusing the stale pass, and report the change explicitly rather than trusting the new configuration silently. Mechanism: `references/release-readiness-gates.md`.
- **Blockers and warnings are different gates.** Only hard failures — chiefly failing tests — should block a release outright. A stale review or an unbumped changelog are warnings: name them explicitly, state why each fired, and require an affirmative, recorded override to proceed past them. Collapsing the two tiers either blocks releases on cosmetic issues or trains people to click through every gate unread; the failure runs both directions, so a warning must never silently pass as clean and must never block like a failure. Detail: `references/release-readiness-gates.md`.

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
- Rollout: 10% canary for a defined window; rollback on 5xx > threshold; canary depth scaled up for the frontend files in this diff (full verification, not just a smoke check)
- Config validation: schema + env diff checks in `validate-config`
- Gates: failing tests are the only blocker; a review 4 commits stale with a "refactor" commit in between, and an un-bumped CHANGELOG, are surfaced as warnings requiring an explicit "merge anyway" override
- Undecided paths: the canary metric gate aborts the rollout after a stated number of inconclusive evaluations instead of waiting on a query that returns no data; the production approval gate is checked at design time to resolve to a non-empty reviewer set, and escalates to the on-call owner at its wait ceiling
- Verification: the canary gate polls a `/health/ready` endpoint that checks database, cache and queue and returns 503 when any is down — not the `/ping` used for liveness — with a stated poll interval and attempt ceiling derived from this service's observed startup time
- Runbook: deploy, pause, rollback, and troubleshooting steps

## Output format

Provide these sections in order:
1. Summary
2. Pipeline Stages & Gates
3. Rollout & Rollback Plan
4. Config Validation Strategy
5. Runbook & Observability
6. Open Questions / Risks

## Output contract (Always)

- Pipeline stage diagram (or bullet list) with gates and required artifacts
- Rollout/rollback plan and stop conditions
- Config validation strategy (what is validated and where)
- Runbook notes (how to deploy, rollback, and troubleshoot)
- Open questions when required inputs are missing

## References (Optional)

- `references/README.md`
