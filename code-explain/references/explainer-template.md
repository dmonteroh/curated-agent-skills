# Explainer Template

Structured template for a durable “how it works” explanation. Fill in the placeholders.

```md
# <Title>: How It Works

Scope: <what code paths are covered>
Audience: <new devs / on-call / contributors>

## What It Is

<1–3 sentences>

## Key Inputs / Outputs

- Inputs:
- Outputs:
- Primary side effects:

## Control Flow (Step-by-step)

1. ...
2. ...
3. ...

## Data Flow & Invariants

- Data sources:
- Data sinks:
- Invariants (must always hold):

## Edge Cases / Failure Modes

- Case:
  - What happens:
  - Why:

## Where To Change It Safely

- Safe extension points:
- High-risk areas:
- “If you change X, also update Y”:

## Suggested Tests

- Unit:
- Integration:
- E2E (if applicable):

## Quick Glossary

- Term:

## References

- Files:
- ADRs (optional):
- Specs/Tracks (optional):
```
