---
name: tailwind
description: "Build and maintain Tailwind CSS systems fast without framework lock-in: tokens (CSS variables), theme + dark mode, content globs/safelist, component variant patterns, accessibility/responsive conventions, and migration hygiene."
category: frontend
---

# Tailwind CSS

This skill is Tailwind-specific and intentionally framework-agnostic (React/Svelte/Vue/Angular all work).

## Use this skill when

- Defining a Tailwind-driven design system (tokens, color semantics, typography, spacing)
- Standardizing component patterns (variants/sizes/states) across a codebase
- Tuning `content`, `safelist`, and build hygiene (avoid missing classes / huge CSS output)
- Migrating Tailwind versions or refactoring class strategy safely

## Do not use this skill when

- The task is only selecting a frontend framework or component library
- The task is only UI critique without Tailwind implementation scope

## Trigger phrases

- "Set up Tailwind tokens/theme"
- "Tailwind config review (content/safelist/dark mode)"
- "Standardize component variants in Tailwind"
- "Migrate Tailwind safely"

## Inputs required

- Repo paths that generate class names (templates, components, CMS templates)
- Whether class names are dynamically generated
- Current theming approach (CSS variables vs hard-coded palette)
- Tailwind config location (if non-standard)

## Workflow (Deterministic)

1) Confirm constraints
- Framework(s) in use (only for content globs and file conventions).
- Whether class names are dynamic (needs safelist strategy).
- Whether theming uses CSS variables (recommended) vs hard-coded palette.
Output: constraints summary and any open gaps.

2) Establish tokens + theme surface
- Pick a small semantic token set (canvas/surface/text/border/action + status colors).
- Map Tailwind `theme.extend.colors` to CSS variables (design tokens).
- Define typography tokens (fonts, sizes, line-heights) intentionally.
Output: token list and `theme.extend` map (or change list).

3) Configure Tailwind correctly
- `content`: include all template/code paths that generate class names.
- `safelist`: only when class names are dynamic; use patterns with tight scope.
- `darkMode`: choose explicit strategy (often `class`).
Output: proposed config changes with rationale.

4) Component patterns (no framework lock-in)
- Use stable class contracts per component (base + variants + sizes + states).
- Prefer data-attributes for variants when that reduces conditional class sprawl.
- Keep "utility soup" from leaking into every callsite.
Output: component contract(s) with examples.

5) Verify
- Build output includes expected classes (no missing styles in prod).
- Responsive + focus states work.
- Dark mode works and contrast is acceptable.
Output: verification checklist with pass/fail notes.

## Decision points

- If class names are dynamic, add a tight `safelist`; otherwise omit it.
- If theme changes should not touch markup, use CSS variables in `theme.extend`.
- If multiple frameworks exist, union their template globs in `content`.

## Common pitfalls

- `content` misses templates from UI libraries or CMS-driven paths.
- Over-broad `safelist` patterns bloating CSS output.
- Variant logic scattered across callsites instead of a component contract.

## Examples

Example request:
"We use Tailwind with dynamic status badges and want consistent variants. Also dark mode is flaky."

Expected response summary:
- Constraints summary (dynamic classes, dark mode strategy).
- Updated `content`/`safelist` guidance and reason.
- Component contract for badges (base + variants + states).
- Verification steps for dark mode and responsive states.

## Output Contract (Always)

Report using this format:

- Constraints and assumptions
- Tokens/theme/config changes (with rationale)
- Component variant contract(s)
- Verification steps and results
- Risks or follow-ups

## Scripts (Optional)

- `scripts/tailwind_audit.sh`: read-only heuristic scan for common misconfigurations.
  - Requirements: `rg` (ripgrep) installed locally.
  - Usage: run from the target repo root; review the printed heuristics.
  - Verification: confirm the reported config paths and heuristics match expectations.

## Trigger test

- "Can you review my Tailwind config and suggest fixes for missing styles in prod?"
- "We need a Tailwind token system and consistent component variants."

## References (Optional)

- Index: `references/README.md`

- Tailwind config essentials (content/safelist/theme/plugins): `references/config.md`
- Token strategy (CSS variables -> semantic colors): `references/tokens-and-theming.md`
- Component variants (framework-agnostic patterns): `references/component-variants.md`
- Design system overview: `references/design-system.md`
- Responsive + accessibility conventions: `references/responsive-and-a11y.md`
- Migration + hygiene checklist: `references/migration-and-hygiene.md`
- Implementation playbook: `resources/implementation-playbook.md`
- Read-only audit script: `scripts/tailwind_audit.sh`
