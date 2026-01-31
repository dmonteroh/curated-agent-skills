# Auth and Security Hygiene (NestJS)

This is a practical checklist, not a full security standard.

## Authentication and authorization

- Authentication in a guard (or middleware that establishes request context).
- Authorization in a guard with clear policy rules.
- Fail closed by default; do not rely on "controller code remembering to check."

## Input and output safety

- Validate all inputs (global ValidationPipe).
- Normalize errors (filters) so internal details do not leak.
- Apply request size limits and timeouts if the service supports it.

## Cross-cutting concerns

- Prefer one centralized place for:
  - security headers (if applicable)
  - CORS policy
  - rate limiting (if used in the project)
  - correlation IDs / request logging

