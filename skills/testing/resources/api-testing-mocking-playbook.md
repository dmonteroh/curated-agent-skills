# API Testing + Mocking Playbook (General, Tool-Agnostic)

This playbook avoids requiring a separate “API mocking specialist” skill.

## Principles

- Prefer **real contracts**: generated clients/schemas/OpenAPI types if available.
- Prefer **deterministic** fixtures and scenarios.
- Avoid “mocking the world”: keep mocks close to the boundary (HTTP client, external service adapter).
- If the goal is parallel development, optimize for **stability** and **speed** over perfect fidelity.

## Where to mock (choose the lightest thing that works)

1) In-process mocks (best default)
- Mock the external dependency at the HTTP client boundary.
- Great for unit + integration tests.
- Lowest operational overhead.

2) Test-time HTTP stub server (good for integration tests)
- Start a local stub server during tests.
- Useful when multiple components talk HTTP and realistic request verification is needed.

3) Standalone mock server (only when consumers need it)
- Use when a frontend team or multiple repos need a stable API surface before backend exists.
- Treat it as a product: version it, document scenarios, keep it deterministic.

## What to simulate

Minimum:
- Success responses (happy path)
- Validation errors (400)
- Auth failures (401/403)
- Not found (404)
- Conflict/concurrency (409) if relevant
- Rate limit / transient failures (429/503) if client retry logic matters

Optional, but high-value:
- Latency / jitter (fixed, or seeded randomness)
- Pagination semantics
- Idempotency behavior (same request => same outcome)
- Stateful flows (create -> read -> update -> delete)

## Fixture strategy (high-signal, low pain)

- Store fixtures as files under `testdata/` (or your repo convention).
- Prefer **small** fixtures and composable builders.
- If recording from live environments, scrub secrets/PII and snapshot only what is needed.
- If randomness is required, use a seed and print it on failure.

## Contract confidence (without becoming “contract testing heavy”)

Lightweight checks that pay off:
- Validate responses against JSON Schema/OpenAPI-derived schemas (where feasible).
- Keep a single canonical error shape; test it.
- Add “backwards compatible” checks for client-facing APIs when changing responses.

## Runbook gates (for API test quality)

- For changes touching API contracts:
  - tests exist for new/changed endpoints
  - error shape tests exist
  - auth/policy coverage exists (at least one negative test)
- For external integrations:
  - at least one deterministic stubbed integration test exists
  - timeouts/retries are covered if they exist in production
