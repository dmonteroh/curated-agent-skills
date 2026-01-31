# Responsive + Accessibility Conventions (Tailwind)

## Focus and keyboard

- Ensure focus rings are visible on interactive elements.
- Do not remove focus outlines without a replacement (`focus-visible:*`).
- Keep tab order logical; avoid `tabindex` hacks unless necessary.

## Touch targets

- Buttons/links should be comfortable on mobile (padding, min sizes).

## Disabled vs readonly vs loading

- Disabled: visually distinct and non-interactive.
- Readonly: non-editable but still focusable (form fields).
- Loading: show busy state and prevent double-submits (or idempotency).

## Contrast

- Treat text-on-action colors as tokens (e.g., `text-ui-on-action`) so you do not accidentally ship low contrast.

## Breakpoints

- Choose a breakpoint strategy and keep it consistent.
- Prefer mobile-first class order: base -> `sm:` -> `md:` -> ...
- Avoid mixing layout paradigms in the same component (grid + flex) unless justified.

