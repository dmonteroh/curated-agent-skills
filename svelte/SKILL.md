---
name: svelte
description: "Build Svelte 5 and SvelteKit apps fast: runes/reactivity, component patterns, SvelteKit routing/data flow, forms/actions, SSR boundaries, and production hygiene. Includes optional guidance for TanStack Query and common component libraries."
category: frontend
---

# Svelte

One canonical Svelte skill optimized for fast, correct Svelte 5/SvelteKit delivery.

## Inputs

- Target framework and version (Svelte 5 vs SvelteKit).
- Files, routes, or components in scope.
- Expected behavior and UI states (loading/error/empty).
- Constraints (SSR boundaries, data sources, UI libraries).

## Use this skill when

- Writing or refactoring Svelte 5 components (runes, snippets, directives)
- Working in a SvelteKit app (routing, layouts, load functions, form actions)
- Fixing SSR/hydration issues and data-flow bugs
- Implementing UI patterns with accessibility and good state boundaries

## Do not use this skill when

- The project is React/Next/Angular (use stack-specific skills)
- The task is purely backend or infrastructure work

## Activation cues

- “Svelte 5”, “SvelteKit”, “runes”, “$state”, “$derived”
- “+page.svelte”, “+layout.ts”, “load function”, “form actions”
- “hydration mismatch”, “SSR boundary”, “SvelteKit routing”

## Workflow (Deterministic)

1. Identify the surface.
   - If the change is in `+page.svelte`/`+layout.svelte`, treat it as SvelteKit.
   - If it is a standalone component, treat it as Svelte-only.
   - Output: list the exact files and whether they are Svelte or SvelteKit.
2. Choose reactivity with intent.
   - If mutable state is required, use `$state`.
   - If derived values are required, use `$derived` and avoid side effects.
   - If effects are required, use `$effect` and always return cleanup.
   - Output: the runes used and what each one controls.
3. Define data flow boundaries.
   - If SvelteKit, decide server vs client (+page.server.ts/+layout.server.ts vs client code).
   - Ensure data passed to the client is serializable.
   - For mutations, default to form `actions` with progressive enhancement.
   - Output: a short description of the data path and SSR boundary.
4. Implement UI behavior and states.
   - Provide loading/error/empty states.
   - Preserve keyboard navigation and focus management.
   - Output: a list of UI states and accessibility behaviors addressed.
5. Verify and document behavior.
   - If tests exist, run the smallest relevant set.
   - Otherwise, define a manual repro for the primary flow and one edge case.
   - Output: the verification steps to run.

## Common pitfalls to avoid

- Module-level state that leaks across SSR requests
- Passing non-serializable values over the server/client boundary
- Using `$effect` for derived computation instead of `$derived`
- Mixing legacy event patterns with Svelte 5 runes inconsistently

## Examples

**Input**: “Add a SvelteKit form action that validates email and shows errors.”

**Output**:
- Scope: src/routes/signup/+page.svelte, src/routes/signup/+page.server.ts (SvelteKit)
- Changes: add `actions` handler, client form enhancement, error rendering
- Data flow: form `actions` -> serialized errors -> client UI
- Edge cases: invalid email, server failure
- Verification: submit valid/invalid email, confirm error rendering

**Input**: “Refactor this Svelte 5 component to compute totals reactively.”

**Output**:
- Scope: `CartSummary.svelte` (Svelte)
- Changes: `$derived` total, `$state` for mutable inputs
- Edge cases: empty cart
- Verification: update quantities and observe totals

## Output Contract (Always)

Report in this format:
- Scope:
- Changes:
- Data/state flow:
- Edge cases:
- Verification:

## Trigger test

- “Our `+page.svelte` load is failing serialization; fix the data flow.”
- “Convert this Svelte 4 component to Svelte 5 runes.”

## References (Optional)

- Index and summaries: `references/README.md`
