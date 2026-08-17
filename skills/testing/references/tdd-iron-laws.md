# TDD Iron Laws (Compact)

Use this to keep high-signal tests and a tight feedback loop. Keep it pragmatic: TDD is a tool, not a religion.

## The three laws (what “TDD” actually means)

1) Do not write production code unless it is to make a failing test pass.
2) If the test failure was not observed, the proof is unknown.
3) Every unit of production behavior should be defended by a test that failed first (or it's not TDD).

## Red / Green / Refactor loop

- RED: write the smallest test that expresses the next behavior; run it and observe meaningful failure.
- GREEN: implement the simplest code to pass *only that test* (no extra features).
- REFACTOR: improve design/clarity while keeping tests green; no new behavior.

## Two valid RED paths

RED can be proven two ways, and only one of them has to hold:

- **Runtime RED**: the test target compiles, the new or changed test actually executes, and it fails.
- **Compile-time RED**: in a compiled or statically-typed context, the new test references or exercises a code path that does not exist or does not typecheck yet, and the compiler's own failure — missing symbol, type error — is the RED signal.

Either path counts only if the failure traces to the intended missing implementation or bug. A failure caused by an unrelated syntax error, broken test setup, or a missing dependency is not RED; it is a broken test run, and fixing it is not GREEN. A test that was written but never compiled or executed is not RED at all.

In a dynamically-typed language with no compile step this collapses back to runtime RED — compile-time RED is a conditional second path, not a replacement.

## Verification rule (non-negotiable)

Before claiming a test is “good”:

- The failure was observed for the expected reason.
- The failure message is understandable.
- The test would fail if the behavior is removed or broken.

## Making that observation durable (git repositories only)

An observed failure is proof only for whoever watched it; after the session it rests on the acting agent's own narration. Where the repository is under git, capture the observation as commits so a reviewer — or the next session — can check it independently:

- One commit for the state where the failing test exists and RED was validated; one for the minimal fix with GREEN validated; optionally one for the refactor. Separate evidence-only commits are unnecessary when the test commit *is* the RED state and the fix commit *is* the GREEN state.
- State in each message which stage it captures and what was observed: the test target that ran, and the reason it failed or passed.
- Before treating a checkpoint as satisfied, verify the commit is reachable from the current `HEAD` on the active branch and belongs to this task's sequence — `git merge-base --is-ancestor <commit> HEAD` exits non-zero when it is not. A commit on another branch, or from unrelated earlier work, is not evidence for this change.
- If the checkpoints will be squashed, copy the RED/GREEN/refactor summary into the squash commit body or the pull-request description first, or the proof disappears with the commits.

Conditional by nature: outside a git repository, or where commit granularity is set by another convention, record the same proof another way. What matters is that "the failure was observed, for this reason" outlives the session, not the specific commit layout.

## Where TDD pays off most

- tricky domain rules / state transitions
- concurrency, retries, idempotency
- data transformations and boundary validation
- bug fixes (write the regression test first)
