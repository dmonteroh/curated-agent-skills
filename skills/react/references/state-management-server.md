# Server State Patterns

## TanStack Query (Server State + Caching)

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const userKeys = {
  all: ['users'] as const,
  detail: (id: string) => ['users', 'detail', id] as const,
};

export function useUser(id: string) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => fetchUser(id),
    staleTime: 5 * 60 * 1000,
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateUser,
    onSuccess: user => {
      queryClient.setQueryData(userKeys.detail(user.id), user);
    },
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({ queryKey: userKeys.detail(variables.id) });
    },
  });
}
```

## Server State Tips

- Keep server state in the cache library, not in UI stores.
- Use `queryKey` helpers to keep invalidation consistent.
- Prefer optimistic updates only when rollback is clear.
- Avoid copying server data into local state unless necessary.
