# Design System Contracts (How To Use Them)

Some teams need enforceable styling rules (especially for data-dense products). A “theme usage contract” is a lightweight, written agreement that keeps UI consistent across many agents and many screens.

This skill does not require Tailwind, but Tailwind pairs well with a contract because it makes violations easy to spot.

## What a contract is

A contract defines:

- **Non-negotiables**: e.g., what the app canvas background is, what primary actions look like.
- **Surface stacking**: a small set of background levels (canvas, surface-1..3).
- **Text + contrast rules**: default text, muted text, and text-on-action tokens.
- **Status hierarchy**: error/warning/success rules so meaning is not diluted.
- **Component rules**: buttons, inputs, tables (and their states).
- **Token map**: semantic tokens -> palette primitives (often via CSS variables).

## How to use a contract (agent behavior)

1) Prefer semantic tokens when they exist (they encode intent).
2) If a semantic token does not exist, use a palette class *and* propose a token addition if the usage repeats.
3) Apply the surface stack rules before adding shadows or random contrast hacks.
4) Keep status colors for meaning, not decoration.
5) Add a QA checklist to the contract (light/dark readability, focus visibility, table legibility).

## Minimal contract skeleton (copy/paste)

```md
# Theme Usage Contract

## Non-negotiables
- ...

## Surface stacking
| level | use | token/class |
| --- | --- | --- |
| 0 | canvas | ... |
| 1 | sections | ... |

## Status hierarchy
- Error:
- Warning:
- Success/Info:

## Component rules (strict)
- Buttons:
- Inputs + focus:
- Tables:

## Semantic token map
| token | maps to | usage |
| --- | --- | --- |
| --ui-canvas | ... | app background |

## QA checklist (required)
- Light/dark readable
- Focus visible
- Status readable
```

## Integration note (optional)

If Tailwind is in use:

- Keep class names aligned with semantic tokens (e.g., `bg-ui-canvas`, `text-ui-text`).
- Use `tailwind-pro` when editing `tailwind.config.*`, content globs, safelist, or token mapping.

