# Auth Implementation Playbook

This playbook provides deeper implementation guidance for common auth patterns. Expand as needed.

## Pattern Selection
- Session-based auth
- JWT access tokens + refresh tokens
- OAuth2/OIDC (authorization code + PKCE)
- Service-to-service auth

## Secure Defaults
- Short token lifetimes
- Rotation and revocation
- Least-privilege scopes
- Strong password hashing

## Implementation Steps
1. Define threat model and trust boundaries
2. Choose auth flow and token strategy
3. Implement login + logout + refresh paths
4. Enforce authorization (RBAC/ABAC) at boundaries
5. Add audit logging and monitoring

## Validation Checklist
- Token validation and clock skew handling
- CSRF protection where applicable
- Revocation or rotation strategy documented
- No secrets in logs
