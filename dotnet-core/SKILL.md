---
name: dotnet-core
description: "Build and review modern .NET (ASP.NET Core / .NET 8+) backend services with DI, auth, data access, and production readiness. Use for implementing or auditing .NET server code and architecture choices."
category: language
---

# .NET Core

Provides guidance for production-grade .NET services with modern patterns and clear verification.

## Use this skill when

- Building or modifying ASP.NET Core services (Minimal APIs or controllers)
- Implementing authentication/authorization, DI, configuration, health checks
- Adding persistence (EF Core or Dapper) or shaping data access boundaries
- Hardening reliability (timeouts, retries, observability hooks)
- Implementing clean architecture/CQRS patterns when the repo already uses them

## Do not use this skill when

- The work is in another language/runtime
- The task only needs generic API design guidance without .NET-specific code changes

## Trigger phrases

- "ASP.NET Core" or ".NET 8 API"
- "Minimal API" or "controller-based API"
- "EF Core migration" or "DbContext"
- "JWT auth" or "Identity in .NET"
- "Dapper query" or "ADO.NET"

## Trigger test

- "Create a .NET 8 Minimal API with JWT auth and EF Core."
- "Review this ASP.NET Core controller for validation and DI issues."

## Required inputs

- Target framework/version and hosting model (Minimal APIs or controllers)
- Authentication/authorization approach and identity provider (if any)
- Data store and access choice (EF Core, Dapper, ADO.NET)
- Existing conventions (solution layout, naming, DI, logging)
- Test framework and verification expectations
- Constraints (no network calls, performance budgets, deployment target)

## Workflow

1. Confirm context and assumptions.
   - Output: summarized assumptions and open questions.
   - Decision: if any required inputs are missing, ask before coding.
2. Define the API surface and contracts.
   - Output: route/endpoint list, request/response DTOs, and status codes.
3. Implement handlers/services with DI and validation at boundaries.
   - Output: code changes with validation rules and error semantics.
4. Add data access patterns.
   - Decision: if EF Core, define DbContext, migrations strategy, and tracking rules; if Dapper/ADO.NET, define connection handling and parameterization.
   - Output: repository/service changes and migration or schema notes.
5. Apply authn/authz and secure defaults.
   - Output: policy/role mapping, token validation, and secrets handling notes.
6. Add production readiness.
   - Output: health checks, logging/metrics hooks, and configuration wiring.
7. Verify behavior.
   - Output: tests added/run or manual verification steps with expected results.

## Common pitfalls to avoid

- Mixing Minimal APIs and controllers without a clear routing strategy
- Leaking EF Core entities directly through API contracts
- Missing async disposal or cancellation tokens in I/O paths
- Skipping validation at the API boundary and relying on database errors
- Hardcoding configuration instead of using options binding

## Examples

**Example request**
"Add a Minimal API endpoint in .NET 8 for creating orders with EF Core and JWT auth. Include validation and tests."

**Example response outline**
- Summary of new `POST /orders` endpoint and validation rules
- Files updated with DTOs, handlers, DbContext changes, and auth policy
- Verification steps (tests run or manual curl examples)

## Output format

- Summary (what changed and why)
- Changes (files touched with key code additions)
- Verification (tests run or manual checks)
- Risks/Open Questions (gaps, missing inputs, or follow-ups)

## References

- See `references/README.md` for focused reference material.
