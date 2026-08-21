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

## Token boundary: intent versus mechanics

Tokenize design *intent*. Keep browser *mechanics* raw.

- **Intent — tokenize it.** Spacing steps, content width, gutters, section gaps, density steps, radius steps, type scale, surface levels, semantic colour. These encode a decision someone made, and the token is what makes the decision reusable and reviewable.
- **Mechanics — leave them raw.** `auto`, `%`, `min-content`, `max-content`, `fit-content`, `clamp()`, viewport and container units, intrinsic sizing, `minmax()` tracks. These encode how the layout responds, not what it should look like. A `clamp(1rem, 4vw, 2rem)` gap or a `minmax(min(16rem, 100%), 1fr)` track is a mechanic, not a magic number — do not force it into a token.

The failure this prevents is token bloat: every fluid value promoted to a named token produces a system full of one-use tokens that carry no intent and cannot be reasoned about as a set. The inverse failure is the more familiar one — an intent value hardcoded at the call site, which makes the decision invisible and unchangeable in one place.

Applying the boundary to the usual "no hardcoded values" rule: a raw value is a defect when it stands in for an intent token that exists or should exist, and is correct when it is a browser mechanic doing a job no token can do.

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
- Use `tailwind` when editing `tailwind.config.*`, content globs, safelist, or token mapping.

