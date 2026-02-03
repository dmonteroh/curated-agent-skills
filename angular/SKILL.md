---
name: angular
description: Build Angular apps with modern standalone APIs, signals, RxJS, routing, and testing. Focuses on clean component boundaries, predictable state flow, accessibility, and performance. Use for Angular implementation and refactors.
category: frontend
---

# Angular Pro

This skill is for Angular web applications and component libraries.

## Use this skill when

- Building/refactoring Angular components (standalone + signals)
- Choosing state strategy (signals vs RxJS vs NgRx) and keeping it consistent
- Implementing routing, guards/resolvers, lazy loading
- Improving performance (change detection, async pipes, bundle hygiene)
- Writing Angular tests (component + service + integration)

## Do not use this skill when

- The project is not Angular
- You only need general UI design critique (use `ui-design`)

## Workflow (Deterministic)

1) Clarify scope + constraints
- Feature/change scope, target routes/components, accessibility needs, performance budget.

2) Choose state strategy (default order)
- Local component state with signals.
- RxJS for async streams and boundary integration (HTTP, events).
- NgRx only when you truly need global, event-driven app state (large apps, complex workflows).

3) Define component boundaries
- Inputs/outputs and what owns the state.
- Avoid “smart-everywhere”: keep containers thin and components reusable.

4) Implement with Angular hygiene
- Prefer standalone components and `OnPush`.
- Prefer template `async` pipe over manual subscriptions.
- Keep effects/side effects explicit and testable.

5) Routing + data loading
- Keep routing declarative; lazy-load where it matters.
- Ensure error/loading states exist for route-level data.

6) Verify
- Unit tests for services and pure logic.
- Component tests for UI + state interactions.
- One negative case for critical flows (validation/auth/guard).

## Output Contract (Always)

- Component/route changes with rationale
- Notes on state boundaries and data flow
- Accessibility notes (keyboard/focus/labels)
- Verification plan (tests + manual checks)

## References (Optional)

- Components + signals patterns: `references/components.md`
- RxJS patterns: `references/rxjs.md`
- NgRx patterns (only when needed): `references/ngrx.md`
- Routing patterns: `references/routing.md`
- Testing patterns: `references/testing.md`

