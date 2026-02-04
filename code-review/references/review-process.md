# Review Process

## Phase 1: Context gathering

- Capture the change intent and expected behavior.
- Identify constraints (risk tolerance, compatibility, compliance needs).
- Note runtime context (public vs internal, scale, threat model).

## Phase 2: High-level scan

- Architecture fit: confirm the solution matches existing patterns.
- File organization: check for cohesive placement and ownership.
- Test strategy: confirm coverage for the changed behavior.

## Phase 3: Line-by-line review

- Correctness: edge cases, nullability, error paths, retries/timeouts.
- Security: input validation, authz/authn, secrets exposure.
- Performance: hot paths, query behavior, allocations, batching.
- Reliability: idempotency, concurrency, failure modes.

## Decision points

- If requirements or intent are unclear, add questions before findings.
- If behavior changes without tests, record a test gap.
- If risk is high, request additional validation (tests, monitoring, rollback plan).

## Scope control

- Prefer risk-based sampling when diffs are large.
- Avoid redesigning features outside the diff unless critical.
