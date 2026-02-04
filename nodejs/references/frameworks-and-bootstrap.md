# Frameworks and Bootstrap

## Framework selection

- Use Express when you need a minimal, familiar middleware stack.
- Use Fastify when you need higher throughput and schema-driven validation.

## Minimal Express setup

```typescript
import express from 'express';

const app = express();

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

app.get('/health', (_req, res) => {
  res.status(200).json({ status: 'ok' });
});

const port = Number(process.env.PORT) || 3000;
app.listen(port);
```

## Minimal Fastify setup

```typescript
import Fastify from 'fastify';

const app = Fastify({ logger: true });

app.get('/health', async () => ({ status: 'ok' }));

const port = Number(process.env.PORT) || 3000;
await app.listen({ port, host: '0.0.0.0' });
```

## Middleware ordering

1. Security headers and CORS
2. Request parsing (JSON, URL-encoded)
3. Authentication/authorization
4. Validation and route handlers
5. Error handler and response formatter
