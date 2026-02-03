# Svelte Deployment Notes

This file is a compact checklist; exact steps depend on your adapter/runtime.

## Common gotchas

- Ensure the correct adapter is installed/configured.
- pnpm: some setups require `"prepare": "svelte-kit sync"`.
- Confirm Node/Vite/Svelte versions are compatible.

## Adapters (common)

- `@sveltejs/adapter-node` (Node server)
- `@sveltejs/adapter-static` (static)
- `@sveltejs/adapter-cloudflare` (Cloudflare)

## Verification

- `svelte-kit sync` (when applicable)
- build + run server locally
- check SSR pages render and hydration succeeds
