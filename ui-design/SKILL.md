---
name: ui-design
description: One canonical, framework-agnostic UI/UX design skill: turn requirements into clear UI briefs, flows, component specs, and design-system rules; review UI code against local guidelines; prioritize accessibility, consistency, and developer-hand-off clarity. Not a Google Stitch skill.
---

# UI Design

This skill is design + review + specification. It is intentionally framework-agnostic.

If Tailwind is in use, treat `tailwind-pro` as an optional helper for implementation details (tokens/config/class hygiene). Do not assume Tailwind exists.

## Use this skill when

- Requirements are unclear and you need a UI brief + flow before implementing
- Designing components and states (loading/empty/error/disabled)
- Defining or enforcing a design system contract (tokens, surfaces, status hierarchy)
- Reviewing UI code for accessibility and consistency using local guidelines

## Do not use this skill when

- The user asks you to implement the UI code (use frontend skills; this skill produces the design/spec)
- The task is “Google Stitch” specific (that is a different skill)

## Workflow (Deterministic)

1) Clarify intent
- Who is the user, what is the job-to-be-done, what is “done”?
- Constraints: density vs delight, desktop vs mobile, light/dark, localization.

2) Produce a UI brief (design-level contract)
- Goals / non-goals
- Primary flow (happy path)
- Secondary flows (error/empty/offline/permission)
- Information hierarchy + navigation placement

3) Component/spec layer
- Component list with responsibilities and states
- Data contracts at the boundary (what props/data each component needs)
- Interaction rules (keyboard/focus, confirm dialogs, destructive actions)

4) Design system rules (only if needed)
- Tokens and surfaces (canvas/surface stack)
- Status hierarchy (error/warn/success) to avoid visual noise
- A “Theme Usage Contract” style doc if the project requires enforceable rules

5) Review / verification
- Run an accessibility + UI checklist.
- If available, apply local guidelines: `references/web-interface-guidelines.md`.

## Output Contract (Always)

- UI brief (goals/non-goals + flows)
- Component/state list (with acceptance criteria)
- A11y notes (focus/labels/keyboard)
- If reviewing code: findings in `file:line` style and a short remediation plan

## Resources (Optional)

- Implementation playbook: `resources/implementation-playbook.md`
- Local UI review checklist (offline): `references/web-interface-guidelines.md`
- Design system contracts (how to write/consume them): `references/design-system-contracts.md`
- Deliverables + handoff templates: `references/deliverables-and-handoff.md`
- Deep topics (optional library of patterns): `references/topics/`
- UI design commands and agents (optional): `commands/`, `agents/`

