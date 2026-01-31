# SvelteKit Forms and Actions (Progressive Enhancement)

This is a compact playbook for mutation flows that work with and without JS.

## Preferred default

- UI: `+page.svelte` renders the form and error states.
- Server: `+page.server.ts` implements `actions` for mutations.
- Client: enhance the form so UX is nicer, but keep the server contract as the source of truth.

## Actions: return shapes and control flow

Use three outcomes consistently:

- Success: return a small success payload (or nothing) and show a toast / update UI.
- Validation failure: return a structured error payload (field errors + form error).
- Navigation: redirect after success when that produces simpler state.

Keep payloads serializable and stable (agents should not invent ad-hoc shapes per screen).

## Progressive enhancement (what to optimize for)

- Without JS: form submit should still work and show errors.
- With JS: avoid full-page reload when possible and keep focus management accessible.

## Invalidation and staleness

After a successful mutation:

- Invalidate the minimum boundary that owns the data (page vs layout).
- If auth/session changes, invalidation often needs to happen at the layout boundary.

Avoid "stale derived UI" by relying on server-derived truth (reload/invalidate) instead of only mutating client state.

## Error UX contract (recommended)

Represent errors as:

- `formError`: one message for the whole form (permission, conflict, unknown)
- `fieldErrors`: map of field -> message(s)

Always render:

- a visible summary (formError)
- inline field messages
- focus/aria links for keyboard users

## When to use endpoints instead

Prefer `+server.ts` when:

- request is not a form (API client)
- you need streaming/binary
- you need custom auth/header semantics per call

Otherwise, actions are usually the fastest, safest default for app mutations.

