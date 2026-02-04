# Security Hardening

## Password and Credential Policy

- Enforce strong password requirements and hashing (bcrypt/argon2).
- Block common passwords and reuse.
- Require MFA for privileged roles.

## Rate Limiting and Abuse Controls

- Rate limit login and token endpoints.
- Add account lockout or exponential backoff.

## Logging and Auditing

- Log authentication events without secrets.
- Track failed login attempts, password resets, and privilege changes.

## Secrets Management

- Store secrets in a secure vault or environment variables.
- Rotate signing keys on a schedule or after incidents.

## Common Pitfalls

- Storing JWTs in localStorage for browser apps.
- Skipping token expiry or refresh token rotation.
- Performing authorization only on the client.
- Exposing sensitive error messages in auth flows.
