# TanStack Query (Svelte)

Use TanStack Query for server state (fetching/caching) and mutations with good UX.

## Mutation pattern (Svelte components)

Prefer `createMutation` in `.svelte` to surface loading/error states.

Key convention: pass `onSuccess` / `onError` to `.mutate(variables, callbacks)` so the handler has full local context.

```svelte
<script lang="ts">
  import { createMutation } from '@tanstack/svelte-query';
  import * as rpc from '$lib/query';

  const deleteSession = createMutation(() => rpc.sessions.deleteSession.options);

  let open = $state(false);
</script>

<button
  onclick={() =>
    deleteSession.mutate(
      { sessionId },
      {
        onSuccess: () => {
          open = false;
          toast.success('Session deleted');
        },
        onError: (err) => {
          toast.error(err.title, { description: err.description });
        },
      },
    )}
  disabled={deleteSession.isPending}
>
  {#if deleteSession.isPending}Deleting...{:else}Delete{/if}
</button>
```

## `.execute()` in `.ts` files

When outside component context (load/util files), prefer a direct execute call (pattern depends on the RPC/client layer).
