# Mode Checklists

Use one or more modes based on risk and PR size.

## quality (default)

- Correctness:
  - Off-by-one, nullability, error paths, retries/timeouts
  - Backwards compatibility (API/DB/contracts)
- Maintainability:
  - Complexity hotspots, duplication, naming, cohesion
  - Clear boundaries and ownership
- Tests:
  - Meaningful coverage for changed behavior
  - Edge cases and regression protection
- UX/DX (when applicable):
  - Reasonable defaults, helpful errors, consistent API shapes

## security

- Inputs + validation:
  - Validate/normalize at boundaries
  - Avoid unsafe parsing/eval patterns
- Authn/authz:
  - Check authorization at the right layer
  - No privilege escalation via missing checks
- Secrets:
  - No keys/tokens in code, logs, configs
  - Sensitive data not logged
- Injection risks:
  - SQL/NoSQL injection, command injection, XSS, SSRF
- Dependency/supply chain (when relevant):
  - New dependencies justified
  - Lockfiles updated intentionally

## performance

- Hot paths:
  - Avoid new N+1 queries / unbounded loops
  - Watch allocations and large intermediate data structures
- I/O:
  - Timeouts, batching, backpressure, streaming where appropriate
- Caching:
  - Cache correctness, invalidation, stampede risk
- Observability:
  - Metrics/logging/tracing to detect regressions

## tooling

- CI signals:
  - Tests/lints run and meaningful
  - Static analysis configured (where appropriate)
- Release safety:
  - Migrations and rollback plans
  - Feature flags / progressive rollout when risky
- Docs:
  - Public API changes documented
  - Runbooks updated for operational changes
