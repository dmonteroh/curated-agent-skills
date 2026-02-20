---
name: ui-design
description: "One canonical, framework-agnostic UI/UX design skill: turn requirements into clear UI briefs, flows, component specs, and design-system rules; review UI code against local guidelines; prioritize accessibility, consistency, and developer-hand-off clarity. Not a Google Stitch skill."
metadata:
  category: design
---
# UI Design

Provides UI design and review guidance that turns requirements into briefs, flows, component specs, and design-system rules. It is intentionally framework-agnostic and does not assume any implementation stack.

## Use this skill when

- Requirements are unclear and you need a UI brief + flow before implementation
- Defining component behaviors and states (loading/empty/error/disabled)
- Defining or enforcing design-system rules (tokens, surfaces, status hierarchy)
- Reviewing UI code for accessibility and consistency using local guidelines

## Do not use this skill when

- The user explicitly wants UI code implementation only
- The task is “Google Stitch” specific

## Required inputs

- Target platform(s) and form factor (web, mobile, desktop; responsive needs)
- Primary user goal and success criteria
- Constraints (density vs delight, accessibility level, branding, localization)
- If reviewing code: files/links and any local UI guidelines
- If platform-specific behavior matters: local standards or product conventions

## Workflow (deterministic)

1) Clarify intent and constraints
   - Output: concise requirements summary + explicit assumptions.

2) Produce the UI brief (design-level contract)
   - Output: goals/non-goals, primary flow, secondary flows, hierarchy + navigation notes.

3) Specify components and states
   - Output: component list with responsibilities, states, data/prop contracts, interaction rules.

4) Define design-system rules (only if needed)
   - Output: token/surface rules, status hierarchy, optional theme usage contract.

5) Review/verification
   - Output: checklist-based findings with remediation plan and validation steps.

## Decision points

- If the user only wants implementation, confirm whether a design/spec is still needed before proceeding.
- If design-system rules already exist, reference them and avoid inventing new tokens.
- If platform is unclear, ask for the primary target before drafting the brief.
- If platform standards are missing, request local guidelines instead of assuming defaults.

## Common pitfalls to avoid

- Skipping empty/error/permission states in the flow
- Overloading the UI with multiple status colors or competing emphasis
- Missing keyboard/focus/label requirements in interactive components
- Providing pixel-perfect visuals when the user asked for structural guidance only
- Assuming platform conventions without local confirmation

## Examples

**Input**: “We need a billing settings screen, but requirements are fuzzy.”

**Output (summary)**:
- UI brief: goals/non-goals, primary + secondary flows, hierarchy notes
- Component list: tables, forms, confirmation dialog, loading/empty states
- A11y notes: focus order, labels, error summary

## Output contract (always)

Use this reporting format, in this order:

```md
# UI Brief
- Goals:
- Non-goals:
- Primary flow:
- Secondary flows:
- Hierarchy/navigation notes:

# Component + State Specs
- <Component>: responsibilities, states, data/props, interactions, acceptance criteria

# Accessibility Notes
- Focus/keyboard:
- Labels/ARIA:
- Motion/contrast:

# Review Findings (if reviewing code)
- blocker: `file:line` issue -> fix + verify step
- should-fix: `file:line` issue -> fix + verify step
- nice-to-have: `file:line` issue -> fix + verify step
```

## Resources (optional)

- `resources/implementation-playbook.md`
- `references/README.md`
