---
name: testing
description: "Create unit tests, API tests, and automation strategies with clear decision points, pitfalls, and deterministic reporting via local scripts."
category: workflow
---

# testing

One testing skill that covers:
- **unit**: generate or improve unit tests with edge-case coverage
- **automation**: integration/E2E strategy, CI feedback loops, and stability
- **api**: API behavior testing and deterministic mocking

## Use this skill when

- Adding unit tests to existing code.
- Designing integration/E2E testing strategy.
- Improving test stability, runtime, CI signal quality.
- Establishing testing standards (test pyramid, quality gates).

## Do not use this skill when

- There is no code or behavior defined to test.
- The only requirement is an informal discussion of testing theory.

## Trigger phrases

- "add tests for this change"
- "write a testing plan"
- "make our tests faster/flaky"
- "mock the API so frontend can proceed"

## Inputs you need

- Code or behavior to test (files, diff, or explicit requirements).
- Target runtime/framework (language + test runner).
- Constraints: CI limits, runtime budgets, and determinism requirements.
- Access to the repo for file edits, if writing tests.

## Mode selection (decision guide)

- If the user asks for new/updated tests for code changes, choose **unit**.
- If the user asks for test strategy, CI gating, or flakiness fixes, choose **automation**.
- If the focus is API contracts or mocking dependencies, choose **api**.
- If none apply, ask for clarification and stop.

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
3) Decide if mocks are required:
   - If external I/O exists, stub at the boundary.
   - If logic is pure, avoid mocking entirely.
4) Implement minimal fixtures and assertions.
5) Ensure tests are deterministic and fast.

Output:
- Test file(s) + brief explanation
- Gaps, risks, and follow-ups

### Mode: automation (E2E/integration strategy)

Goal: build a fast, reliable feedback loop with the right test mix.

Workflow:
1) Define critical journeys and risks (auth, payments, data integrity, permissions).
2) Choose test layers:
   - If unit coverage is low, start there.
   - If cross-service behavior is risky, add integration/contract tests.
   - If business-critical flows fail end-to-end, add E2E tests.
3) Design for stability:
   - hermetic environments where possible
   - test data management
   - retries only at the framework edge (avoid hiding bugs)
4) Add CI quality gates:
   - smoke suite, full suite, perf gates (if relevant), reporting

Output:
- Recommended test pyramid + tooling
- Execution plan and CI integration steps

### Mode: api (API testing + mocking, pragmatic)

Goal: test API behavior with strong signal and enable parallel development without relying on live dependencies.

Use when:
- Frontend/client work needs stable API behavior before the backend is ready.
- Integration tests need to replace third-party/partner APIs with deterministic stubs.
- You want API contract confidence (schemas, error shapes, pagination/auth semantics).

Defaults:
- Prefer in-process stubs/mocks where possible (cheapest, least brittle).
- Use a standalone mock server only when consumers truly need it.
- Keep fixtures deterministic; avoid randomness unless explicitly seeded.

Outputs:
- API test plan (what to cover + where: unit/integration/e2e)
- Mock/stub approach (in-process vs mock server) + scenarios
- Fixtures and how to regenerate them

## Common pitfalls to avoid

- Over-mocking internals instead of stubbing boundaries.
- Non-deterministic fixtures (randomness without seeding).
- Slow E2E suites without smoke tests.
- Retrying tests that hide real failures.

## Output contract (always report)

Use this format whenever the skill runs:

- Mode: unit | automation | api
- Scope: what code/flows were covered
- Assumptions: constraints or unknowns
- Work completed: tests added/strategy decided
- Files touched or created
- Tests run: commands or “not run”
- Risks/gaps + recommended follow-ups

## Examples

Trigger test prompts:
- "Add unit tests for the new validation function"
- "Create a testing strategy for our checkout flow"

## Quick start (in a real repo)

```sh
./testing/scripts/test.sh plan
./testing/scripts/test.sh report
```

Outputs a deterministic report under `docs/_docgen/testing/`.

Script usage and verification:
- `./testing/scripts/test.sh plan` writes `docs/_docgen/testing/PLAN.md`.
- `./testing/scripts/test.sh report` writes `docs/_docgen/testing/REPORT.md`.
- Verify by opening the generated file; the script does not run tests.
- Optional: install `rg` for faster file counting (fallback uses `find`).

## References

- `references/README.md` (index of reference material)
- `resources/unit-playbook.md` (unit testing patterns)
- `resources/automation-playbook.md` (E2E/CI strategy patterns)
- `resources/api-testing-mocking-playbook.md` (API tests + deterministic mocking patterns)
- `references/performance-regression.md` (perf budgets + CI gates)
- `references/unit-test-generation.md` (fast unit test checklist)
- `references/tdd-iron-laws.md` (TDD loop + verification discipline)
- `references/testing-anti-patterns.md` (fast test review heuristics)
- `references/test-report-template.md` (consistent findings + sign-off)
- `references/qa-practice-compact.md` (exploratory charters, a11y smoke, risk-based focus)
- `scripts/test.sh` (wrapper)
