# Tailwind Implementation Playbook

Provides a repeatable loop for introducing or refactoring Tailwind usage in an app or design system.

## Inputs

- Project paths that generate class names (framework + folder conventions).
- Theme approach:
  - fixed palette (simple)
  - CSS-variable driven (recommended)
- Component surface being standardized (buttons, inputs, tables, etc.)

## Default Loop

1) Tailwind config sanity
- Confirm `content` covers all UI sources.
- Add a *minimal* `safelist` only when classes are created dynamically.
- Confirm dark mode strategy.

2) Tokens first
- Create semantic tokens (not per-component tokens).
- Back tokens with CSS variables so brand/theme changes do not require changing class names.

3) Component class contracts
- Define: base + variants + sizes + states.
- Prefer data attributes for variants when it improves readability.
- Keep callsites thin; do not re-invent styles per usage.

4) Accessibility + responsive
- Focus rings are visible.
- Disabled states are distinct and non-interactive.
- Touch targets and spacing are consistent at breakpoints.

5) Verify
- Build and confirm styles exist in production output.
- Manually validate: default/hover/focus/disabled + one responsive breakpoint.

## Common Footguns

- Missing `content` paths (styles work in dev but not in prod).
- Over-broad `safelist` patterns (bloats CSS output).
- Using palette tokens directly everywhere (`blue-500`) instead of semantic tokens (`ui.action`).
- Dark mode token mismatch (background changes but borders/text do not).
