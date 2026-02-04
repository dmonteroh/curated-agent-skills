---
name: tech-debt
description: Identify, quantify, and prioritize technical debt, then turn it into an executable remediation plan with ROI estimates, risk tiers, and verification steps. Use for debt audits, cleanup planning, or when velocity and quality are degrading.
category: workflow
---

# Tech Debt

Run a high-signal technical debt assessment and convert it into an actionable, staged remediation plan.

## Use this skill when

- Dev velocity is slowing, bug rate is increasing, or on-call is painful.
- You need a debt audit and a prioritized cleanup roadmap.
- You need an execution plan that can be staffed by a team.

Trigger phrases:
- “technical debt audit”
- “cleanup roadmap”
- “prioritize refactors”
- “too many TODOs and flaky tests”
- “we need a debt register”

## Do not use this skill when

- You only need a local refactor of a single module.
- There is no codebase or telemetry to analyze.

## Workflow

### 1) Confirm scope and inputs

Inputs:
- target area(s): repo/module/service
- constraints: timebox, release windows, forbidden changes
- success metrics: build time, p95 latency, crash rate, bug rate, dev cycle time
- available evidence: issues, incidents, telemetry, TODOs

Decision:
- If there is no codebase or evidence to analyze, ask for it and stop.

Output:
- scoped target statement
- constraints list
- success metrics list
- evidence sources + gaps

### 2) Gather debt signals

Collect quick signals using repo scans, issue trackers, incident notes, and build/test logs.

Optional script:
- Run `./scripts/debt_scan.sh` in the target repo to generate a quick signal report.

Decision:
- If scripts cannot run, document manual scan findings instead.

Output:
- signal summary (top files, hotspots, recurring markers)
- evidence snippets with locations

### 3) Build the debt register

Create a “debt register” with categories:
- Code debt (duplication, complexity, coupling)
- Architecture debt (boundary violations, missing abstractions)
- Tech debt (outdated deps, deprecated APIs)
- Testing debt (coverage gaps, flakiness)
- Docs debt (missing runbooks, onboarding)
- Infra/ops debt (missing monitoring, manual deploys)

Decision:
- If evidence is weak, mark the item as “Hypothesis” and list required data to confirm.

Output:
- debt register table with evidence links

### 4) Score impact, effort, and risk

For each item, estimate:
- Impact: velocity / reliability / security / cost / customer pain
- Effort: S/M/L (or hours)
- Risk: low/med/high (blast radius)

Rank by **Impact / Effort**, with risk as a multiplier.

Output:
- prioritized list with scores and rationale

### 5) Plan remediation

Group top items into phases and define acceptance criteria.

Decision:
- If remediation touches architecture boundaries, data model, auth, scaling approach, or major tooling, create a lightweight decision log entry in the repo (e.g., `docs/decisions/`).

Output:
- phased plan (Phase 0/1/2) with acceptance criteria
- dependencies and sequencing notes

### 6) Verification plan

Define how to prove outcomes improved.

Output:
- tests, benchmarks, and monitoring checks tied to success metrics

## Script usage (optional)

`scripts/debt_scan.sh` runs a quick, read-only scan in the target repo.

Usage:
- `./scripts/debt_scan.sh`

Environment variables:
- `DEBT_SCAN_OUT_DIR` (default: `docs/_docgen`)
- `DEBT_SCAN_OUT_FILE` (default: docs/_docgen/tech_debt_scan.md)
- `DEBT_SCAN_LIMIT` (default: `20`)

Requirements:
- `rg` (ripgrep) if available; otherwise it falls back to `find` + `grep`.

Verification:
- Confirm docs/_docgen/tech_debt_scan.md exists and contains sections for large files and debt markers.

## Common pitfalls

- Jumping to refactors without evidence or measurable impact.
- Treating speculative issues as facts (mark them as hypotheses).
- Over-scoping into a full rewrite without phased milestones.
- Ignoring verification; every fix needs a measurable success check.

## Example

Input:
- “We have frequent production incidents and long deploy times. Can you audit tech debt and propose a remediation plan?”

Output (abridged):
- Summary: Top debt items are build pipeline bottlenecks and flaky integration tests.
- Debt register entry: `CI pipeline is 45m` | Testing debt | Evidence: `ci/logs/2024-...` | Impact: high | Effort: M | Risk: low | Fix: split tests + parallelize.
- Phase 1: stabilize tests; Phase 2: pipeline changes; Verification: build time < 20m, flaky test rate < 2%.

## Output contract

Return a report with the following sections and format:

### Tech Debt Report

Summary:
- 3–5 sentences describing scope, evidence, and top risks.

Debt Register (table):
- Columns: item | category | evidence | impact | effort | risk | proposed fix | status

Top Items:
- Top 5 “do now” items with one-line rationale each.

Remediation Plan:
- Phases with acceptance criteria and dependencies.

Verification:
- Tests, benchmarks, and monitoring checks tied to success metrics.

## Trigger test

Use this skill for prompts like:
- “Create a technical debt register for this repo and prioritize it.”
- “Audit tech debt and give me a phased cleanup plan.”
