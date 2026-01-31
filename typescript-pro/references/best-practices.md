# TypeScript Best Practices

This reference is intentionally framework-agnostic. Apply it to Node backends, React frontends, libraries, CLIs, and scripts.

## Defaults

- Prefer **`strict: true`** in `tsconfig.json`.
- Keep types close to the code they describe; centralize only shared domain contracts.
- Use runtime validation at external boundaries (HTTP, env, DB rows, file IO).

## Type Modeling

- Prefer `unknown` over `any` at boundaries.
- Prefer **discriminated unions** over boolean flags:

```ts
type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function isOk<T, E>(r: Result<T, E>): r is { ok: true; value: T } {
  return r.ok;
}
```

- Use `satisfies` to keep literal precision without narrowing the variable:

```ts
const routes = {
  health: "/health",
  users: "/v1/users",
} satisfies Record<string, `/${string}`>;
```

- Use `as const` for immutable config and discriminants.
- Prefer **`type`** for unions/intersections and **`interface`** for object shapes you expect to be extended/merged.

## Guardrails

- Avoid `@ts-ignore`; prefer `@ts-expect-error` with a comment explaining why.
- Make illegal states unrepresentable.
- Use exhaustive checks to prevent silent drift:

```ts
function assertNever(x: never): never {
  throw new Error(`Unexpected: ${String(x)}`);
}

type Status = "idle" | "loading" | "done";

function toLabel(s: Status): string {
  switch (s) {
    case "idle": return "Idle";
    case "loading": return "Loading";
    case "done": return "Done";
    default: return assertNever(s);
  }
}
```

## Runtime Validation

TypeScript types do not validate runtime data.

- Validate:
  - HTTP request bodies/params
  - env vars
  - DB rows
  - external API payloads
- Use a schema library if available (e.g. Zod/Valibot/Yup/TypeBox), but keep the approach generic.

## Async & Error Handling

- Type your error boundaries:
  - `catch (e: unknown)` then narrow
- Avoid throwing strings.

## Project Structure

- Prefer explicit exports. Keep barrel files intentional (don’t create cycles).
- Enforce `importsNotUsedAsValues: "error"` and use `import type`.
- Avoid circular dependencies (they break types and runtime).

## Incremental Strictness (For Legacy Code)

- Turn on `strict` as a target.
- Add stricter flags gradually (one by one) and fix:
  - `noUncheckedIndexedAccess`
  - `exactOptionalPropertyTypes`
  - `noImplicitOverride`
  - `noFallthroughCasesInSwitch`

## Build Performance

- Prefer project references in monorepos.
- Use incremental builds.
- Measure first: run `tsc --noEmit --extendedDiagnostics` to find hotspots.
