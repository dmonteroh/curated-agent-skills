# React Best Practices (Condensed)

Use this as a fast checklist when implementing or refactoring React code. It focuses on React web (not Next.js server features).

## Rendering and Re-renders

- Compute derived state during render instead of storing it in state.
- Keep effect dependencies narrow and accurate; avoid extra dependencies that trigger re-renders.
- Use `useRef` for transient values that should not trigger re-renders.
- Use functional `setState` when the next state depends on the previous state.
- Lazy-initialize expensive state with `useState(() => initial)`.
- Avoid `useMemo` for simple primitives; use it only for expensive work.
- Move interaction logic into event handlers instead of `useEffect`.

Example: derived state in render

```tsx
function PriceSummary({ items }: { items: Item[] }) {
  const total = items.reduce((sum, item) => sum + item.price, 0);
  return <div>Total: {total}</div>;
}
```

Example: useRef for transient values

```tsx
function SearchInput({ onSearch }: { onSearch: (q: string) => void }) {
  const latestQuery = useRef('');

  useEffect(() => {
    const id = setInterval(() => {
      if (latestQuery.current) onSearch(latestQuery.current);
    }, 500);
    return () => clearInterval(id);
  }, [onSearch]);

  return <input onChange={(e) => (latestQuery.current = e.target.value)} />;
}
```

## Rendering Performance

- Hoist static JSX elements outside render.
- Use explicit conditional rendering; avoid returning `false`/`0` in JSX.
- Use `content-visibility: auto` for long lists when appropriate.
- Prefer `useTransition` for non-urgent updates to keep UI responsive.

Example: hoist static JSX

```tsx
const EmptyState = <div>No results</div>;

function Results({ items }: { items: Item[] }) {
  return items.length === 0 ? EmptyState : <List items={items} />;
}
```

## Client-Side Data and Events

- Deduplicate global event listeners; add them once at module scope or inside a single effect.
- Use passive listeners for scroll/touch when you do not call `preventDefault`.
- Keep localStorage reads minimal and versioned.

Example: passive scroll listener

```tsx
useEffect(() => {
  const onScroll = () => {
    // read-only work
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  return () => window.removeEventListener("scroll", onScroll);
}, []);
```

## Bundling and Code Splitting

- Avoid barrel imports from large libraries; import the specific module.
- Use `React.lazy` + `Suspense` to split heavy components.
- Load large modules only when the feature is activated.

Example: split heavy component

```tsx
const Chart = React.lazy(() => import("./Chart"));

function Dashboard() {
  return (
    <Suspense fallback={<Spinner />}>
      <Chart />
    </Suspense>
  );
}
```

## JavaScript Hot-Path Optimizations

Use only in hot paths or when profiling shows a bottleneck.

- Avoid layout thrashing (batch reads and writes).
- Build `Map`/`Set` for repeated lookups.
- Cache repeated function calls and property access in loops.
- Use `toSorted()` or spread + `sort()` to avoid mutating arrays.

Example: Map for repeated lookups

```tsx
const byId = new Map(users.map((u) => [u.id, u]));
const rows = orders.map((o) => ({ ...o, user: byId.get(o.userId) }));
```
