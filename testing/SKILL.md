---
name: testing
description: Unified testing skill for speed + quality. Supports two modes: unit test generation and end-to-end/automation strategy. Includes safe-by-default scripts to scaffold test plans and generate a deterministic testing report. Works standalone; if stack-specific testing skills exist, prefer them for framework/tooling details.
---

# testing

One canonical testing skill that combines:
- **unit**: generate and improve unit tests quickly with strong edge-case focus
- **automation**: end-to-end / integration / CI strategy and reliability (flakiness, runtime, reporting)

## Use this skill when

- Adding unit tests to existing code.
- Designing integration/E2E testing strategy.
- Improving test stability, runtime, CI signal quality.
- Establishing testing standards (test pyramid, quality gates).

## Do not use this skill when

- There is no code or behavior defined to test.
- The only requirement is an informal discussion of testing theory.

## Modes

### Mode: unit (fast unit test generation)

Goal: maximize coverage of changed behavior with maintainable tests.

Workflow:
1) Identify units under test + seams (pure functions, modules, services).
2) Enumerate scenarios:
   - happy path
   - boundary conditions
   - error handling
   - state transitions
3) Add minimal fixtures/mocks and avoid over-mocking.
4) Ensure tests are deterministic and fast.

Output:
- test file(s) + brief explanation
- gaps / follow-ups

### Mode: automation (E2E/integration strategy)

Goal: build a fast, reliable feedback loop with the right test mix.

Workflow:
1) Define critical journeys and risks (auth, payments, data integrity, permissions).
2) Choose test layers:
   - unit -> integration -> contract -> E2E (as needed)
3) Design for stability:
   - hermetic environments where possible
   - test data management
   - retries only at the framework edge (avoid hiding bugs)
4) Add CI quality gates:
   - smoke suite, full suite, perf gates (if relevant), reporting

Output:
- recommended test pyramid + tooling
- execution plan and CI integration steps

## Quick start (in a real repo)

```sh
./testing/scripts/test.sh plan
./testing/scripts/test.sh report
```

Outputs a deterministic report under `docs/_docgen/testing/`.

## Integration notes

- Convert testing work into tasks/tracks via `tracks-conductor-protocol` when non-trivial.
- If tests reveal an architectural decision (e.g., contract strategy, isolation approach), record an ADR via `adr-madr-system`.
- For code review alignment, use `code-review` to enforce “tests required” gates.
- For performance-related tests, coordinate with `performance`.

## Resources

- `resources/unit-playbook.md` (unit testing patterns)
- `resources/automation-playbook.md` (E2E/CI strategy patterns)
- `scripts/test.sh` (wrapper)
