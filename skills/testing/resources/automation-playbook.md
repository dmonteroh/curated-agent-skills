# Automation Testing Playbook

Guidance for integration/E2E automation that is fast, reliable, and CI-friendly.

## Principles

- Optimize for fast feedback: small smoke suite + slower full suite.
- Reliability beats coverage: flaky tests destroy trust.
- Prefer contract/integration tests over full UI E2E when possible.

## Test pyramid recommendation

- Unit: many, fast, deterministic.
- Integration/contract: focused on boundaries (HTTP, DB, queues).
- E2E: a small number of critical user journeys.

## Flakiness control

- Stable test data strategy (seed/fixtures; reset between tests).
- Control time/randomness.
- Use explicit waits (avoid arbitrary sleeps).
- Quarantine flaky tests quickly; track trends.

## CI integration

- Parallelize where safe (sharding).
- Collect artifacts (screenshots, traces, logs) on failure.
- Use deterministic environments (containerized where possible).

## Observability in tests

- Log correlation id per test run.
- Capture timings for key steps to detect regressions early.
