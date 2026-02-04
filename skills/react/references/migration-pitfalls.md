# Migration Pitfalls

## Stale Closures

**Problem:**
```tsx
useEffect(() => {
  const id = setInterval(() => {
    setCount(count + 1);
  }, 1000);

  return () => clearInterval(id);
}, []);
```

**Fix:**
```tsx
useEffect(() => {
  const id = setInterval(() => {
    setCount(prev => prev + 1);
  }, 1000);

  return () => clearInterval(id);
}, []);
```

## Missing Effect Dependencies

**Problem:**
```tsx
useEffect(() => {
  fetchUser(userId);
}, []);
```

**Fix:**
```tsx
useEffect(() => {
  let cancelled = false;

  async function fetch() {
    const data = await fetchUser(userId);
    if (!cancelled) setUser(data);
  }

  fetch();
  return () => {
    cancelled = true;
  };
}, [userId]);
```

## Over-Memoization

**Problem:**
```tsx
const memoizedTodos = useMemo(() => todos, [todos]);
const handleClick = useCallback(() => console.log('clicked'), []);
```

**Fix:**
```tsx
const completedCount = useMemo(
  () => todos.filter(t => t.completed).length,
  [todos]
);
```

**Rules:**
- Measure before optimizing.
- Memoize expensive calculations only.
- Memoize callbacks passed to memoized children.
