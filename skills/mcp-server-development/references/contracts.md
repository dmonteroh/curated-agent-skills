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

## Success envelope (recommended)

`errors.md` normalizes the failure path into one fixed shape. Apply the same discipline to the success path so a caller does not have to re-read prose to learn what happened:

- `status` — succeeded, or succeeded with warnings.
- `summary` — one line the caller can log or surface verbatim.
- `next_actions` — the follow-up calls that make sense from this result. A tool that declares this field always emits it: an empty list means "nothing further is needed", which is information; an absent field is not.
- `artifacts` — stable identifiers or paths this call created or changed.

Recommended, not mandatory. Concise-by-default still governs: declare the fields that carry real information for a given tool in its output schema rather than padding every response with all four. Keep the names identical across every tool that declares them, so a caller learns the shape once and reads every tool with it.

## Safety hints

- Mark tools correctly:
  - `readOnlyHint`: true for pure reads
  - `idempotentHint`: true when repeating yields the same result
  - `destructiveHint`: true for operations that can delete/overwrite

