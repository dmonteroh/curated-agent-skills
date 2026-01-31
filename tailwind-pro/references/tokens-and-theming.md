# Tokens and Theming (CSS Variables -> Tailwind Colors)

Goal: keep Tailwind class names stable while allowing theme changes via CSS variables.

## Recommended token layers

1) Brand tokens (rarely referenced directly)
- raw palette anchors

2) Semantic tokens (used everywhere)
- `ui.canvas`, `ui.surface-*`, `ui.text`, `ui.border`, `ui.action`
- status: `ui.success`, `ui.warning`, `ui.error`

3) Optional product tokens
- e.g., `tag.*` for colored labels if your UI needs many stable tag colors

## Tailwind mapping pattern (semantic)

In Tailwind config:

- map semantic colors to CSS variables
- keep names stable and avoid leaking palette numbers everywhere

Example asset: `assets/tailwind.config.example.cjs`

## CSS variable definition (where)

Put variables in a global stylesheet and scope them:

- `:root` for default theme
- `.dark` or `[data-theme="dark"]` for dark theme (match your `darkMode` strategy)

Keep the token set small; expand only when you can justify the semantic difference.

## Typography tokens

Use Tailwind config for:

- `fontFamily` (e.g., base/heading)
- custom font sizes only when needed (2xs, 3xs, etc.)

Avoid scattering `text-[11px]` arbitrary values everywhere unless it is truly an exception.

