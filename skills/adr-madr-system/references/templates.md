# Templates

This skill uses **MADR-style** ADRs stored as individual files (recommended for multi-agent work to reduce merge conflicts).

## Standard MADR Template

```markdown
# ADR-XXXX: <Title>

## Status

Proposed | Accepted | Rejected | Deprecated | Superseded

## Date

YYYY-MM-DD

## Deciders

- @name1
- @name2

## Context

What problem are we solving? Why now? What constraints matter?

## Decision Drivers

Ranked priorities that drive the decision (tie rationale to these):

1. <Driver 1>
2. <Driver 2>
3. <Driver 3>

## Considered Options

### Option A: <Name>

- Pros:
  - ...
- Cons:
  - ...
- Notes:
  - ...

### Option B: <Name>

- Pros:
  - ...
- Cons:
  - ...
- Notes:
  - ...

## Decision

We will <decision>.

## Rationale

Why this option best satisfies the decision drivers (explicitly reference drivers).

## Consequences

- Positive:
  - ...
- Negative:
  - ...
- Risks:
  - ...
- Mitigations:
  - ...

## Follow-ups

- [ ] ...

## Links

- Spec/track/task: <link or path>
- Related ADRs:
  - ADR-XXXX: <Title>
```

## Lightweight ADR Template (still “architectural”)

Use when the decision is real but the tradeoffs are narrow.

```markdown
# ADR-XXXX: <Title>

**Status:** Proposed | Accepted | Rejected | Deprecated | Superseded
**Date:** YYYY-MM-DD
**Deciders:** @name1, @name2

## Context

...

## Decision

...

## Consequences

Good:
- ...

Bad:
- ...

## Links

- Spec/track/task: <link or path>
```

## Supersedes Block

When replacing an accepted ADR, add this to the new ADR (and update the index):

```markdown
## Supersedes

- ADR-XXXX: <Title>
```
