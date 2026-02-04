# Svelte Implementation Playbook

Deterministic sequence for implementing or refactoring Svelte/SvelteKit code.

## Inputs

- Svelte version (prefer Svelte 5) and whether this is SvelteKit.
- Target behavior and states (loading/error/empty).
- Where code runs (server vs client) if SvelteKit.

## Default Loop

1) Identify the surface
- Component-only vs route/layout.

2) State and reactivity
- Prefer `$state` and `$derived`.
- Use `$effect` only for side effects; always return cleanup.

3) Data flow (SvelteKit)
- Decide what belongs in `+page.server.ts` / `+layout.server.ts` vs client.
- Ensure data crossing SSR boundaries is serializable.
- For mutations, default to form `actions` + progressive enhancement.

4) UI states
- Provide explicit loading/error/empty states.
- Use `<svelte:boundary>` / error boundaries where appropriate.

5) Accessibility
- Keyboard navigation and focus.
- Semantic markup.

6) Verify
- Run existing tests if present.
- Manual repro: primary flow + at least one error case.

## Common Footguns

- Module-level state leaks across SSR requests.
- Using `$effect` for derived computation.
- Using legacy `on:click` patterns inconsistently in Svelte 5.
- Passing non-serializable values from server to client.
