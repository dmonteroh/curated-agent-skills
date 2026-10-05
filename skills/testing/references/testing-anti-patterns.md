# Testing Anti-Patterns

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
- Not the same as a seam: a constructor parameter for the clock or HTTP client is production interface that tests also use. A method that exists only so a test can reach state is a backdoor.

3) Mocking everything
- Smell: every dependency mocked, test still passes with nonsense returns.
- Fix: mock at the boundary (network/clock/fs/external services), keep core logic real.

4) Incomplete mocks / fake data that can’t happen in reality
- Smell: mocks return `{ ok: true }` but production expects fields that are missing.
- Fix: use factories/builders that fill sensible defaults; mirror real shapes.

5) Integration/E2E as an afterthought
- Smell: “we’ll add tests later,” then the suite never stabilizes.
- Fix: ship feature + tests together; at least one negative case per boundary.

6) Testing the language or a third-party library
- Smell: the assertion would hold for any caller of the platform or the package.
- Fix: assert on what this code does with it — the mapping, the arguments it chose, its handling of the library's errors.

```python
# Wrong: tests that the standard library and the date package work
assert json.loads('{"a": 1}') == {"a": 1}
assert parse_date("2026-01-31") + timedelta(days=1) == date(2026, 2, 1)

# Right: tests this code's rule, which happens to use them
assert next_billing_date(date(2026, 1, 31)) == date(2026, 2, 28)
```

7) Pinned to implementation
- Smell: call counts or call order on internal collaborators, a spy on a private helper, an assertion on an intermediate structure.
- Fix: assert on the result a caller can see. Run the refactor check: would a rewrite with identical behavior still pass?

```ts
// Wrong: breaks if the cache is replaced by memoization, passes if the price is wrong
expect(priceCache.get).toHaveBeenCalledTimes(1);

// Right
expect(quote(order)).toEqual({ subtotal: 40, tax: 8, total: 48 });
```

8) Reaching into private state (rule: "Before writing a test" in `SKILL.md`)

```ts
// Wrong: sets an internal form control, then reads a private field
fixture.componentInstance["form"].controls.email.setValue("not-an-email");
expect(fixture.componentInstance["submitted"]).toBe(false);

// Right: drives and reads the DOM, as a user would
await user.type(screen.getByLabelText("Email"), "not-an-email");
await user.click(screen.getByRole("button", { name: "Sign up" }));
expect(screen.getByText("Enter a valid email address")).toBeVisible();
```

9) Asserting that something removed is gone
- Smell: after a removal, a new test that a module, import, flag, route, or package does not exist.
- Fix: delete the removed feature's tests and keep the remaining suite green. That is the verification.

```ts
// Wrong: written after "remove moment.js"
it("does not depend on moment", () => {
  expect(pkg.dependencies.moment).toBeUndefined();
});
```

10) Tautological expected value
- Smell: the expected side calls the unit under test, re-implements its logic, or was pasted from its current output.
- Fix: a literal worked out from the contract. If the contract does not say what the answer is, that is a question to ask, not a value to copy.

11) Unreachable or swallowed assertion
- Smell: `expect` inside a `catch` with no failure when nothing throws, inside a callback never invoked, or after an un-awaited promise.
- Fix: use the runner's own throws or rejects matcher, await every promise, and check the test fails when the code is broken.

```ts
// Wrong: passes when parse() does not throw
try { parse("bad"); } catch (e) { expect(e.code).toBe("E_SYNTAX"); }

// Right
expect(() => parse("bad")).toThrow(expect.objectContaining({ code: "E_SYNTAX" }));
```

12) Rubber-stamp snapshot
- Smell: a large snapshot or golden file re-blessed whenever it goes red.
- Fix: a targeted assertion on the values that define the contract. A snapshot is updated only when the change it shows was the intended behavior change, and the update says so.

## Detection checklist

- Do tests assert behavior or only that mocks were called?
- Would each test fail if the behavior it names were broken? Was that observed?
- Would each test survive a refactor that keeps the observable behavior?
- Does any test only prove the language or a dependency works, or that something removed is gone?
- Is any expected value computed by the code under test?
- Does any test read or set private state instead of the public surface?
- Are tests deterministic (no real time/random/network unless controlled)?
- Are error paths covered (invalid input, authz, not-found, conflict)?
- Do tests fail for the right reason (no brittle snapshots/timeouts)?
