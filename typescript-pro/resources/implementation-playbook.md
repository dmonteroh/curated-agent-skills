# TypeScript Pro - Implementation Playbook

Use this playbook when you need a deterministic workflow for designing types, fixing type errors, or evolving TS strictness without slowing development.

## Quickstart Workflow

1) Identify the surface
- Is this a *boundary* (HTTP/env/DB/external API) or *internal logic*?

2) Choose the shape
- Prefer discriminated unions for state/results.
- Prefer branded types for identifiers when helpful.

3) Validate boundaries
- Add runtime validation and narrow from `unknown`.

4) Add guardrails
- Ban `any` in new code.
- Replace `@ts-ignore` with `@ts-expect-error`.

5) Verify
- Run typecheck and ensure no new lint errors.

## Output Expectations

When producing TypeScript changes, include:

- The core type definitions.
- How the types enforce invariants.
- Edge cases and how they are represented.
- (If applicable) a migration plan for call sites.

## References

- Best practices: `references/best-practices.md`
- Advanced patterns: `references/advanced-types.md`
- TSConfig baseline: `references/tsconfig-baseline.md`
- Type performance: `references/type-performance.md`
