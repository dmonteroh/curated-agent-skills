# TypeScript Style & Organization (High-Signal Conventions)

Use these conventions when they improve consistency and reduce agent confusion.

Default rule: follow the existing repo style. If the repo has no strong style yet, adopt the defaults below.

## Type vs Interface

- Prefer `type` for unions/intersections and local composition.
- Prefer `interface` when you intentionally want declaration merging or extensible object shapes.

If a codebase strongly prefers one, follow that.

## "readonly" Usage

`readonly` is shallow; use it where it prevents real footguns:

- Prefer `readonly` for arrays/maps/sets and exported constants.
- Avoid blanket `readonly` on every object property (noise unless it meaningfully prevents mutation).

## Acronyms in camelCase

Treat acronyms as words:

- `parseUrl`, `readJson`, `httpClient`, `customerId`
- Avoid `parseURL`, `readJSON`, `HTTPClient`, `customerID` unless matching upstream APIs.

## Modern TS Narrowing

- TS 5.5+ often infers narrowing from `.filter()`; avoid redundant type predicates unless inference fails.

## Co-location (Avoid "type buckets")

Avoid dumping unrelated types into generic buckets like `types/models.ts`.

Prefer:

- Service-specific: `services/<service>/types.ts`
- Domain-specific: `domains/<domain>/types.ts`
- Component-specific: inline in the component file
- Cross-domain: `types/<specific-topic>.ts` only when truly shared

## Constant Array Patterns (Options/IDs/Labels)

When modeling stable option sets:

- Source of truth values: `SCREAMING_SNAKE_CASE` arrays (optionally with units)
  - `BITRATES_KBPS`, `SAMPLE_RATES`
- Derived UI options: `_OPTIONS`
  - `BITRATE_OPTIONS`
- Derived IDs (for validation): `_IDS`
  - `PROVIDER_IDS`
- Label map: `_TO_LABEL`
  - `LANGUAGES_TO_LABEL`

Prefer `satisfies` for typed constant arrays:

```ts
export const RECORDING_MODES = [
  { label: "Manual", value: "manual" },
  { label: "Upload", value: "upload" },
] as const satisfies { label: string; value: "manual" | "upload" }[];

export const RECORDING_MODE_IDS = RECORDING_MODES.map((o) => o.value);
```

## Factory Functions: Parameter Destructuring

Prefer destructuring in the signature (clear defaults at the API boundary):

```ts
function createThing({ foo, bar = 10 }: { foo: string; bar?: number }) {
  return { foo, bar };
}
```

Body destructuring is still valid when you need `"key" in opts` semantics or complex normalization.

## Single-use Definitions in Tests

Inline one-off builders/config to keep context at the call site.

Extract when:

- reused multiple times
- you call methods on the intermediate object
- it becomes too large to read (~15-20+ lines)

## Test File Organization

Shadow source files with colocated tests:

- `foo.ts` -> `foo.test.ts` in the same folder

Skip tests for:

- type-only modules
- barrel re-exports

## Branded Types

Avoid scattered `as SomeBrand` assertions.

Prefer a single brand constructor:

```ts
type Brand<T, B extends string> = T & { readonly __brand: B };

export type UserId = Brand<string, "UserId">;

export function UserId(id: string): UserId {
  // Optional: validate format here.
  return id as UserId;
}
```

This makes boundaries explicit and easy to audit.

## Schema Libraries (Arktype/Zod/etc.)

If your codebase uses a schema library that converts to JSON Schema/OpenAPI:

- Prefer optional property syntax that round-trips cleanly.
- Avoid encoding `undefined` unions if the converter can’t represent it.

(Exact syntax depends on the library; follow that library's recommended pattern.)
