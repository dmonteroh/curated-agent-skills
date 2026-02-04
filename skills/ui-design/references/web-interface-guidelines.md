# Web Interface Guidelines (Local, Offline)

This is a locally vendored checklist. Use it for UI code review when you want consistent, high-signal findings.

Output style for findings: `file:line: issue (fix)`.

## Accessibility

- Icon-only buttons need an accessible name (`aria-label` or visible text).
- Form controls need labels (`<label>` or `aria-label`).
- Prefer semantic elements: `<button>` for actions; `<a>`/router links for navigation (avoid `<div onClick>`).
- Images need `alt` (or `alt=""` if decorative).
- Decorative icons should be `aria-hidden="true"`.
- Async updates (toasts/validation) should announce via `aria-live="polite"` when appropriate.
- Headings must be hierarchical (`h1`..`h6`); include a skip link for main content.
- Do not rely on color alone to communicate state (pair with text/icon/shape).

## Focus States

- Interactive elements need visible focus styles (prefer `:focus-visible`).
- Never remove focus outlines without a replacement.
- Use `:focus-within` for compound widgets.

## Forms

- Inputs should use appropriate `type`, `name`, `autocomplete`, and `inputmode`.
- Do not block paste.
- Error handling:
  - errors appear next to fields
  - focus first error on submit (when feasible)
- Warn before navigation with unsaved changes (route guard / beforeunload) when data loss risk exists.
- Keep submit buttons enabled until request starts; show busy state during request.

## Animation

- Honor `prefers-reduced-motion` (reduce or disable non-essential animation).
- Animate `transform`/`opacity` where possible; avoid `transition: all`.
- Animations should be interruptible and respond to user input mid-motion.

## Typography

- Prefer consistent typographic scale; avoid arbitrary font-size values unless justified.
- Prefer ellipsis rendering that matches the platform; avoid "..." as a substitute for truncation logic.

## Layout + responsiveness

- Use a consistent spacing scale; avoid raw pixels unless exceptional.
- Ensure touch targets are usable on mobile (padding/min sizes).
- Avoid layout shift on loading: reserve space for images/skeletons when possible.

## Links + navigation

- Links should be distinguishable from body text (underline, weight, or color + affordance).
- External links should be clearly indicated when it affects user expectations.

## Performance hygiene (UI-facing)

- Avoid unnecessarily large images; use responsive images where the stack supports it.
- Avoid heavy JS for simple interactions.
- Prefer CSS for simple transitions; keep animation counts low in dense apps.
