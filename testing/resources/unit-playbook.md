# Unit Testing Playbook

Fast unit testing guidance that prioritizes signal quality and maintainability.

## Principles

- Test behavior, not implementation details.
- Prefer deterministic, hermetic tests.
- Mock at boundaries (network, filesystem, clock, random), not internal logic.
- Name tests by scenario + expected outcome.

## Minimal scenario set

- Happy path
- Boundary conditions
- Invalid inputs / exceptions
- State transitions / idempotency (if applicable)

## Test quality checklist

- Assertions are meaningful (not `is not None`).
- Tests fail for the right reason (avoid brittle snapshots unless needed).
- Setup is minimal; shared fixtures are justified.

## When to stop and add higher-level tests

- When behavior spans multiple modules/services.
- When integration boundaries are the source of bugs (DB, queue, HTTP).
