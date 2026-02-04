# Explainer Pitfalls Checklist

Use this checklist to keep explanations accurate and focused.

## Content quality

- Includes scope, entry points, and dependencies.
- Separates control flow from data flow.
- Lists invariants and failure modes, not just the happy path.
- Calls out safe change points and high-risk areas.

## Clarity risks

- Avoids mixing explanation with implementation changes.
- Avoids ambiguous pronouns (“it”, “this”) without clear referents.
- Avoids overloading with diagrams when a short narrative is clearer.

## Accuracy checks

- Confirms which modules own state and which are pure.
- Confirms where errors are swallowed vs propagated.
- Notes side effects (network calls, persistence, external queues).
