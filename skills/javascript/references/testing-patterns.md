# JavaScript Testing Patterns

Use this when writing JavaScript tests or setting up test infrastructure.

## Framework Choice

- Jest for comprehensive Node/DOM testing.
- Vitest for fast Vite-native testing.

## Core Patterns

- Arrange, Act, Assert (AAA) per test.
- Prefer behavior testing over implementation details.
- Keep tests isolated and deterministic.

## Async Testing

```ts
it("fetches user", async () => {
  const user = await api.fetchUser("1")
  expect(user.id).toBe("1")
})

it("throws on invalid", async () => {
  await expect(api.fetchUser("bad")).rejects.toThrow("Not found")
})
```

## Mocking

- Mock external dependencies (HTTP, filesystem, time).
- Use spies for logging and side-effects.
- Prefer dependency injection for testability.

## Testing Library (UI)

- Prefer semantic queries (`getByRole`, `getByLabelText`).
- Avoid `data-testid` unless necessary.

## Coverage

- Aim for 80%+ meaningful coverage.
- Test error paths and edge cases.

## Quick Checklist

- Clear test names.
- No shared mutable state.
- No reliance on test order.
- Clean up timers and mocks.
