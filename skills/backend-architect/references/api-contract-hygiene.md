# API Contract Hygiene (Pragmatic Defaults)

Use this reference when you need concrete rules for APIs that stay stable as teams and codebases evolve.

## Outputs to produce

- Endpoint list + request/response schemas
- Error model (single canonical shape)
- Compatibility rules (what changes are allowed)
- Versioning / deprecation policy (even if “v1 forever”)

## Canonical error shape

Prefer a single error envelope. If you need a standard, consider RFC 9457 “Problem Details”.

Minimum fields to standardize (regardless of exact format):
- stable machine code (for branching)
- human message (for debugging)
- request correlation ID
- per-field validation errors (when relevant)

## Compatibility rules (most important)

Safe-ish changes:
- add optional fields
- add new endpoints
- add new enum values only if clients are tolerant (often they are not)

Breaking changes:
- remove/rename fields
- change meaning/units
- tighten validation
- change pagination semantics

Rule: write down what “compatibility” means for your clients and enforce it in review/CI.

## Pagination, filtering, sorting

- Pick one primary pagination model per API surface.
- Make ordering explicit and stable.
- If you expose cursor-based pagination, document cursor invalidation and sort guarantees.

## Idempotency & retries

- If clients may retry, define idempotency behavior for mutating operations.
- Use request IDs or idempotency keys where appropriate.
- Be explicit about concurrency conflicts (e.g., conditional updates / version checks).

## Source references (authoritative)

```text
HTTP Semantics (RFC 9110):
  https://www.rfc-editor.org/rfc/rfc9110

Problem Details for HTTP APIs (RFC 9457):
  https://www.rfc-editor.org/rfc/rfc9457
```

