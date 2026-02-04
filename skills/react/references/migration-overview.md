# Class to Modern React Migration Overview

## When to Migrate

- Adopting modern React features (hooks, Suspense)
- Reducing code complexity and improving reuse
- Improving performance or testing ergonomics
- Standardizing a team on hooks-based patterns

## Do Not Migrate When

- The component is an error boundary
- The component is stable with no planned changes
- The team lacks hooks expertise and migration risk is high
- A third-party library requires class inheritance

## Migration Priority

1. New features (write with hooks)
2. Frequently modified components
3. Components with reusable logic
4. Performance bottlenecks
5. Stable, working components (lowest priority)

## Lifecycle to Hooks Map

| Class Component | Modern React Equivalent | Notes |
| --- | --- | --- |
| `constructor` | `useState` initialization | No constructor needed |
| `componentDidMount` | `useEffect(() => {}, [])` | Mount-only effect |
| `componentDidUpdate` | `useEffect(() => {})` | Runs after render |
| `componentWillUnmount` | `useEffect` cleanup | Return cleanup function |
| `shouldComponentUpdate` | `React.memo` | Custom comparator optional |
| `getSnapshotBeforeUpdate` | `useLayoutEffect` | Rarely required |
| `componentDidCatch` | No hook equivalent | Keep class component |
| `this.state` | `useState` / `useReducer` | Split state slices |
| `this.setState` callback | `useEffect` watching state | Separate effect |

## Migration Checklist

**Before Migration:**
- Add tests to current class component
- Document props, state, and behavior
- Identify all lifecycle methods used
- Verify no error boundary requirement

**During Migration:**
- Convert constructor/state to `useState`
- Map lifecycle methods to `useEffect`
- Replace `this.setState` with setters
- Add cleanup functions where needed
- Validate effect dependencies

**After Migration:**
- Confirm all tests pass
- Verify performance is equal or better
- Update TypeScript types
- Update documentation and usage

## Gradual Migration Strategy

- Phase 1: Write new components with hooks
- Phase 2: Migrate leaf components first
- Phase 3: Migrate container components
- Phase 4: Migrate providers and contexts
