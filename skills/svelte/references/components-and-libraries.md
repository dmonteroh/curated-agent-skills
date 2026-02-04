# Components and Libraries

## Component boundaries

- Prefer self-contained components over parent state “plumbing”, especially for repeated rows/actions.
- Keep component props small and explicit.

## Props typing (Svelte 5)

Prefer inline typing at `$props()` destructure:

```svelte
<script lang="ts">
  let { title, onClose }: {
    title: string;
    onClose: () => void;
  } = $props();
</script>
```

## Common libraries

- Headless UI: Bits UI, Ark UI, Melt UI (prefer accessible primitives).
- shadcn-svelte: good for composable UI patterns; follow the library’s conventions.
- Web components: Svelte can compile to custom elements when needed.

## Forms

- Prefer native form semantics.
- Use the `form="..."` attribute when markup constraints prevent wrapping inputs.
