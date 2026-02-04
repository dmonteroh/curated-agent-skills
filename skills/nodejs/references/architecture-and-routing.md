# Architecture and Routing

## Layered structure

```
src/
  controllers/
  services/
  repositories/
  models/
  middleware/
  routes/
  config/
  utils/
```

## Routing guidelines

- Keep routes thin; delegate business logic to services.
- Use explicit versioned paths when APIs evolve (`/v1/orders`).
- Prefer resource-focused naming and consistent HTTP verbs.

## Error handling pattern

```typescript
export type ErrorResponse = {
  status: 'error';
  message: string;
  details?: Record<string, unknown>;
};

export function toErrorResponse(message: string, details?: Record<string, unknown>): ErrorResponse {
  return { status: 'error', message, details };
}
```

## Response format guidelines

- Success responses include `status`, `data`, and optional `message`.
- Error responses include `status`, `message`, and optional `details`.
