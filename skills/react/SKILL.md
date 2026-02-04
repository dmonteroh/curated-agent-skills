---
name: react
description: "Build React frontends (SPA/library) with modern hooks, state management, accessibility, and performance. Framework-agnostic: not Next.js-specific and not React Native. Use when implementing React components, client-side routing, data fetching/state, and React testing."
category: frontend
---

# React

Provides guidance for React web apps and component libraries that are not tied to a specific meta-framework.

## Use this skill when

- Building/refactoring React components (hooks, composition)
- Choosing state management (local state, context, Zustand/Redux, query caching)
- Handling forms, validation, error boundaries
- Improving accessibility and performance (memoization, virtualization)
- Writing React tests (RTL/Vitest/Jest)

## Do not use this skill when

- The project is Next.js / App Router / Server Components (use `nextjs`)
- The project is React Native / Expo (use `react-native`)

## Trigger phrases

- "Build a React component" / "refactor React hooks"
- "Add React state management" / "context vs Redux"
- "Fix React performance" / "optimize rendering"
- "Write React tests" / "RTL for components"

## Workflow (Deterministic)

1. Clarify requirements and constraints (a11y, perf budget, responsiveness, browser support).
   - Output: short list of functional + non-functional requirements.
2. Define component boundaries and props/state contracts.
   - Output: component list with props/state table.
3. Choose state strategy.
   - If state is local to a component, keep it local.
   - If shared across sibling branches, use context.
   - If app-wide or complex, use a store (Zustand/Redux).
   - If server state, use query caching (React Query/SWR).
   - Output: selected approach with justification.
4. Implement components with the project's typing conventions and stable keys.
   - If the project uses TypeScript, use explicit prop/state types.
   - If the project uses JavaScript, document prop/state expectations in code or tests.
   - Output: code changes with notes on key patterns.
5. Add error handling (error boundaries for UI failures).
   - Output: error boundary usage and fallback UI notes.
6. Verify with tests and manual checks (keyboard navigation, loading/error states).
   - Output: test plan + any executed checks.

## Common pitfalls to avoid

- Overusing global state for local UI concerns.
- Missing `key` stability in lists, causing render churn.
- Uncontrolled/controlled input mismatch in forms.
- Skipping accessibility checks for focus/ARIA.
- Fetching server state without caching or error handling.

## Examples

**Input**: "Create a reusable `UserCard` component with loading and error states."

**Output**:
- Implemented `UserCard` with props for `user`, `isLoading`, and `error`.
- Added skeleton + error fallback UI and proper aria labels.
- Tests added for loading and error rendering.

## Trigger test

- User prompt: "Refactor this React component to use hooks and add tests."
- User prompt: "We need a shared React context for theme state."

## Output Contract (Always)

- Component/code changes with rationale
- Notes on state boundaries and data flow
- Accessibility notes (keyboard/focus/ARIA)
- Verification plan (tests + how to validate behavior)

## Reporting Format

- Summary
- State decisions
- Accessibility notes
- Verification
