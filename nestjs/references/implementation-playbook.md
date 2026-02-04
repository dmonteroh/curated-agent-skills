# NestJS Pro - Implementation Playbook

Use this when you need a repeatable loop for implementing a feature in a NestJS backend.

## Inputs (must be explicit)

- Endpoint(s) / message handlers affected, with HTTP method + path
- Authn/authz requirements (who can do what)
- Data contract (request/response DTOs) + error cases
- Any cross-cutting concerns (rate limiting, idempotency, audit, tracing) if present in the codebase

## Default Loop

1) Put it in the right module
- Identify the owning domain module.
- If adding a new provider, decide if it is:
  - pure domain service (no framework types)
  - adapter/integration service (talks to DB/HTTP/etc.)

2) DTOs first
- Request DTO: validation rules, transforms, defaults.
- Response DTO: serialization rules (what is intentionally omitted).

3) Route/controller wiring
- Keep controllers thin: bind DTOs, call a provider, return a DTO.
- Avoid leaking ORM models or internal entities across the boundary.

4) Cross-cutting behavior (choose the right mechanism)
- Input: pipes
- Access: guards
- Logging/metrics/response mapping: interceptors
- Error mapping: filters

5) Prove it works
- Unit test provider logic.
- E2E test: the happy path + at least one failure mode.
- Verify OpenAPI output if the project publishes docs.

## Common Footguns

- Providers declared in a module but not exported (or exported too broadly).
- Circular module dependencies (often indicates a bad boundary).
- Missing global ValidationPipe (validation silently not running).
- Returning raw Error/stack details in HTTP responses.
- Inconsistent serialization (e.g., leaking internal fields).
