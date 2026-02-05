---
name: ui-visual-validator
description: Verifies UI changes via rigorous, evidence-based visual validation (screenshots/video/URLs) to catch regressions, design-system drift, responsive breakage, and visual accessibility issues.
category: design
---

# UI Visual Validator

High-signal visual verification that is intentionally tool-agnostic and works from visual evidence.

## Use this skill when

- Confirming a UI change is actually correct (not just "different")
- Catching visual regressions before merge/release
- Needing a deterministic checklist for responsive + state coverage
- Running a visual accessibility pass (focus visibility, contrast concerns, readability)

### Trigger phrases

- "validate the UI visually"
- "check for visual regressions"
- "compare before/after screenshots"
- "confirm responsive layouts" or "check breakpoints"
- "verify focus/contrast visually"

## Do not use this skill when

- Designing a UI or exploring new layouts
- Lacking visual evidence and a URL + repro steps

## Required inputs

- Evidence: before/after screenshots or recordings, or a URL with repro steps
- Intended change: what should be different and why
- Scope: pages/components/states that are in scope
- Constraints: target viewports, themes, or environments (if any)

## Workflow (Deterministic)

1. **Inventory evidence**
   - Output: evidence table listing filename/URL, viewport, theme, state, environment.
   - If evidence is missing, stop and output `needs-evidence` with a retest plan.
2. **Translate intent into goals**
   - Output: checklist of visual goals (one line per goal).
3. **Diff pass (what changed)**
   - Output: bullet list of observed diffs (objective, no judgments).
4. **Validation pass (is it correct)**
   - For each goal, mark `met`, `not met`, or `needs-evidence` and cite evidence.
5. **Responsive + state coverage**
   - Output: coverage matrix for default/hover/focus/active/disabled/loading/error/empty and breakpoints.
   - Decision: if a required state/breakpoint is missing, downgrade verdict to `partial` or `needs-evidence`.
6. **Accessibility (Visual) checks**
   - Output: focus visibility findings, contrast concerns, text scaling/wrapping issues.
7. **Verdict + next actions**
   - Decision rules:
     - `pass`: all goals met, no regressions, coverage complete.
     - `partial`: goals mostly met but missing coverage or minor regressions.
     - `fail`: any critical regression or goal not met.
     - `needs-evidence`: missing evidence blocks evaluation.

## Common pitfalls to avoid

- Calling a change "correct" without listing visible evidence.
- Skipping focus/contrast checks because the change seems minor.
- Ignoring states that are in scope (loading/error/empty) for the component.
- Mixing subjective language with objective observations.

## Output Contract (Always)

Use this exact section order:

1. **Verdict**: pass/fail/partial/needs-evidence
2. **Evidence Inventory**: list of artifacts with viewport/theme/state
3. **Goals**: checklist with status per goal
4. **Observations (Objective)**: what is visible
5. **Intended Diffs Observed**: which goals are satisfied
6. **Regressions / Unintended Changes**: anything unexpected
7. **Accessibility (Visual)**: focus visibility, contrast concerns, readability
8. **Responsive + State Coverage**: breakpoints and states covered + gaps
9. **Issues (With Severity)**: blocker/major/minor/nit
10. **Retest Plan**: missing evidence + how to capture it

## Examples

**Trigger test prompts**

- "Please validate these before/after screenshots of the settings page for regressions."
- "Can you check the responsive behavior and focus visibility for this modal?"

**Output snippet**

- Verdict: partial
- Evidence Inventory: `settings-desktop-before.png` (1280x800, light, default)
- Goals: [ ] Updated button padding (needs-evidence at 768px)
- Regressions / Unintended Changes: Hover state missing from evidence

## Optional automation

- Report scaffold script: `scripts/visual_report.sh`
- Usage: `./scripts/visual_report.sh "<subject>" <output-path>`
- Requirements: bash, standard coreutils (`date`, `mkdir`, `dirname`).
- Verification: confirm the report file exists and open it to fill in findings.
- Template reference: `references/report-template.md` (matches output contract order).

## References (Optional)

- Index: `references/README.md`
