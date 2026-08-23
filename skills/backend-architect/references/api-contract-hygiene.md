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

### Retiring a version or a field

A compatibility policy with no retirement mechanism keeps every version alive forever. Retire in three visible stages:

1. **Announce** to the consumers recorded for that boundary: what is going away, what replaces it, and the date it stops working. The notice period is a policy choice sized from how fast those consumers can actually move — not a portable constant. Write the chosen period into the policy so it is the same for the next deprecation.
2. **Signal it on the wire.** Send a `Sunset` response header carrying the retirement date on every response from the deprecated surface, so a consumer that never read the announcement still gets a machine-readable warning in traffic it is already receiving. A deprecation that exists only in documentation is invisible to the client that most needs it.
3. **Return `410 Gone` after the date, not `404`.** `404` says the resource may never have existed and sends the consumer looking for a bug on its own side; `410` says it existed and was withdrawn, which is the fact that resolves the call.

Cap how many versions are supported concurrently and state the cap — current plus one previous is a workable chosen default, not a measured one. An uncapped set is a permanent maintenance surface that no single change is ever responsible for.

## Pagination, filtering, sorting

- Pick one primary pagination model per API surface.
- Make ordering explicit and stable.
- If you expose cursor-based pagination, document cursor invalidation and sort guarantees.
- Choose the model from the consumer's access pattern, not from implementation convenience:
  - **Offset** where the consumer expects page numbers or has to jump to an arbitrary page — admin tables, search results.
  - **Cursor** where the list is unbounded or is written to while it is read — feeds, infinite scroll, export jobs. Offset paging over a list that is being mutated concurrently silently skips and repeats rows across page boundaries, which makes this a correctness property first and a performance one second.

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

