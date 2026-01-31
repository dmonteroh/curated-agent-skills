# TDD Iron Laws (Compact)

Use this when you want high signal tests and a tight feedback loop. Keep it pragmatic: TDD is a tool, not a religion.

## The three laws (what “TDD” actually means)

1) Do not write production code unless it is to make a failing test pass.
2) If you didn't watch the test fail, you don't know what it proves.
3) Every unit of production behavior should be defended by a test that failed first (or it's not TDD).

## Red / Green / Refactor loop

- RED: write the smallest test that expresses the next behavior; run it and observe meaningful failure.
- GREEN: implement the simplest code to pass *only that test* (no extra features).
- REFACTOR: improve design/clarity while keeping tests green; no new behavior.

## Verification rule (non-negotiable)

Before claiming a test is “good”:

- You observed it fail for the expected reason.
- The failure message is understandable.
- The test would fail if you remove/break the behavior.

## Where TDD pays off most

- tricky domain rules / state transitions
- concurrency, retries, idempotency
- data transformations and boundary validation
- bug fixes (write the regression test first)

