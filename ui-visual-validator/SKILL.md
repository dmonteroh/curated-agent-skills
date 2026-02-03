---
name: ui-visual-validator
description: Verify UI changes via rigorous, evidence-based visual validation (screenshots/video/URLs). Catch regressions, design-system drift, responsive breakage, and visual accessibility issues (focus visibility, contrast, readability). Use PROACTIVELY as a final quality gate before merge.
category: frontend
---

# UI Visual Validator

High-signal visual verification that is intentionally tool-agnostic and works from visual evidence.

## Use this skill when

- You need to confirm a UI change is actually correct (not just "different")
- You want to catch visual regressions before merge/release
- You need a deterministic checklist for responsive + state coverage
- You need a visual accessibility pass (focus visibility, contrast concerns, readability)

## Do not use this skill when

- You are designing a UI (use a design skill instead)
- You have no visual evidence and cannot provide a URL + repro steps

## Workflow (Deterministic)

1. Collect evidence: before/after, viewports, theme, relevant states.
2. Convert the intended change into a checklist of goals.
3. Validate each goal against evidence and actively hunt regressions.
4. Require state coverage (hover/focus/disabled/loading/error/empty) when relevant.
5. Always include a visual accessibility check.
6. Output a verdict: `pass` | `fail` | `partial` | `needs-evidence`.

## Output Contract (Always)

- **Verdict**: pass/fail/partial/needs-evidence
- **Observations (objective)**: what is visible
- **Regressions**: unintended diffs
- **Accessibility (visual)**: focus visibility + contrast concerns + readability
- **Responsive**: breakpoints covered + issues
- **Retest plan**: what evidence is missing and how to collect it

## Resources (Optional)

- Deep-dive playbook + report template: `resources/implementation-playbook.md`
- Report scaffold script: `scripts/visual_report.sh`
