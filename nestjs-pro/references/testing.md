# Testing (NestJS)

## Two tiers (fast + confidence)

1) Unit tests (providers)
- Test domain/application services as pure logic (no HTTP).
- Mock adapters (DB/HTTP) at the module boundary.

2) E2E tests (routes)
- Boot a Nest app with a testing module.
- Exercise the real HTTP pipeline (guards/pipes/filters/interceptors).
- Include at least:
  - happy path
  - validation failure
  - authz failure (if applicable)

## Reliability rules

- Avoid flakey time-based assertions; use deterministic clocks when possible.
- Ensure error payload shapes are asserted (not just status codes).

