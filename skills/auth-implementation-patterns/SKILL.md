---
name: auth-implementation-patterns
description: "Provides authentication and authorization implementation patterns (JWT, OAuth2/OIDC, sessions, RBAC) for designing, implementing, or reviewing secure access control in applications and APIs."
metadata:
  category: security
---
# Authentication & Authorization Implementation Patterns

Provides guidance to build secure, scalable authentication and authorization systems using industry-standard patterns and modern best practices.

## Use this skill when

- Implementing user authentication systems
- Securing REST or GraphQL APIs
- Adding OAuth2/social login or SSO
- Designing session management or RBAC
- Debugging authentication or authorization issues

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

1. The skill scopes identities, tenants, and flows, then summarizes assumptions and constraints.
   - Output: Auth scope summary (actors, assets, trust boundaries, constraints).
2. The skill selects an authentication strategy with explicit decision points.
   - If the system is browser-first with server-rendered pages, prioritize session-based auth with secure cookies.
   - If the system is API-first or multi-service, prioritize JWT access tokens with refresh or OAuth2/OIDC.
   - Output: Strategy decision and chosen flow.
3. The skill designs the token/session lifecycle and validation rules.
   - If using tokens, define issuer/audience, expiry, refresh, revocation, and rotation.
   - If using sessions, define session store, idle/absolute timeouts, CSRF defenses, and logout invalidation.
   - Output: Lifecycle and validation checklist.
4. The skill defines the authorization model and enforcement points.
   - If access is role-based, define RBAC roles and permissions matrix.
   - If access is resource- or attribute-based, define ABAC rules and ownership checks.
   - Output: Authorization model and enforcement map.
5. The skill plans credential, secrets, and key management.
   - If keys are used, define rotation, storage, and auditing requirements.
   - Output: Secrets and key management plan.
6. The skill produces a hardening and risk checklist, including pitfalls to avoid.
   - Output: Risk and mitigation checklist.
7. The skill provides an implementation checklist and validation plan.
   - Output: Step-by-step implementation checklist and verification steps.

## Common pitfalls

- Storing tokens in insecure client storage (e.g., localStorage for browser apps).
- Skipping audience/issuer/expiry validation on JWTs.
- Missing rotation or revocation strategy for refresh tokens.
- Ignoring CSRF protection for cookie-based sessions.
- Conflating authentication with authorization checks at boundaries.

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

## Reporting format

- Auth scope summary: actors, assets, trust boundaries, constraints.
- Strategy decision: session or token-based flow + rationale.
- Token/session lifecycle: validation rules, expiry, refresh, revocation.
- Authorization model: RBAC/ABAC rules and enforcement points.
- Secrets/key management: rotation, storage, audit logging.
- Hardening checklist: top risks and mitigations.
- Implementation plan: checklist + verification steps.
- Open questions: unresolved dependencies or decisions.

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

- `resources/implementation-playbook.md` for detailed patterns and examples.
- `references/README.md` for deeper, topic-specific reference material.
