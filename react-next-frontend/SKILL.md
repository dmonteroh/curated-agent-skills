---
name: react-next-frontend
description: "Build React + Next.js (App Router) frontends: server/client boundaries, data fetching and caching, routing, forms/actions, accessibility, and performance. Not for generic React SPA or React Native."
---

# React + Next Frontend

This skill is for Next.js projects (especially App Router) where Server Components, caching, and server/client boundaries matter.

## Use this skill when

- Building or refactoring React components in a Next.js app
- Working with App Router routing/layouts/loading/error boundaries
- Handling server vs client component boundaries
- Implementing data fetching, caching, revalidation, and streaming/Suspense
- Implementing form actions / server actions (where supported)

## Do not use this skill when

- The project is a plain React SPA or component library (use `react-pro`)
- The project is React Native / Expo (use `react-native-pro`)

## Workflow (Deterministic)

1. Identify which parts must run on the server vs client.
2. Define routing and UI state boundaries (layout vs page vs client component).
3. Choose data fetching strategy and caching/revalidation semantics.
4. Add loading/error boundaries and Suspense where it improves UX.
5. Verify accessibility (keyboard, focus, ARIA) and performance.

## Output Contract (Always)

- Code changes with explicit server/client boundary notes
- Data fetching + caching behavior explanation
- Error/loading state behavior
- Verification steps (dev repro + tests if present)

## References (Optional)

- Server Components patterns: `references/server-components.md`
- React 19 features used in RSC contexts: `references/react-19-features.md`
