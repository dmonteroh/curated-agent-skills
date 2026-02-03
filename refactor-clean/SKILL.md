---
name: refactor-clean
description: Refactor code safely and quickly using clean-code + SOLID principles with an incremental, test-first workflow. Includes a lightweight hotspot scan script to find high-impact refactor targets. Use PROACTIVELY for refactoring tangled code, reducing duplication/complexity, and preparing modules for new features without behavior regressions.
category: workflow
---

# Refactor Clean

Refactor code with a bias toward **speed**, **small diffs**, and **behavioral stability**.

This skill consolidates duplicate refactoring skills into one canonical workflow.

## Use this skill when

- Refactoring tangled or hard-to-maintain code.
- Reducing duplication, complexity, or code smells.
- Improving testability and design consistency.
- Preparing modules/components for new features.
- Cleaning up a large codebase with accumulated debt (but still via incremental steps).

## Do not use this skill when

- You only need a tiny targeted fix (refactor cost outweighs benefit).
- Refactoring is blocked by policy, deadlines, or change freeze.
- The request is documentation-only.

## Workflow (best results, best speed)

1) Clarify intent + constraints
- What is the behavior that must not change?
- What scope is allowed? What is off-limits?
- What “done” looks like (tests, perf budget, style constraints).

2) Establish a safety net
- Identify and run existing tests and/or add minimal characterization tests.
- If tests are missing, add the smallest set that protects the refactor seam.

3) Find hotspots (fast)
- Run `scripts/scan_hotspots.sh` to locate high-impact targets.
- Prefer refactors that reduce risk quickly:
  - duplicate logic
  - large files/modules
  - long functions
  - high churn areas (if git history is available in the repo you are working in)

4) Plan the refactor in small slices
- Sequence changes so each step is reviewable and revertible.
- Prefer interface-preserving refactors (rename/extract/inline/encapsulate).

5) Refactor incrementally
- One small change at a time; keep behavior stable.
- Keep diffs focused; avoid opportunistic rewrites.

6) Verify + communicate
- Run tests and targeted regressions.
- Summarize what changed, why it’s safer, and what to watch.

## Output format (when asked for a plan)

- Hotspots + why they matter
- Proposed steps (ordered), with risk notes
- Verification plan (tests + targeted checks)

## Integration notes

- If work needs structured intake/spec/planning, use `tracks-conductor-protocol` to create tasks/tracks.
- If a refactor changes architecture boundaries or introduces a major new pattern, record an ADR via `adr-madr-system`.

## Resources

- `resources/implementation-playbook.md` for patterns and examples.
- `scripts/scan_hotspots.sh` for a quick hotspot inventory.
