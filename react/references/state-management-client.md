# Client State Patterns

## Local State (useState)

```tsx
function Counter() {
  const [count, setCount] = useState(0);

  const increment = () => setCount(prev => prev + 1);

  return <button onClick={increment}>{count}</button>;
}
```

## Context for Shared UI State

```tsx
interface ThemeContextValue {
  theme: 'light' | 'dark';
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggle = useCallback(() => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be inside ThemeProvider');
  return context;
}
```

## Zustand (Lightweight Global State)

```tsx
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clear: () => void;
}

const useCartStore = create<CartStore>()(
  persist(
    set => ({
      items: [],
      addItem: item => set(state => ({ items: [...state.items, item] })),
      removeItem: id =>
        set(state => ({ items: state.items.filter(i => i.id !== id) })),
      clear: () => set({ items: [] }),
    }),
    { name: 'cart-storage' }
  )
);
```

## Redux Toolkit (Large Apps)

```tsx
import { createSlice, configureStore } from '@reduxjs/toolkit';
import { Provider, useSelector, useDispatch } from 'react-redux';

const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: {
    increment: state => {
      state.value += 1;
    },
  },
});

const store = configureStore({ reducer: { counter: counterSlice.reducer } });

type RootState = ReturnType<typeof store.getState>;
type AppDispatch = typeof store.dispatch;

const useAppSelector = useSelector.withTypes<RootState>();
const useAppDispatch = useDispatch.withTypes<AppDispatch>();
```

## Jotai (Atomic State)

```tsx
import { atom, useAtom } from 'jotai';
import { atomWithStorage } from 'jotai/utils';

export const userAtom = atom<User | null>(null);
export const isAuthenticatedAtom = atom(get => get(userAtom) !== null);
export const themeAtom = atomWithStorage<'light' | 'dark'>('theme', 'light');

function Profile() {
  const [user] = useAtom(userAtom);
  return <div>{user?.name}</div>;
}
```
