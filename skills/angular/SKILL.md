---
name: angular
description: Guides Angular implementation and refactors using standalone APIs, signals, RxJS, routing, and testing. Focuses on clean component boundaries, predictable state flow, accessibility, and performance. Use when work is Angular-specific.
category: frontend
---

# Angular Skill

Provides guidance for Angular web applications and component libraries.

## Use this skill when

Use this skill when Angular-specific architecture or implementation choices are required.

- Building/refactoring Angular components (standalone + signals)
- Choosing state strategy (signals vs RxJS vs NgRx) and keeping it consistent
- Implementing routing, guards/resolvers, lazy loading
- Improving performance (change detection, async pipes, bundle hygiene)
- Writing Angular tests (component + service + integration)

## Do not use this skill when

- The project is not Angular
- You only need general UI design critique
- The request is framework-agnostic frontend guidance

## Activation cues

- "Build an Angular component" / "refactor an Angular component"
- "Use signals" / "RxJS vs signals" / "NgRx store"
- "Angular routing" / "guard" / "resolver" / "lazy load"
- "Angular tests" / "TestBed" / "Component harness"

## Inputs to collect

- Target components/routes/services and current pain points
- Angular version and architectural constraints (standalone vs NgModule)
- State boundaries and data sources (HTTP, signals, store)
- Accessibility requirements (keyboard, focus order, labeling)
- Performance constraints (change detection, bundle size)
- Test expectations (unit, component, integration) and available tooling

## Workflow

1) Clarify scope + constraints
- Capture feature/change scope, target routes/components, accessibility needs, performance budget.
- Record architecture constraints (NgModule vs standalone) and dependency constraints.
- Outputs: scope summary and acceptance criteria.

2) Choose state strategy (default order)
- If state is local to a component and UI-driven, use signals.
- If signals are unavailable in the target Angular version, use RxJS or existing state patterns.
- If state is async or shared via streams/IO boundaries, use RxJS.
- If state must be global, event-driven, and shared across many features, use NgRx.
- If the codebase already standardizes on one approach, follow it and document the constraint.
- Outputs: selected state strategy with rationale and boundaries.

3) Define component boundaries
- Specify inputs/outputs, ownership of state, and what is purely presentational.
- Avoid “smart-everywhere”: keep containers thin and components reusable.
- Outputs: component tree with state owners and data flow.

4) Implement with Angular hygiene
- Prefer standalone components and `OnPush`.
- If the codebase is NgModule-based or forbids standalone, follow existing patterns and note the constraint.
- Prefer template `async` pipe over manual subscriptions.
- Keep effects/side effects explicit and testable.
- Outputs: implementation plan or code changes list, plus risk notes.

5) Routing + data loading
- Keep routing declarative; if a route is rarely used or heavy, lazy-load it.
- If route data is required before render, use resolvers or route-level effects; otherwise load on init with loading state.
- Ensure error/loading states exist for route-level data.
- Outputs: route config updates and loading/error strategy.

6) Verify
- Unit tests for services and pure logic.
- Component tests for UI + state interactions.
- One negative case for critical flows (validation/auth/guard).
- If tests are out of scope, provide a manual verification checklist.
- Outputs: verification checklist with exact test targets.

## Common pitfalls to avoid

- Mixing signals and RxJS without clear ownership boundaries
- Manual subscriptions in templates instead of `async` pipe
- Shared mutable state in components that should be inputs/outputs
- Missing loading/error states for route-level data
- Unmocked dependencies in component tests
- `OnPush` with mutable data leading to stale UI

## Examples

Trigger tests:
- "Refactor this Angular page to use signals and OnPush."
- "Add lazy-loaded routes with guards and tests for a new feature."

Example input:
- "We need a standalone Angular profile page with signals, routing, and tests."

Example output (condensed):
- Scope: Profile page and edit dialog
- State strategy: Signals for local form state, RxJS for HTTP
- Changes: `ProfileComponent`, `ProfileService`, `profile.routes.ts`
- Tests: `ProfileService` unit tests, component harness tests

## Output Contract (Always)

- Component/route changes with rationale
- Notes on state boundaries and data flow
- Accessibility notes (keyboard/focus/labels)
- Verification plan (tests + manual checks)
- Constraints or assumptions that affected the approach

Reporting format:
- Scope:
- Constraints/assumptions:
- State strategy:
- Changes:
- Data flow boundaries:
- Accessibility checks:
- Verification:
