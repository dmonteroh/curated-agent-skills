# Testing Anti-Patterns (Fast Review Checklist)

Use this when writing or reviewing tests. The goal is fewer tests with higher signal.

## Core principle

Test what the code does, not what the mocks do.

## Anti-patterns and fixes

1) Testing mock calls instead of behavior
- Smell: `expect(mock).toHaveBeenCalledWith(...)` with no assertion on the result.
- Fix: assert output/state/side-effects that users care about.

2) “Test-only” methods in production code
- Smell: `_resetForTesting`, `clearForTests`, debug hooks shipped for tests.
- Fix: use fresh instances per test; create test helpers/builders in the test suite.

3) Mocking everything
- Smell: every dependency mocked, test still passes with nonsense returns.
- Fix: mock at the boundary (network/clock/fs/external services), keep core logic real.

4) Incomplete mocks / fake data that can’t happen in reality
- Smell: mocks return `{ ok: true }` but production expects fields that are missing.
- Fix: use factories/builders that fill sensible defaults; mirror real shapes.

5) Integration/E2E as an afterthought
- Smell: “we’ll add tests later,” then the suite never stabilizes.
- Fix: ship feature + tests together; at least one negative case per boundary.

## Detection checklist

- Do tests assert behavior or only that mocks were called?
- Are tests deterministic (no real time/random/network unless controlled)?
- Are error paths covered (invalid input, authz, not-found, conflict)?
- Do tests fail for the right reason (no brittle snapshots/timeouts)?

