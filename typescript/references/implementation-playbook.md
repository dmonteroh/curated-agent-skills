# TypeScript Implementation Playbook

Use this playbook when a deterministic workflow is needed for designing types, fixing type errors, or evolving TypeScript strictness without slowing development.

## Quickstart workflow

1) Identify the surface
- Classify the request as a *boundary* (HTTP/env/DB/external API) or *internal logic*.

2) Choose the shape
- Prefer discriminated unions for state/results.
- Prefer branded types for identifiers when helpful.

3) Validate boundaries
- Add runtime validation and narrow from `unknown`.

4) Add guardrails
- Avoid `any` in new code.
- Replace `@ts-ignore` with `@ts-expect-error`.

5) Verify
- Run the typecheck and confirm no new lint errors.

## Output expectations

When producing TypeScript changes, include:

- The core type definitions.
- How the types enforce invariants.
- Edge cases and how they are represented.
- (If applicable) a migration plan for call sites.

## Related references

- Best practices: `best-practices.md`
- Advanced patterns: `advanced-types.md`
- TSConfig baseline: `tsconfig-baseline.md`
- Type performance: `type-performance.md`
