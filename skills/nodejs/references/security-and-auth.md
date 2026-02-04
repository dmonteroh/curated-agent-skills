# Security and Authentication

## Authentication options

- JWT: stateless APIs, mobile clients, or service-to-service access.
- Sessions: browser-first apps with server-side session storage.
- API keys: machine-to-machine access with simple rotation.

## Authorization checks

- Enforce role-based access at route or service boundaries.
- Always validate tenant or ownership constraints for multi-tenant apps.

## Validation and sanitization

- Validate all inputs at the edge (request schema or DTO validation).
- Normalize and sanitize user-provided strings before persistence.

## Security hardening checklist

- Enforce request size limits to prevent abuse.
- Use secure defaults for cookies and headers.
- Rate-limit public endpoints with clear error messaging.
- Avoid leaking internal stack traces in error responses.
