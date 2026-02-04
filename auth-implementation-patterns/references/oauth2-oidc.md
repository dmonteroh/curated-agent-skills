# OAuth2 / OpenID Connect

## Integration Checklist

- Identify provider, client ID/secret, redirect URIs.
- Select flow (authorization code with PKCE for browsers).
- Map provider claims to local user identity.
- Handle token refresh or re-authentication.

## Flow Summary (Auth Code + PKCE)

1. Redirect user to IdP authorization endpoint.
2. Receive authorization code on redirect URI.
3. Exchange code for tokens via back-channel call.
4. Validate ID token (issuer, audience, expiry).

## Security Notes

- Store client secrets server-side only.
- Validate state parameter to prevent CSRF.
