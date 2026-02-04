# API Documentation Playbook

## Outcomes

- API surface summary (endpoints, auth, error model).
- Stable reference for consumers (OpenAPI or equivalent).
- Evidence links to code/config/tests for each endpoint.

## Extraction checklist

- Entry points and routers (HTTP handlers, controllers, route tables).
- Authn/authz middleware and tenancy rules.
- Request/response schemas and validation.
- Error types and status mappings.
- Rate limits, pagination, and versioning.

## Minimal OpenAPI outline

```yaml
openapi: 3.0.0
info:
  title: <Service Name>
  version: <Version>
paths:
  /resource:
    get:
      summary: <Purpose>
      responses:
        "200":
          description: <Response>
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
```

## Evidence format

- `path/to/file.ext:line` or `symbolName` for each endpoint or schema.
- If evidence is inferred, label it as an assumption and add a follow-up question.
