---
name: nextjs
description: "Build React + Next.js (App Router) frontends: server/client boundaries, data fetching and caching, routing, forms/actions, accessibility, and performance. Not for generic React SPA or React Native."
metadata:
  category: frontend
---
# React + Next Frontend

Provides guidance for Next.js projects (especially App Router) where Server Components, caching, and server/client boundaries matter.

## Use this skill when

- Building or refactoring React components in a Next.js app
- Working with App Router routing/layouts/loading/error boundaries
- Handling server vs client component boundaries
- Implementing data fetching, caching, revalidation, and streaming/Suspense
- Implementing form actions / server actions (where supported)
- The task targets App Router usage (or mixed routing where App Router is in scope)

## Do not use this skill when

- The project is a plain React SPA or component library
- The project is React Native / Expo
- The task is strictly Pages Router-specific
- The task is unrelated to Next.js routing, data fetching, or server/client boundaries

## Required inputs

- Next.js project context and router type (App Router vs Pages Router)
- Feature intent (UI change, data fetching, caching, server action, or routing change)
- Constraints (auth, data source, performance, accessibility)

## Workflow (Deterministic)

1. Confirm this is a Next.js App Router task and restate inputs.
   - Output: router type, scope, and constraints summary.
   - Decision: If not Next.js or not App Router, stop and ask for clarification before proceeding.
2. Identify which parts must run on the server vs client.
   - Output: list of Server Components, Client Components, and server actions/route handlers.
   - Decision: If a component needs hooks/state, mark it `use client` and keep server data access in a parent.
3. Define routing and UI state boundaries (layout vs page vs template vs client component).
   - Output: routing map and boundary notes (which file owns loading/error state).
4. Choose data fetching strategy and caching/revalidation semantics.
   - Output: data source, cache mode, and invalidation/revalidation plan.
   - Decision: If data is user-specific or mutable, prefer `no-store` or tag-based revalidation.
5. Add loading/error boundaries and Suspense where it improves UX.
   - Output: `loading.tsx`/`error.tsx` behavior and any Suspense fallbacks.
6. Verify accessibility (keyboard, focus, ARIA) and performance.
   - Output: a11y/perf checks performed and any fixes applied.

## Common pitfalls

- Calling browser-only APIs in Server Components
- Using React hooks in Server Components without `use client`
- Mixing per-user data with cached fetches
- Missing loading/error boundaries for async routes
- Mutating data without revalidation

## Examples

**Example input**
"Add a form with a server action to create a post and show optimistic UI in the App Router."

**Example output**
- Summary: Added server action and client form component with optimistic state.
- Server/client boundaries: Server action in app/actions.ts, client form in app/posts/PostForm.tsx.
- Data fetching/caching: `revalidateTag('posts')` after create.
- Loading/error: `app/posts/loading.tsx` and `app/posts/error.tsx` updated.
- Verification: `npm test` (if present), manual form submit in dev server.

## Output Contract (Always)

- Code changes with explicit server/client boundary notes
- Router type confirmation and scope summary
- Data fetching + caching behavior explanation
- Error/loading state behavior
- Verification steps (dev repro + tests if present)

## Reporting format

- Summary
- Server/client boundaries
- Data fetching + caching
- Error/loading behavior
- Verification

## References (Optional)

- Index: `references/README.md`

- Server Components patterns: `references/server-components.md`
- React 19 features used in RSC contexts: `references/react-19-features.md`
- App Router patterns: `references/app-router.md`
- Data fetching & caching: `references/data-fetching.md`
- Server Actions: `references/server-actions.md`
- Deployment: `references/deployment.md`
- Best practices: `references/best-practices.md`
