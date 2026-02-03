# SvelteKit Server Boundaries (Hooks, Cookies, Locals, Env)

Use this as a quick map of "what runs where" so you do not leak secrets, break SSR, or accidentally rely on browser APIs.

## The rule of thumb

- If it touches secrets/credentials, DB access, privileged APIs, or raw cookies: do it on the server (`+page.server.ts`, `+layout.server.ts`, `hooks.server.ts`).
- If it touches `window`, `document`, WebCrypto, localStorage, or needs user interaction: do it in the browser (client-side component code).
- Any data returned from server `load` to the client must be serializable.

## Hooks: request-scoped glue

`src/hooks.server.ts` is the right place for:

- Authentication/session parsing from cookies/headers
- Setting `event.locals` (request-scoped context for downstream loads/actions)
- Centralized redirects (e.g., enforce login) and security headers
- Per-request correlation IDs / logging context

Avoid:

- Long-running background work
- Global mutable module state (breaks SSR correctness)

## `event.locals` (request context)

- Store request-scoped "who is the user/tenant" and small derived facts.
- Do not put large objects (ORM entities) in locals; re-fetch where needed.
- Treat locals as trusted only if you validated them in the hook.

## Cookies and sessions

- Prefer HttpOnly cookies for session identifiers; do not expose secrets to client JS.
- Mutations that change auth state should update cookies in server actions/endpoints.
- After login/logout, ensure the right invalidation happens (layout-level vs page-level).

## Env vars

- Server-only secrets belong in server env access (never return them to the client).
- Public config can be passed intentionally from server load, or baked via build-time env (depending on the project).
- When in doubt: assume anything imported/used in client code is visible.

## Endpoints vs actions

- Use `+server.ts` endpoints when you need:
  - non-form clients
  - custom methods/headers
  - streaming/binary responses
- Use `actions` in `+page.server.ts` for form-first mutations with progressive enhancement.

## SSR/hydration safety checklist

- No module-level mutable state that varies by request.
- No browser APIs in code that can run on the server.
- No non-serializable values crossing the server->client boundary.

