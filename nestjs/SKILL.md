---
name: nestjs
description: "Build and evolve NestJS backends fast with correct DI/module boundaries, request lifecycle hygiene (pipes/guards/interceptors/filters), validation + serialization, OpenAPI, and testing. Optimized for spec-driven work: deterministic steps, clear output contracts, and verification gates."
category: backend
---

# NestJS Pro

This skill is NestJS-specific. It does not assume a particular database, ORM, or hosting environment.

## Use this skill when

- Creating or refactoring a NestJS service (modules/providers/controllers)
- Designing request lifecycle behavior (auth, validation, logging, errors)
- Adding endpoints with clean DTOs, OpenAPI docs, and reliable tests
- Debugging dependency injection issues or cross-module coupling

## Do not use this skill when

- The service is not NestJS (use the stack-specific skill instead)
- You only need generic architecture guidance (use backend-architect)

## Workflow (Deterministic)

1) Identify the surface
- New endpoint, cross-cutting behavior (auth/validation/logging), or module refactor.

2) Lock boundaries
- Decide the module that owns the behavior.
- Export only what downstream modules must consume.

3) Define contracts
- DTOs: request/response shapes, validation rules, serialization rules.
- Errors: what can fail, which status codes, and what payload shape.

4) Implement along the Nest request pipeline
- **Pipes**: validate/transform inputs.
- **Guards**: authn/authz + access decisions.
- **Interceptors**: logging/metrics, mapping responses, timeouts.
- **Filters**: exception -> consistent HTTP response.

5) Verify
- Unit tests for providers (pure logic).
- E2E tests for routes (HTTP + Nest wiring).
- One negative test per endpoint (validation/authz/error mapping).

## Output Contract (Always)

- What changed (modules/providers/controllers) and why the boundary is correct
- Request lifecycle behavior (what runs in pipes/guards/interceptors/filters)
- DTO validation/serialization rules
- Verification steps (tests or manual curl + expected status codes)

## References (Optional)

- Modules + DI boundaries: `references/modules-and-di.md`
- Request lifecycle cheat sheet: `references/request-lifecycle.md`
- Validation + serialization: `references/validation-and-serialization.md`
- Auth + security hygiene: `references/auth-and-security.md`
- OpenAPI with Nest Swagger: `references/openapi.md`
- Testing strategy (unit vs e2e): `references/testing.md`
- Implementation playbook: `resources/implementation-playbook.md`
- Read-only project audit script: `scripts/nestjs_audit.sh`

