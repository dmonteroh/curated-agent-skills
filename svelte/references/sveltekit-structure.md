# SvelteKit Structure

## Route file types (common)

- `+page.svelte`: page UI
- `+page.ts`: load (client/server)
- `+page.server.ts`: load + actions (server only)
- `+layout.svelte`: layout wrapper
- `+layout.ts` / `+layout.server.ts`: shared load
- `+error.svelte`: error boundary UI
- `+server.ts`: endpoint

## Layout guidance

- Use layouts to share data and UI chrome.
- Keep layout load data minimal; don’t fetch per-page data in the root layout unless it truly applies everywhere.

## Error boundaries

- Prefer local error boundaries close to the failing feature.
- Ensure errors are not swallowed; make recovery paths explicit.

## SSR hygiene

- Avoid mutable module-level state.
- Treat `load` data as request-scoped.
