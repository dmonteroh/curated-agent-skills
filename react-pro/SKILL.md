---
name: react-pro
description: Build React frontends (SPA/library) with modern hooks, state management, accessibility, and performance. Framework-agnostic: not Next.js-specific and not React Native. Use when implementing React components, client-side routing, data fetching/state, and React testing.
---

# React Pro

This skill is for React web apps and component libraries that are not tied to a specific meta-framework.

## Use this skill when

- Building/refactoring React components (hooks, composition)
- Choosing state management (local state, context, Zustand/Redux, query caching)
- Handling forms, validation, error boundaries
- Improving accessibility and performance (memoization, virtualization)
- Writing React tests (RTL/Vitest/Jest)

## Do not use this skill when

- The project is Next.js / App Router / Server Components (use `react-next-frontend`)
- The project is React Native / Expo (use `react-native-pro`)

## Workflow (Deterministic)

1. Clarify requirements and constraints (a11y, perf budget, responsiveness, browser support).
2. Define component boundaries and props/state contracts.
3. Choose state strategy:
   - local state first
   - context for cross-cutting UI state
   - a store (Zustand/Redux) only when needed
   - query caching for server state
4. Implement with strict TypeScript types and stable keys.
5. Add error handling (error boundaries for UI failures).
6. Verify with tests and manual checks (keyboard navigation, loading/error states).

## Output Contract (Always)

- Component/code changes with rationale
- Notes on state boundaries and data flow
- Accessibility notes (keyboard/focus/ARIA)
- Verification plan (tests + how to validate behavior)

## References (Optional)

- Hooks patterns: `references/hooks-patterns.md`
- State management: `references/state-management.md`
- Performance: `references/performance.md`
- Testing: `references/testing-react.md`
- Migration (class -> hooks): `references/migration-class-to-modern.md`
