# Advanced Types (Fast Pattern Index)

This reference is a compact, high-signal catalog of TypeScript type-level patterns.

Use this when you need to:

- design a typed public API (library/shared package)
- model tricky invariants (results, state machines, config schemas)
- extract types from runtime values safely
- avoid `any` while keeping call sites ergonomic

## Contents

- Generics
- Conditional types + `infer`
- Mapped types + key remapping
- Template literal types
- Common utility patterns
- Type-level performance tips

## Generics

### Generic constraints (most common)

```ts
interface HasId { id: string }

function byId<T extends HasId>(items: readonly T[]): Record<string, T> {
  return Object.fromEntries(items.map((x) => [x.id, x]));
}
```

### Prefer inference (don’t over-annotate)

```ts
function wrap<T>(value: T) {
  return { value };
}

const x = wrap({ a: 1 }); // infers T
```

## Conditional Types + `infer`

### Extract return / params

```ts
type Fn = (...args: any[]) => any;

type Ret<F extends Fn> = F extends (...a: any[]) => infer R ? R : never;

type Params<F extends Fn> = F extends (...a: infer A) => any ? A : never;
```

### Narrow unknown with a type guard

```ts
function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null;
}
```

### Distribute (careful)

Conditional types distribute over unions.

```ts
type ToArray<T> = T extends any ? T[] : never;
// string | number -> string[] | number[]
```

Use this intentionally; it can create huge unions and slow `tsc`.

## Mapped Types + Key Remapping

### Readonly / Mutable

```ts
type Mutable<T> = { -readonly [K in keyof T]: T[K] };
```

### Pick by value type

```ts
type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K]
};
```

### Key remap (getter map)

```ts
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K]
};
```

## Template Literal Types

### Event names

```ts
type Event = "click" | "focus" | "blur";

type Handler = `on${Capitalize<Event>}`; // onClick | onFocus | onBlur
```

### Typed paths (bounded)

Keep path generation bounded; deep recursion can be slow.

```ts
type Path1<T> = {
  [K in keyof T & string]: K
}[keyof T & string];

type Path2<T> = {
  [K in keyof T & string]:
    | K
    | (T[K] extends object ? `${K}.${Path1<T[K]>}` : never)
}[keyof T & string];
```

## Common Utility Patterns

### Result

```ts
type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };
```

### Brand (nominal-ish typing)

```ts
type Brand<T, B extends string> = T & { readonly __brand: B };

type UserId = Brand<string, "UserId">;
```

### XOR (mutually exclusive shapes)

```ts
type Without<T, U> = { [K in Exclude<keyof T, keyof U>]?: never };

type XOR<T, U> = (T | U) extends object ? (Without<T, U> & U) | (Without<U, T> & T) : T | U;
```

### Exactly one key required

```ts
type ExactlyOne<T> = {
  [K in keyof T]-?: Required<Pick<T, K>> & Partial<Record<Exclude<keyof T, K>, never>>
}[keyof T];
```

### DeepPartial (use sparingly)

```ts
type DeepPartial<T> = T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } : T;
```

### Exhaustiveness

```ts
function assertNever(x: never): never {
  throw new Error(`Unexpected: ${String(x)}`);
}
```

### `satisfies` (best practice for config)

```ts
const cfg = {
  env: "prod",
  port: 8080,
} satisfies { env: "dev" | "prod"; port: number };

// cfg.env stays the literal "prod" while still being checked.
```

## Type-Level Performance Tips

- Prefer simpler exported/public types; keep complex types internal.
- Avoid deep recursive conditional types and giant distributed unions.
- Use helper types with names (improves readability and sometimes compiler work).
- Beware `as const` on huge objects; it can create enormous literal unions.
- If editors lag, measure:
  - `tsc --noEmit --extendedDiagnostics`

## Anti-Patterns

- `any` at boundaries (use `unknown` + runtime validation).
- `@ts-ignore` for convenience.
- “Type golf”: extremely clever types that no one can maintain.
- Using advanced types to avoid writing runtime validation.
