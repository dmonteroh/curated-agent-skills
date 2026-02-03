# Next.js Best Practices (Condensed)

## Server/Client Boundaries

- Default to Server Components.
- Add `"use client"` only for interactivity, state, or browser APIs.
- Fetch data in Server Components and pass to client islands.

## Routing and Layouts

- Use `loading.tsx` and `error.tsx` for every meaningful segment.
- Avoid deeply nested layouts unless necessary.
- Use route groups and parallel routes to control UI composition.

## Data Fetching and Caching

- Prefer cached fetches; opt out with `cache: "no-store"` only when needed.
- Use `revalidate` or tag-based invalidation for semi-dynamic content.
- Use `cache()` to dedupe repeated data access.

## Streaming and UX

- Use Suspense for slow sections, not for critical above-the-fold UI.
- Prefer parallel routes for independent data regions.

## Server Actions

- Validate inputs, check auth, and revalidate after mutations.
- Return error objects for client handling.

## Performance

- Use `next/image` and `next/font`.
- Split heavy client components with dynamic import.
- Avoid barrel imports for large packages unless `optimizePackageImports` is configured.
