# Release Build Optimization

## Multi-stage Docker Build

```dockerfile
FROM node:20 AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
USER node
CMD ["node", "dist/main.js"]
```

Verification: confirm the final image is smaller and runs with a non-root user.

## Parallel Testing (CircleCI)

```yaml
version: 2.1
jobs:
  test:
    parallelism: 4
    docker:
      - image: cimg/node:20
    steps:
      - checkout
      - run: npm ci
      - run: |
          TESTS=$(circleci tests glob "test/**/*.js" | circleci tests split)
          npm test $TESTS
```

Verification: ensure test shards complete and results are aggregated.

## Build Caching Strategy (GitHub Actions)

```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.npm
      ~/.cache
      node_modules
    key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-deps-

- name: Cache Docker layers
  uses: docker/build-push-action@v4
  with:
    context: .
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

Verification: compare build duration before and after cache adoption.

## Parallel CI Pipeline (GitHub Actions)

```yaml
name: Build

on: [push]

jobs:
  test:
    strategy:
      matrix:
        node: [18, 20, 22]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node }}
      - run: npm ci && npm test

  build-images:
    needs: test
    strategy:
      matrix:
        platform: [linux/amd64, linux/arm64]
    runs-on: ubuntu-latest
    steps:
      - uses: docker/build-push-action@v4
        with:
          platforms: ${{ matrix.platform }}
          tags: app:${{ github.sha }}
```

Verification: confirm multi-arch images are produced and tests run on all node versions.
