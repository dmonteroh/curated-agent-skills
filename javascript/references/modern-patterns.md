# Modern JavaScript Patterns

Use this as a quick reference for ES6+ syntax and patterns.

## Core Syntax

- Arrow functions for callbacks and lexical `this`.
- Destructuring for objects/arrays.
- Spread/rest for immutable updates and variadic functions.
- Template literals for readable strings.

## Async Patterns

- Prefer `async/await` with `try/catch`.
- Use `Promise.all` for independent work.
- Wrap long-running operations with timeouts.

## Functional Patterns

- Prefer `map`, `filter`, `reduce` over manual loops.
- Use pure functions where possible.
- Avoid mutating input data.

## Modern Operators

- Optional chaining: `obj?.prop`.
- Nullish coalescing: `value ?? default`.
- Logical assignment: `||=`, `&&=`, `??=`.

## Performance Notes

- Avoid blocking the event loop.
- Debounce or throttle hot UI handlers.
- Memoize expensive computations where needed.

## Quick Example

```js
const normalizeUser = ({ name, email, ...rest }) => ({
  ...rest,
  name: name.trim(),
  email: email.toLowerCase(),
})
```
