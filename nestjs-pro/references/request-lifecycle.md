# NestJS Request Lifecycle (Cheat Sheet)

Use this to decide "where does this logic go" without inventing new patterns per endpoint.

## Typical order (mental model)

1) Guards (authn/authz) decide whether the request is allowed.
2) Pipes validate + transform inputs (including parameter parsing).
3) Interceptors wrap execution (logging, metrics, response mapping, timeouts).
4) Controller handler calls providers.
5) Filters map thrown exceptions into a consistent HTTP response shape.

## Where to put logic

- **Authentication** (who are you?): guard (or middleware that sets request context).
- **Authorization** (can you do this?): guard.
- **Input parsing** (UUID, ints, enums): pipes.
- **Business rules** (state transitions): providers (domain service).
- **Response shaping** (hide fields, map domain -> DTO): interceptors or in controller return mapping.
- **Error normalization**: filters.

## Keep it deterministic

- Prefer global defaults (global pipes/filters/interceptors) when consistent across the API.
- Prefer route-scoped overrides only when requirements differ materially.

