---
name: tech-debt
description: Identify, quantify, and prioritize technical debt fast, then turn it into an executable remediation plan (SDD/CDD friendly). Produces a debt register with ROI estimates, risk tiers, and a track/task breakdown compatible with tracks-conductor-protocol and adr-madr-system. Use PROACTIVELY for debt audits, cleanup planning, or when velocity/quality is degrading.
---

# Tech Debt

Run a high-signal technical debt assessment and convert it into an actionable, staged remediation plan.

This skill consolidates overlapping tech-debt skills into one canonical workflow optimized for:
- **Speed**: get to a prioritized list quickly.
- **ROI**: quantify impact (velocity, reliability, cost).
- **Execution**: produce work units compatible with `tracks-conductor-protocol`.
- **Governance**: record major architectural decisions with `adr-madr-system`.

## Use this skill when

- Dev velocity is slowing, bug rate is increasing, or on-call is painful.
- You need a debt audit and a prioritized cleanup roadmap.
- You want to create an execution plan that can be staffed by multiple agents.

## Do not use this skill when

- You only need a local refactor of a single module (use `refactor-clean`).
- There is no codebase or telemetry to analyze.

## Workflow (best performance, best results)

### 1) Scope + signals (15 min)

Output:
- target area(s): repo/module/service
- constraints: timebox, release windows, forbidden changes
- success metrics: build time, p95 latency, crash rate, bug rate, dev cycle time

### 2) Inventory (fast scan)

Create a “debt register” with categories:
- Code debt (duplication, complexity, coupling)
- Architecture debt (boundary violations, missing abstractions)
- Tech debt (outdated deps, deprecated APIs)
- Testing debt (coverage gaps, flakiness)
- Docs debt (missing runbooks, onboarding)
- Infra/ops debt (missing monitoring, manual deploys)

If you can’t measure it, label it as “Hypothesis” and note what data would confirm it.

### 3) Impact + ROI (prioritize)

For each item, estimate:
- Impact: velocity / reliability / security / cost / customer pain
- Effort: S/M/L (or hours)
- Risk: low/med/high (blast radius)

Then rank by **Impact / Effort**, with risk as a multiplier.

### 4) Convert to executable work (multi-agent)

Output:
- A single track proposal for the top cluster of debt items (or 2-3 tracks if needed).
- A set of small tasks per track with acceptance criteria.

Use `tracks-conductor-protocol`:
- If there is no existing work system in the target repo, run `tcd.sh init` there.
- Create a track + plan, then generate tasks.

### 5) Governance (when debt requires decisions)

If remediation changes architecture boundaries, data model, auth, scaling approach, or major tooling:
- Create/update an ADR via `adr-madr-system`.

If a requirement is deferred but architecture-sensitive:
- Create a Future entry via `tracks-conductor-protocol` Futures.

## Output format

- Debt register (table): item, category, evidence, impact, effort, risk, proposed fix
- Top 5 “do now” items + rationale
- Proposed track(s) + phased plan
- Verification strategy (tests, benchmarks, monitoring)

