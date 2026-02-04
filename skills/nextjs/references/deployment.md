# Deployment & Production

## Vercel (Recommended)

```bash
vercel
vercel --prod
```

## Standalone Output (Self-Hosting)

```js
// next.config.js
const nextConfig = { output: "standalone" }
module.exports = nextConfig
```

```bash
npm run build
node .next/standalone/server.js
```

## Docker (Multi-stage)

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

## Production Checklist

- Enable TypeScript strict mode.
- Optimize images (`next/image`) and fonts (`next/font`).
- Configure security headers.
- Add health checks and error monitoring.
- Use ISR/SSG where possible.
- Verify Core Web Vitals.
