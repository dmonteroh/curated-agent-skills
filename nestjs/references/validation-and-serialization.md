# Validation and Serialization (NestJS)

## Validation defaults (strongly recommended)

- Use a global `ValidationPipe` so validation is not optional per route.
- Prefer:
  - `whitelist: true` to strip unknown fields
  - `forbidNonWhitelisted: true` for strict APIs
  - `transform: true` when using DTO transforms

## DTO rules of thumb

- Use DTOs at API boundaries; do not expose internal entities/models.
- Validate inputs strictly; be explicit about optional fields and defaults.
- Keep error payloads stable (do not leak stack traces).

## Serialization

- Use a consistent response DTO shape.
- If using class-transformer patterns, keep them localized and test them.
- Avoid returning raw objects that accidentally expose internal fields.

