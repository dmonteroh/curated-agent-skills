# SvelteKit Data Flow

## Load functions

- Use server load for secrets and privileged access.
- Use client load for browser-only behavior.
- Parallelize independent work with `Promise.all`.

## Serialization

- Anything passed from server load to client must be JSON-serializable.
- Convert Dates to ISO strings or structured objects.

## Form actions

- Use `+page.server.ts` actions for mutations.
- Return explicit errors and map them to UX states.

## Auth invalidation

- When auth state changes (login/logout), ensure invalidation/refresh happens consistently.
- Avoid stale UI by reloading/invalidation at the right boundary (layout vs page).
