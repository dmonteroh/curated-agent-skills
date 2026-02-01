---
name: svelte-pro
description: "Build Svelte 5 and SvelteKit apps fast: runes/reactivity, component patterns, SvelteKit routing/data flow, forms/actions, SSR boundaries, and production hygiene. Includes optional guidance for TanStack Query and common component libraries."
---

# Svelte Pro

One canonical Svelte skill optimized for speed and correct implementation.

## Use this skill when

- Writing or refactoring Svelte 5 components (runes, snippets, directives)
- Working in a SvelteKit app (routing, layouts, load functions, form actions)
- Fixing SSR/hydration issues and data-flow bugs
- Implementing UI patterns with accessibility and good state boundaries

## Do not use this skill when

- The project is React/Next/Angular (use stack-specific skills)

## Workflow (Deterministic)

1. Confirm Svelte vs SvelteKit surface:
   - component-only (library/app) vs SvelteKit route/layout.
2. Choose the right reactive primitive:
   - `$state` for mutable state
   - `$derived` for computed values
   - `$effect` for side effects (cleanup required)
3. Keep state local; push shared state down into self-contained components when possible.
4. For SvelteKit:
   - pick where code runs (server vs client)
   - ensure data is serializable across SSR boundaries
   - use layouts/error boundaries/loading states intentionally
5. Verify behavior:
   - loading/error/empty states
   - keyboard navigation/focus
   - SSR correctness (no request-global state)

## Output Contract (Always)

- The change (component/route) and what state/data flow it relies on
- Edge cases handled (loading/error/empty, SSR)
- Verification steps (how to prove it works)

## Resources (Optional)

- Runes + snippets + common mistakes: `references/runes-and-snippets.md`
- Template directives (`@attach`, `@render`, `@const`, etc.): `references/template-directives.md`
- SvelteKit structure (routes/layouts/errors/SSR): `references/sveltekit-structure.md`
- SvelteKit data flow (load, form actions, serialization): `references/sveltekit-data-flow.md`
- SvelteKit server boundaries (hooks, cookies, locals, env): `references/sveltekit-server-boundaries.md`
- SvelteKit forms/actions (progressive enhancement, fail/redirect, invalidation): `references/sveltekit-forms-actions.md`
- Components + libraries (Bits UI/shadcn-svelte/web components): `references/components-and-libraries.md`
- TanStack Query patterns (mutations, server state): `references/tanstack-query.md`
- Deployment notes (adapters, Vite/pnpm gotchas): `references/deployment.md`
- Implementation playbook: `resources/implementation-playbook.md`
