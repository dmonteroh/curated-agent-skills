# Backend Security Coding (Pragmatic Checklist)

Use this reference when implementing or reviewing backend code that touches auth, data access, multi-tenancy, API boundaries, or any security-sensitive workflow.

Goal: **make security outcomes explicit** (invariants + tests + safe defaults), not to write a security encyclopedia.

## Outputs to produce

- Security invariants (what must always be true)
- Threats + mitigations (short list)
- Concrete code changes
- Tests proving the security behavior (positive + negative)
- Operational notes (logging/alerts, rate limits, auditability if needed)

## Critical invariants (common)

- Authorization is enforced on every access path (not just “UI hides it”).
- Tenant/organization scoping is applied on every query and mutation (if multi-tenant).
- Mutations are authenticated and authorization-checked before side effects.
- Errors do not leak secrets/PII or internal details (stack traces, SQL).
- Inputs are validated at the boundary; internal layers assume validated inputs.

## API boundary checklist

- Validate:
  - content-type
  - body size limits
  - required fields and formats
  - enum values
  - pagination bounds
- Use allowlists where possible (fields, sort keys, filters).
- Normalize and reject unknown fields when appropriate (prevents “silent ignored input”).

## Authn/Authz checklist

- Authentication:
  - validate token signatures/expiry/audience/issuer
  - rotate keys safely; handle clock skew
- Authorization:
  - define policy in one place (service layer / policy module)
  - enforce on every handler/endpoint
  - add negative tests (forbidden) for each protected capability
- Avoid “role checks sprinkled everywhere”; prefer a single policy function per capability.

## Injection prevention

- Use parameterized queries (always).
- Never string-concatenate user input into SQL.
- Validate and allowlist identifiers (e.g., sort keys) that can’t be parameterized.

## Secrets and sensitive data

- Never log secrets, auth tokens, or raw credentials.
- Treat PII similarly: log minimal, hashed/redacted where feasible.
- Ensure debug endpoints/config are not enabled in production.

## Rate limiting / abuse controls (when relevant)

- Add rate limits to:
  - login / token endpoints
  - password recovery / verification flows
  - expensive search endpoints
- Make limits observable (metrics + logs) and tune via configuration.

## Error handling (safe-by-default)

- Use a canonical error envelope and stable error codes (see `api-contract-hygiene.md`).
- Return generic messages to clients; keep detailed diagnostics in logs.
- Map validation/authz errors to appropriate status codes consistently.

## Minimum test set for security-sensitive changes

- Auth required (401) for unauthenticated requests.
- Forbidden (403) for authenticated but unauthorized actor.
- Cross-tenant access prevented (if relevant).
- Input validation: missing/invalid fields yield expected 4xx and error shape.
- Regression: ensure a previously fixed vulnerability stays fixed.

## Fast review heuristics (things to grep for)

- `SELECT ... WHERE` missing tenant/org scoping
- ad-hoc string building around queries
- endpoints missing auth middleware/policy checks
- logging of request bodies/headers without redaction
- permissive CORS or wildcard origins in production configs

