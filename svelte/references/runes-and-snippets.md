# Runes, Reactivity, and Snippets (Svelte 5)

## Which rune?

- `$state(value)`:
  - mutable reactive state
- `$derived(expr)`:
  - computed values
  - prefer `const x = $derived(...)` for read-only
- `$effect(() => { ...; return cleanup })`:
  - side effects only
  - always cleanup subscriptions/timeouts
- `$props()`:
  - typed props destructuring
- `$bindable()`:
  - opt-in to `bind:` for a prop

## Runes rules

- Runes are top-level in the component script.
- Avoid mixing Svelte 4 patterns (stores/slot/event dispatcher) unless the codebase is intentionally hybrid.

## Snippets vs slots

Prefer snippets/`{@render}` for composition in Svelte 5.

```svelte
<script lang="ts">
  let { header, children } = $props();
</script>

{@render header?.()}
{@render children()}
```

## Events

- Prefer `onclick` (Svelte 5 convention) consistently.
- Prefer callback props over event dispatcher for component APIs.

## Common mistakes

- Using `$effect` for derived state (use `$derived`).
- Forgetting cleanup in `$effect`.
- Setting module-level mutable state in SSR apps.
