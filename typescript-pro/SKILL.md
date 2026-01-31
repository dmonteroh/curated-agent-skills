---
name: typescript-pro
description: TypeScript best-practices + advanced typing in one skill. Use for strictness/tsconfig decisions, type-level design (generics/conditional/mapped types), fixing type errors, improving type-system performance, and building durable runtime-validated contracts at boundaries.
---

# TypeScript Pro

One canonical TypeScript skill for architecture, day-to-day implementation, and advanced types.

## Use this skill when

- Designing shared types/contracts or public library surfaces
- Fixing hard TypeScript errors, inference issues, or unsafe `any` usage
- Deciding `tsconfig` strictness and an incremental migration strategy
- Improving type-checking performance (slow `tsc`, editor lag)

## Do not use this skill when

- You only need JavaScript guidance
- You need UI/UX design rather than type design

## Workflow (Deterministic)

1. Identify the surface: boundary data vs internal logic.
2. Model invariants with types (make illegal states unrepresentable).
3. Validate boundary inputs at runtime and narrow from `unknown`.
4. Add guardrails (strictness, lint rules, avoid `@ts-ignore` in new code).
5. Verify: typecheck, tests, and (when needed) `tsc --extendedDiagnostics`.

## Focus Areas

- Type design: generics, conditional/mapped/template literal types, utility types.
- TSConfig: strictness, module resolution, incremental builds.
- Runtime contracts: schema validation + parsing at boundaries.
- Type-system performance: diagnosing and reducing type explosions.
- Migration: incremental strictness and safe refactors.

## Output

- Type definitions and a short explanation of the invariants they enforce.
- Concrete fixes for type errors (with minimal unsafe casting).
- TSConfig recommendations and an incremental rollout plan when needed.
- Optional: a performance diagnosis plan for slow type-checking.

## Resources (Optional)

- `resources/implementation-playbook.md`
- `references/best-practices.md`
- `references/style-and-organization.md`
- `references/advanced-types.md`
- `references/tsconfig-baseline.md`
- `references/type-performance.md`
- Script (read-only scan): `scripts/ts_doctor.sh`
