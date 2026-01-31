# OpenAPI (NestJS Swagger)

Use this when the service publishes OpenAPI and you want stable, high-quality docs.

## Principles

- Treat OpenAPI as a contract: keep DTOs, status codes, and error shapes correct.
- Document auth requirements per route.
- Ensure examples match real responses (prefer generating from DTOs over hand-written JSON blobs).

## Verification

- Build and inspect the OpenAPI output after changes.
- Add one e2e test that asserts a key contract detail if docs are critical (e.g., required fields, auth behavior).

