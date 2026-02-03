# State Management

## State Categories

| Type | Description | Solutions |
| --- | --- | --- |
| Local State | Component UI state | `useState`, `useReducer` |
| Global Client State | Shared UI state | Zustand, Redux Toolkit, Jotai |
| Server State | Remote data, caching | TanStack Query, SWR, RTK Query |
| URL State | Search params, routes | React Router, `nuqs` |
| Form State | Inputs, validation | React Hook Form, Formik |

## Selection Guide

```
Small app, simple state -> Zustand or Jotai
Large app, complex workflows -> Redux Toolkit
Heavy server interaction -> TanStack Query + light client state
Highly granular updates -> Jotai
```

## Local State (useState)

```tsx
function Counter() {
  const [count, setCount] = useState(0);

  // Functional update for derived state
  const increment = () => setCount((prev) => prev + 1);

  return <button onClick={increment}>{count}</button>;
}
```

## Context for Simple Global State

```tsx
interface ThemeContextValue {
  theme: "light" | "dark";
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  const toggle = useCallback(() => {
    setTheme((t) => (t === "light" ? "dark" : "light"));
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error("useTheme must be inside ThemeProvider");
  return context;
}
```

## Zustand (Recommended for Lightweight Global State)

```tsx
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clear: () => void;
  total: () => number;
}

const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      addItem: (item) =>
        set((state) => ({ items: [...state.items, item] })),
      removeItem: (id) =>
        set((state) => ({
          items: state.items.filter((i) => i.id !== id),
        })),
      clear: () => set({ items: [] }),
      total: () => get().items.reduce((sum, i) => sum + i.price, 0),
    }),
    { name: "cart-storage" },
  ),
);

function Cart() {
  const items = useCartStore((state) => state.items);
  const total = useCartStore((state) => state.total());
  const clear = useCartStore((state) => state.clear);

  return (
    <div>
      {items.map((item) => (
        <CartItem key={item.id} item={item} />
      ))}
      <p>Total: ${total}</p>
      <button onClick={clear}>Clear Cart</button>
    </div>
  );
}
```

## Redux Toolkit (Large Apps)

```tsx
import { createSlice, configureStore, PayloadAction } from "@reduxjs/toolkit";
import { Provider, useSelector, useDispatch } from "react-redux";

const counterSlice = createSlice({
  name: "counter",
  initialState: { value: 0 },
  reducers: {
    increment: (state) => {
      state.value += 1;
    },
    decrement: (state) => {
      state.value -= 1;
    },
    incrementBy: (state, action: PayloadAction<number>) => {
      state.value += action.payload;
    },
  },
});

const store = configureStore({
  reducer: { counter: counterSlice.reducer },
});

type RootState = ReturnType<typeof store.getState>;
type AppDispatch = typeof store.dispatch;

const useAppSelector = useSelector.withTypes<RootState>();
const useAppDispatch = useDispatch.withTypes<AppDispatch>();
```

## Jotai (Atomic State)

```tsx
import { atom, useAtom } from "jotai";
import { atomWithStorage } from "jotai/utils";

export const userAtom = atom<User | null>(null);
export const isAuthenticatedAtom = atom((get) => get(userAtom) !== null);
export const themeAtom = atomWithStorage<"light" | "dark">("theme", "light");

function Profile() {
  const [user] = useAtom(userAtom);
  return <div>{user?.name}</div>;
}
```

## TanStack Query (Server State)

```tsx
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export const userKeys = {
  all: ["users"] as const,
  list: (filters: UserFilters) => ["users", "list", filters] as const,
  detail: (id: string) => ["users", "detail", id] as const,
};

export function useUsers(filters: UserFilters) {
  return useQuery({
    queryKey: userKeys.list(filters),
    queryFn: () => fetchUsers(filters),
    staleTime: 5 * 60 * 1000,
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateUser,
    onMutate: async (newUser) => {
      await queryClient.cancelQueries({
        queryKey: userKeys.detail(newUser.id),
      });
      const previousUser = queryClient.getQueryData(
        userKeys.detail(newUser.id),
      );
      queryClient.setQueryData(userKeys.detail(newUser.id), newUser);
      return { previousUser };
    },
    onError: (_err, _newUser, context) => {
      queryClient.setQueryData(
        userKeys.detail((_newUser as User).id),
        context?.previousUser,
      );
    },
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({
        queryKey: userKeys.detail(variables.id),
      });
    },
  });
}
```

## Best Practices

- Colocate state close to where it is used.
- Use selectors to avoid unnecessary re-renders.
- Normalize data for complex collections.
- Do not duplicate server state in client stores.
- Avoid storing derived data; compute it instead.
- Pick one primary tool per state category.

## Quick Reference

| Solution | Best For |
| --- | --- |
| `useState` | Local component state |
| Context | Theme, auth, simple globals |
| Zustand | Medium complexity, minimal boilerplate |
| Redux Toolkit | Complex state, middleware, devtools |
| Jotai | Atomic, fine-grained updates |
| TanStack Query | Server state, caching |
