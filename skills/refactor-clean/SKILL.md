---
name: refactor-clean
description: Provides an incremental, test-first refactoring workflow for reducing complexity or duplication while keeping behavior stable, best used during technical-debt cleanup or design improvement.
category: workflow
---

# Refactor Clean

Provides a workflow to refactor code with small diffs, stable behavior, and fast feedback.

## Use this skill when

- Refactoring tangled or hard-to-maintain code.
- Reducing duplication, complexity, or code smells.
- Improving testability or design consistency.
- Preparing modules for new features without regressions.

## Do not use this skill when

- A small, targeted fix is all that is needed.
- Refactoring is blocked by policy, deadlines, or change freeze.
- The request is documentation-only or purely stylistic.

## Trigger phrases

- "refactor"
- "clean up this code"
- "reduce duplication"
- "simplify this module"
- "address code smells"
- "technical debt"

## Required inputs

- Target files/modules or a clear scope boundary.
- Behavior that must not change (invariants, contracts, API expectations).
- Allowed change scope and any constraints (deadlines, perf budgets, style rules).
- Available tests or how to verify changes.

## Workflow

1) Confirm intent and scope
   - If scope or invariants are unclear, ask clarifying questions before editing.
   - Output: a one-paragraph scope statement and non-goals.

2) Establish a safety net
   - If tests exist, run the most relevant subset.
   - If tests are missing, add minimal characterization tests for refactor seams.
   - Output: list of tests to run and any new tests added.

3) Identify hotspots
   - Run `skills/refactor-clean/scripts/scan_hotspots.sh` (from repo root) or use manual heuristics.
   - Output: 1–3 targets with a short risk/impact note each.

4) Plan small slices
   - If the change is large or risky, propose a staged plan before editing.
   - Prefer interface-preserving steps (rename, extract, inline, encapsulate).
   - Output: ordered steps with risk notes.

5) Refactor incrementally
   - Make one small change at a time and keep diffs focused.
   - Avoid mixing behavior changes with cleanup unless explicitly required.
   - Output: brief log of each completed slice.

6) Verify and report
   - Run tests and targeted checks after the refactor.
   - If verification cannot be run, state what should be run.
   - Output: verification results and any remaining risks.

## Common pitfalls

- Broad rewrites without a safety net.
- Mixing formatting changes with structural changes.
- Skipping a plan for large or risky changes.
- Letting refactors drift into new feature work.

## Script: `skills/refactor-clean/scripts/scan_hotspots.sh`

- Purpose: quick inventory of large files and TODO/FIXME density.
- Usage: `HOTSPOT_LIMIT=20 sh skills/refactor-clean/scripts/scan_hotspots.sh`
- Requirements: POSIX shell; uses `rg` if available, otherwise `find`, `wc`, `awk`, `sort`, `head`.
- Verification: output should include "Largest Files" and "TODO / FIXME Counts" sections.

## Examples

**Example 1: request for incremental refactor**

Input: "Refactor `orders.py` to remove duplication. Keep API behavior identical and tests are in pytest."

Expected output (summary):

- Scope: `orders.py` duplication cleanup, no API changes.
- Hotspots: repeated pricing logic, long validation function.
- Plan: extract pricing helpers, consolidate validation, run pytest subset.
- Verification: `pytest tests/orders`.

**Example 2: request for plan only**

Input: "Give me a plan to clean up this payment service without changing behavior."

Expected output (summary):

- Hotspots and risks identified.
- Ordered refactor slices with rationale.
- Test/verification plan.

## Output contract

When this skill runs, report:

- Scope and invariants.
- Hotspots or target areas with brief rationale.
- Plan or changes made (ordered, small slices).
- Risks or follow-up recommendations.
- Verification performed or explicitly not run.

## Reporting format

- Scope:
- Hotspots:
- Changes or Plan:
- Risks:
- Verification:

## Trigger test

- "Can you refactor this module to reduce duplication without changing behavior?"
- "Clean up the legacy service and keep tests passing."

## References

- `references/README.md` for detailed playbooks and checklists.
