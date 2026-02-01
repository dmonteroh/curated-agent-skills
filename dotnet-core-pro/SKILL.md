---
name: dotnet-core-pro
description: "Build modern .NET (ASP.NET Core / .NET 8+) services: Minimal APIs, auth, DI, configuration, background jobs, and production readiness. Includes EF Core patterns and clean architecture/CQRS as optional variants. Use when implementing or reviewing .NET backend code."
---

# .NET Core Pro

This skill focuses on shipping production-grade .NET services with modern patterns.

## Use this skill when

- Building or modifying ASP.NET Core services (Minimal APIs or controllers)
- Implementing auth (JWT/Identity), DI, configuration, health checks
- Adding persistence (EF Core) or shaping data access boundaries
- Hardening reliability (timeouts, retries, observability hooks)
- Implementing clean architecture/CQRS patterns *when they fit the project*

## Do not use this skill when

- You’re working in another language/runtime
- You only need generic API design guidance (use a backend architecture skill)

## Workflow (Deterministic)

1. Confirm runtime and conventions (target framework, auth mode, DB, deployment).
2. Define the API surface (routes, DTOs, error semantics, pagination).
3. Implement with DI + validation at boundaries.
4. Add persistence patterns (EF Core optional) with migration strategy.
5. Add authz policies and secure defaults.
6. Add production readiness: health checks, logging, metrics hooks.
7. Add tests (unit + integration) appropriate for the repo.

## Output Contract (Always)

- Concrete code changes (endpoints/services)
- DTOs/contracts and validation rules
- Security notes (auth/authz, secrets handling)
- Verification steps (tests, local run, expected responses)

## Resources (Optional)

- Minimal APIs: `references/minimal-apis.md`
- Clean architecture/CQRS (optional): `references/clean-architecture.md`
- EF Core patterns: `references/entity-framework.md`
- Auth patterns: `references/authentication.md`
- Cloud-native/containers: `references/cloud-native.md`
