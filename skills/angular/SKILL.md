---
name: angular
description: Build Angular apps with modern standalone APIs, signals, RxJS, routing, and testing. Focuses on clean component boundaries, predictable state flow, accessibility, and performance. Use for Angular implementation and refactors.
category: frontend
---

# Angular Skill

Provides guidance for Angular web applications and component libraries.

## Use this skill when

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
- State boundaries and data sources (HTTP, signals, store)
- Accessibility requirements (keyboard, focus order, labeling)
- Performance constraints (change detection, bundle size)
- Test expectations (unit, component, integration)

## Workflow

1) Clarify scope + constraints
- Capture feature/change scope, target routes/components, accessibility needs, performance budget.
- Outputs: scope summary and acceptance criteria.

2) Choose state strategy (default order)
- If state is local to a component and UI-driven, use signals.
- If state is async or shared via streams/IO boundaries, use RxJS.
- If state must be global, event-driven, and shared across many features, use NgRx.
- Outputs: selected state strategy with rationale and boundaries.

3) Define component boundaries
- Specify inputs/outputs, ownership of state, and what is purely presentational.
- Avoid “smart-everywhere”: keep containers thin and components reusable.
- Outputs: component tree with state owners and data flow.

4) Implement with Angular hygiene
- Prefer standalone components and `OnPush`.
- Prefer template `async` pipe over manual subscriptions.
- Keep effects/side effects explicit and testable.
- Outputs: implementation plan or code changes list.

5) Routing + data loading
- Keep routing declarative; lazy-load where it matters.
- Ensure error/loading states exist for route-level data.
- Outputs: route config updates and loading/error strategy.

6) Verify
- Unit tests for services and pure logic.
- Component tests for UI + state interactions.
- One negative case for critical flows (validation/auth/guard).
- Outputs: verification checklist with exact test targets.

## Common pitfalls to avoid

- Mixing signals and RxJS without clear ownership boundaries
- Manual subscriptions in templates instead of `async` pipe
- Shared mutable state in components that should be inputs/outputs
- Missing loading/error states for route-level data
- Unmocked dependencies in component tests

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

Reporting format:
- Scope:
- State strategy:
- Changes:
- Data flow boundaries:
- Accessibility checks:
- Verification:
