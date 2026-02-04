# Component Variants (Framework-Agnostic)

Goal: define a stable "class contract" per component so callsites stay simple.

## Default structure

- Base: shape + typography + layout + focus ring
- Variants: intent (`primary`, `secondary`, `danger`, `ghost`, ...)
- Sizes: (`sm`, `md`, `lg`, `icon`)
- States: (`disabled`, `loading`, `active`, `invalid`)

## Pattern A: data attributes (portable)

Data attributes reduce conditional class concatenation:

- `data-variant="primary"`
- `data-size="sm"`
- `data-state="loading"`

Then write Tailwind classes that target those attributes when the setup supports it.

Benefits:

- works across frameworks
- callsites stay declarative

## Pattern B: class composition helper (optional)

Optional helpers include:

- a tiny `cn()` function
- `clsx`
- "cva"-style variant builders

Rule: treat it as an *implementation detail*. Do not make the design system depend on a specific library.

## Avoid these traps

- Variant logic duplicated across callsites.
- "utility soup" per usage (hard to change style globally).
- Using raw palette colors everywhere instead of semantic tokens.
