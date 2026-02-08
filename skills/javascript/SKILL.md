---
name: javascript
description: "Build and debug modern JavaScript (ES6+) with async patterns and Node.js/browser compatibility when authoring, modernizing, or diagnosing JS."
category: language
---
Provides guidance for modern JavaScript, async programming, and runtime compatibility.

## Use this skill when

- Building modern JavaScript for Node.js or browsers
- Debugging async behavior, event loops, or performance
- Migrating legacy JS to modern ES standards
- The user needs guidance on modules, promises, or async/await

## Do not use this skill when

- The user needs TypeScript architecture guidance
- The work is in a non-JS runtime
- The task requires backend architecture decisions
- The user explicitly requests a different language

## Required inputs

- Target runtime(s): Node.js, browser, or both
- Module system expectations (ESM, CJS, or bundler-managed)
- Performance constraints or compatibility targets
- Testing expectations or tooling constraints (if any)

## Instructions

1. Identify runtime targets and constraints.
   - Output: stated runtime(s), module system, and compatibility targets.
2. Choose async patterns, error boundaries, and module layout.
   - Output: explicit decisions on async flow, imports/exports, and error handling.
3. Implement or modify code with modern JS and JSDoc comments.
   - Output: updated code snippets or files with rationale.
4. Validate behavior and compatibility.
   - Output: verification notes, limitations, and any suggested tests.
5. Report results using the required output format.
   - Output: Summary, Decisions, Changes, Tests, Risks or follow-ups.

## Decision points

- If both Node.js and browser targets are required, choose a shared module format
  and note any conditional exports or build steps needed.
- If legacy browsers are in scope, specify required polyfills or transpilation.
- If async flows are parallelizable, use `Promise.all` and document error handling.

## Focus Areas

- ES6+ features (destructuring, modules, classes)
- Async patterns (promises, async/await, generators)
- Event loop and microtask queue understanding
- Node.js APIs and performance optimization
- Browser APIs and cross-browser compatibility

## Approach

1. Prefer async/await over promise chains
2. Use functional patterns where appropriate
3. Handle errors at appropriate boundaries
4. Avoid callback hell with modern patterns
5. Consider bundle size for browser code
6. Document assumptions and compatibility constraints

## Common pitfalls

- Mixing ESM and CJS without a clear boundary
- Unhandled promise rejections or missing `await`
- Blocking the event loop with sync IO or heavy computation
- Relying on browser-only APIs in Node.js or vice versa

## Examples

**Example prompt**
"Fix this async JavaScript bug causing double requests."

**Example response outline**
- Summary: Identify race condition in `fetchUser`.
- Decisions: Use `AbortController` to cancel inflight requests.
- Changes: Updated `api.js` to share a single pending promise.
- Tests: Suggested async test cases for overlapping calls.

## Output contract

Responses must use this format for every run:

- Summary
- Decisions
- Changes
- Tests (or state "Not run" with reason)
- Risks or follow-ups

Ensure guidance covers Node.js and browser environments when requested.
Include JSDoc comments when adding or modifying functions.

## References

- Index: `references/README.md`
