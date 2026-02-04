# Core Concepts

## Authentication vs Authorization

- **Authentication (AuthN)** verifies identity (passwords, magic links, OAuth, MFA).
- **Authorization (AuthZ)** checks permissions (roles, policies, ownership).

## Auth Strategy Selection

Use these cues to select an auth strategy.

- **Session-based**: server-rendered apps, strict logout control, centralized session revocation.
- **JWT access tokens**: stateless APIs, horizontal scaling, service-to-service calls.
- **OAuth2/OIDC**: external identity providers, social login, enterprise SSO.

## Token and Session Lifecycle

- **Access token**: short-lived, sent on every request.
- **Refresh token**: long-lived, stored securely, rotated on use.
- **Session ID**: opaque server-side session pointer, stored in secure cookies.

## Threat Model Inputs

- Identity risks (credential stuffing, phishing, token theft).
- Data sensitivity (PII, financial, regulated data).
- Attack surfaces (public APIs, admin portals, third-party integrations).
