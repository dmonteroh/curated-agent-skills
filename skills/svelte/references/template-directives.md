# Template Directives (Svelte 5)

Use directives when integrating with DOM APIs or third-party libraries.

## `{@attach}` (preferred over `use:` actions in Svelte 5)

- Reacts to dependency changes.
- Supports cleanup functions.

```svelte
<script lang="ts">
  function attachZoom(opts: { width: number }) {
    return (el: HTMLElement) => {
      const inst = new ImageZoom(el, opts);
      return () => inst?.destroy?.();
    };
  }
</script>

<figure {@attach attachZoom({ width: 400 })}>
  <img src="photo.jpg" alt="zoom" />
</figure>
```

## `{@render}`

Render a snippet function (slot replacement pattern).

## `{@const}`

Declare a local constant inside a block.

## `{@html}`

Render raw HTML.

- Treat as unsafe input by default.
- Only use with trusted, sanitized sources.
