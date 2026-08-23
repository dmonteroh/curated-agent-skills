---
name: auth-implementation-patterns
description: "Provides authentication and authorization implementation patterns (JWT, OAuth2/OIDC, sessions, RBAC) for designing, implementing, or reviewing secure access control in applications and APIs."
metadata:
  category: security
---
# Authentication & Authorization Implementation Patterns

## Use this skill when

- Implementing user authentication systems
- Securing REST or GraphQL APIs
- Adding OAuth2/social login or SSO
- Designing session management or RBAC
- Debugging authentication or authorization issues
- Exposing a local, already-trusted capability (an agent daemon, dev tool, or CLI) to a remote or third-party caller

## Do not use this skill when

- Only UI copy or login page styling is needed
- The task is infrastructure-only without identity concerns
- Auth policies or credential storage cannot be changed

## Required inputs

- Application type, client platforms, and trust boundaries
- Identity store (users, tenants, service accounts) and data sensitivity
- Compliance or regulatory constraints (if any)
- Existing auth infrastructure, integrations, and migration constraints

## Constraints

- Non-negotiable policies (credential storage, audit, encryption, or data residency)
- Legacy protocols or clients that must remain supported

## Workflow

1. Scope identities, tenants, and flows; summarize assumptions and constraints.
   - Output: Auth scope summary (actors, assets, trust boundaries, constraints).
2. Select an authentication strategy with explicit decision points.
   - If the system is browser-first with server-rendered pages, prioritize session-based auth with secure cookies.
   - If the system is API-first or multi-service, prioritize JWT access tokens with refresh or OAuth2/OIDC.
   - If a local, already-trusted process is being exposed to a remote or third-party caller (the caller may act on untrusted instructions), treat it as a distinct threat model from client-server web auth: separate the surfaces by socket rather than by an authorization check (a private listener with the full command set, a second listener with a locked path allowlist), put a command allowlist on the exposed listener that denies management commands outright, issue a token ladder with descending power and TTL and reject the top of the ladder if it ever arrives on the exposed surface, and grant capability through a small set of named tiers with the highest tier(s) gated behind an explicit action rather than auto-escalated — see `references/remote-capability-exposure.md` for the full pattern.
   - Output: Strategy decision and chosen flow.
3. Design the token/session lifecycle and validation rules.
   - If using tokens, define issuer/audience, expiry, refresh, revocation, and rotation.
   - If using sessions, define session store, idle/absolute timeouts, CSRF defenses, and logout invalidation.
   - Output: Lifecycle and validation checklist.
4. Define the authorization model and enforcement points.
   - If access is role-based, define RBAC roles and permissions matrix.
   - If access is resource- or attribute-based, define ABAC rules and ownership checks.
   - Output: Authorization model and enforcement map.
5. Plan credential, secrets, and key management.
   - If keys are used, define rotation, storage, and auditing requirements.
   - Output: Secrets and key management plan.
6. Produce a hardening and risk checklist, including pitfalls to avoid.
   - Output: Risk and mitigation checklist.
7. Verify the implementation against named checks, each with its expected failure symptom.
   - Token/session validation test: an expired or tampered token or session ID is accepted → fail.
   - Authorization boundary test: a lower-privilege role reaches a higher-privilege route or resource → fail.
   - Secret-exposure scan: a token, session secret, or signing key appears in logs, error output, or version control → fail.
   - Output: Verification checklist naming each check, its method, and its expected failure symptom.

## Common pitfalls

- Storing tokens in insecure client storage (e.g., localStorage for browser apps).
- Skipping audience/issuer/expiry validation on JWTs.
- Missing rotation or revocation strategy for refresh tokens.
- Ignoring CSRF protection for cookie-based sessions.
- Conflating authentication with authorization checks at boundaries.
- Gating a powerful local surface with a single authorization check instead of separating it by transport — a routing bug can bypass a check, but cannot make a caller reach a path that does not exist on the listener it connected to.

## Output contract

The skill produces a concise report with the following sections:

- Auth scope summary
- Strategy decision (session, JWT, OAuth2/OIDC) and flow rationale
- Token/session lifecycle and validation rules
- Authorization model and enforcement points
- Secrets/key management and audit logging plan
- Hardening checklist and top risks
- Implementation checklist and verification steps
- Open questions or dependencies

## Examples

Example input:
- "Design JWT auth and RBAC for a multi-tenant API with mobile and web clients."

Example output summary:
- Auth scope summary: mobile + web clients, tenant-scoped APIs, PII data.
- Strategy decision: JWT access + refresh tokens with short TTLs and rotation.
- Token/session lifecycle: validate iss/aud/exp, rotate refresh, revoke on logout.
- Authorization model: RBAC roles mapped to tenant-scoped permissions.
- Secrets/key management: rotate signing keys on a defined cadence, store in HSM/KMS.
- Hardening checklist: no localStorage tokens, CSRF for cookie flows, rate limits.
- Implementation plan: login, refresh, logout, middleware, automated tests.
- Open questions: token storage constraints on mobile, audit log retention.

## Safety

- Avoid logging secrets, tokens, or credentials.
- Enforce least privilege and secure storage for keys.

## Resources

- `references/README.md` for deeper, topic-specific reference material.
