# Migration Patterns: Advanced

## Pattern: `shouldComponentUpdate` → `React.memo`

```tsx
const ExpensiveList = React.memo(
  ({ items, filter }: { items: string[]; filter: string }) => {
    const filtered = useMemo(
      () => items.filter(item => item.includes(filter)),
      [items, filter]
    );

    return (
      <ul>
        {filtered.map(item => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    );
  },
  (prev, next) => prev.items === next.items && prev.filter === next.filter
);

ExpensiveList.displayName = 'ExpensiveList';
```

**Notes:**
- Use `React.memo` only when render cost is measurable.
- Use `useMemo`/`useCallback` for expensive or stable props.

---

## Pattern: Refs Migration

```tsx
function FormWithFocus() {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return <input ref={inputRef} />;
}
```

---

## Pattern: HOC → Custom Hook

```tsx
function useAuth() {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const data = await auth.login(email, password);
    setUser(data);
  };

  const logout = () => setUser(null);

  return { user, login, logout };
}

function Profile() {
  const { user, logout } = useAuth();
  if (!user) return null;
  return <button onClick={logout}>Logout {user.name}</button>;
}
```

---

## Pattern: Render Props → Custom Hook

```tsx
function useMouse() {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    function handleMouseMove(e: MouseEvent) {
      setPosition({ x: e.clientX, y: e.clientY });
    }

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return position;
}
```

---

## Pattern: Context Migration

```tsx
type Theme = 'light' | 'dark';

interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = React.createContext<ThemeContextValue | undefined>(
  undefined
);

function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');

  const toggleTheme = useCallback(() => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  }, []);

  const value = useMemo(
    () => ({ theme, toggleTheme }),
    [theme, toggleTheme]
  );

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}
```

**Notes:**
- Memoize context values to prevent re-renders.
- Split contexts by update frequency.
