# Modules and DI Boundaries (NestJS)

## Default module design

- One domain module owns its controllers + core providers.
- Export providers only when another module must consume them.
- Prefer dependency on an interface-like token (or a thin adapter) when swapping implementations.

## Provider types (recommended mental split)

- **Domain services**: pure logic; avoid framework types.
- **Application services**: orchestrate use-cases; may depend on adapters.
- **Adapters**: DB/HTTP/queue integrations; isolate vendor specifics.

## Common fixes

- DI error "Nest can't resolve dependencies": confirm provider is listed in `providers` and exported/imported correctly.
- Circular deps: treat as a boundary smell; split shared abstractions into a small module or invert dependency via tokens.

