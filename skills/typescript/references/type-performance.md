# Type-System Performance

TypeScript can become slow due to pathological types and very large inferred unions.

## Diagnose

- `tsc --noEmit --extendedDiagnostics`
- `tsc --generateTrace <dir>` (for deep analysis)

## Common Causes

- Deeply recursive conditional types.
- Very large unions from overusing generic inference.
- Huge inferred object types from `as const` on large data.
- Public API types that explode downstream (library types).

## Practical Fixes

- Introduce intentional "type boundaries":
  - Export simpler public types; keep internal types fancy.
- Prefer named helper types over nested inline conditionals.
- Avoid distributing conditional types over massive unions unless needed.
- Use `satisfies` to keep literals without freezing the whole structure.
- In libraries, consider `tsd`-style tests for public surface stability.
