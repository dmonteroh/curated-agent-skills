# State Management Overview

## State Categories

| Type | Description | Typical Solutions |
| --- | --- | --- |
| Local state | Component UI state | `useState`, `useReducer` |
| Shared client state | Cross-component UI state | Context, Zustand, Redux Toolkit, Jotai |
| Server state | Remote data + caching | TanStack Query, SWR, RTK Query |
| URL state | Routes, search params | React Router, custom hooks |
| Form state | Inputs + validation | React Hook Form, Formik |

## Selection Guide

- Small app, simple shared state → Context or Zustand
- Large app, complex workflows → Redux Toolkit
- Heavy server interaction → TanStack Query + light client state
- Highly granular updates → Jotai

## Best Practices

- Colocate state close to where it is used.
- Prefer derived data via selectors, not duplicated state.
- Normalize large collections for predictable updates.
- Keep server state in a cache library, not in UI stores.
- Choose one primary tool per state category.

## Quick Reference

| Solution | Best For |
| --- | --- |
| `useState` | Local component state |
| Context | Theme, auth, simple globals |
| Zustand | Medium complexity, minimal boilerplate |
| Redux Toolkit | Complex state, middleware, devtools |
| Jotai | Atomic, fine-grained updates |
| TanStack Query | Server state, caching |
