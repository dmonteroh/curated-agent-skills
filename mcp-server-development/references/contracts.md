# Contracts (Inputs/Outputs)

## Inputs

- Use strict schemas:
  - TypeScript: Zod `.strict()`
  - Python: Pydantic strict models
- Prefer enums over freeform strings.
- Put examples in field descriptions.
- Keep identifiers consistent (if a tool takes `user_id`, do not call it `id` elsewhere).

## Outputs

- Prefer stable JSON objects with a small, documented set of fields.
- Return both:
  - stable identifiers (IDs)
  - human-readable labels (names/titles)
- Support a `detail` or `format` option if some callers need more output.

## Safety hints

- Mark tools correctly:
  - `readOnlyHint`: true for pure reads
  - `idempotentHint`: true when repeating yields the same result
  - `destructiveHint`: true for operations that can delete/overwrite

