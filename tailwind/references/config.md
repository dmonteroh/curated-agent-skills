# Tailwind Config Essentials (content, safelist, theme, plugins)

This is intentionally short. Verify specifics against your Tailwind version docs.

## `content`

Goal: include every path that can produce Tailwind class names at build time.

Checklist:

- include app sources (e.g., `src/**/*.{ts,js,html,svelte,vue,tsx,jsx}`)
- include component libraries that ship templates (if you use them)
- include MD/MDX if class names appear there

Failure mode:

- missing content path => "works in dev, missing in prod" (purged classes)

## `safelist`

Use only when class names are constructed dynamically (string concatenation, CMS data, runtime theme keys).

Rules:

- prefer *tight* patterns scoped to a namespace you own (e.g., `ui-`).
- prefer enumerating explicit class lists when the set is small.
- keep variants explicit (`hover`, `focus`, `disabled`, etc.)

Failure modes:

- too broad => huge CSS bundle
- too narrow => missing styles in prod

## `theme.extend`

Prefer semantic tokens over raw palette values:

- `ui.canvas`, `ui.text`, `ui.border`, `ui.action`, status colors
- optional: "tag" colors or product-specific token groups

Best practice:

- map Tailwind colors to CSS variables so theme changes do not change class names

## `darkMode`

Pick one strategy and make it consistent:

- `class` is the easiest to control across apps.

## Plugins

Keep plugins minimal and intentional.

- if you add plugins, document *why* and how they change class surfaces

