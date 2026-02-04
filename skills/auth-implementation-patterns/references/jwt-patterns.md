# JWT Patterns

## JWT Implementation Checklist

- Define token claims (subject, roles, scopes, tenant).
- Sign with a strong secret or asymmetric keys.
- Set `exp`, `iat`, and issuer/audience claims.
- Keep access tokens short-lived (minutes, not days).

## Example (Pseudocode)

```ts
function issueAccessToken(user) {
  return signJwt({ sub: user.id, role: user.role }, SECRET, { expiresIn: '15m' });
}

function verifyAccessToken(token) {
  return verifyJwt(token, SECRET);
}
```

## Refresh Token Flow

1. Issue a refresh token and store a hashed version server-side.
2. Rotate refresh tokens on use (invalidate old token).
3. Revoke refresh tokens on password reset, logout, or compromise.

## Storage Guidance

- Prefer `httpOnly` cookies for browser apps to reduce XSS exposure.
- Never store raw refresh tokens or JWT secrets in logs.
