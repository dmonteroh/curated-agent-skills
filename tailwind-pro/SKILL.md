---
name: tailwind-pro
description: Build and maintain Tailwind CSS systems fast without framework lock-in: tokens (CSS variables), theme + dark mode, content globs/safelist, component variant patterns, accessibility/responsive conventions, and migration hygiene.
---

# Tailwind Pro

This skill is Tailwind-specific and intentionally framework-agnostic (React/Svelte/Vue/Angular all work).

## Use this skill when

- Defining a Tailwind-driven design system (tokens, color semantics, typography, spacing)
- Standardizing component patterns (variants/sizes/states) across a codebase
- Tuning `content`, `safelist`, and build hygiene (avoid missing classes / huge CSS output)
- Migrating Tailwind versions or refactoring class strategy safely

## Do not use this skill when

- You are choosing a frontend framework or component library (use stack-specific skills)
- You only need UI critique (use UI/UX skills)

## Workflow (Deterministic)

1) Confirm constraints
- Framework(s) in use (only for content globs and file conventions).
- Whether class names are dynamic (needs safelist strategy).
- Whether theming uses CSS variables (recommended) vs hard-coded palette.

2) Establish tokens + theme surface
- Pick a small semantic token set (canvas/surface/text/border/action + status colors).
- Map Tailwind `theme.extend.colors` to CSS variables (design tokens).
- Define typography tokens (fonts, sizes, line-heights) intentionally.

3) Configure Tailwind correctly
- `content`: include all template/code paths that generate class names.
- `safelist`: only when class names are dynamic; use patterns with tight scope.
- `darkMode`: choose explicit strategy (often `class`).

4) Component patterns (no framework lock-in)
- Use stable class contracts per component (base + variants + sizes + states).
- Prefer data-attributes for variants when that reduces conditional class sprawl.
- Keep "utility soup" from leaking into every callsite.

5) Verify
- Build output includes expected classes (no missing styles in prod).
- Responsive + focus states work.
- Dark mode works and contrast is acceptable.

## Output Contract (Always)

- What tokens/theme/config changed and why
- How component variants are represented (classes, data-attrs, helpers)
- Verification steps (how to confirm build output + UI states)

## References (Optional)

- Tailwind config essentials (content/safelist/theme/plugins): `references/config.md`
- Token strategy (CSS variables -> semantic colors): `references/tokens-and-theming.md`
- Component variants (framework-agnostic patterns): `references/component-variants.md`
- Responsive + accessibility conventions: `references/responsive-and-a11y.md`
- Migration + hygiene checklist: `references/migration-and-hygiene.md`
- Implementation playbook: `resources/implementation-playbook.md`
- Read-only audit script: `scripts/tailwind_audit.sh`

