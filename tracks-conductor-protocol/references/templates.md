# Templates

These templates are optimized for:
- SDD (clear intent, scope, acceptance)
- CDD (explicit links to context artifacts)
- Multi-agent execution (small, linkable artifacts; deterministic indexing)

Default locations are described in `tracks-conductor-protocol/SKILL.md`.

## Intake Draft (To-Do)

Filename: `TD-YYYYMMDD-<short-slug>.md`

```markdown
# <Title>

## Status

Draft | Ready for Review | Accepted | Rejected | Parked

## Problem Statement

2-4 sentences describing user truth + business invariant at risk.

## Intent

1-2 sentences describing desired outcome (no solutioning).

## Scope

In scope:
- ...

Out of scope:
- ...

## Evidence

- <link to observation, bug report, PRD, log, screenshot>

## Dependencies

- ADRs:
  - ADR-XXXX: ...
- Tasks:
  - S##-T-YYYYMMDD-...: ...
- Futures:
  - FUT-XXX: ...

## Risks/Notes

- <only if invariants, security, compliance, or long-term constraints>

## Success Signal

- <one measurable signal (even if rough)>

## Links

- Context (CDD):
  - docs/context/product.md
  - docs/context/tech-stack.md
  - docs/context/workflow.md
```

## Task Brief (SDD)

Filename: `S##-T-YYYYMMDD-<short-slug>.md`

```markdown
# S## - <Title>

## Intent

1-2 sentences: user outcome or system behavior.

## Scope

In scope:
- ...

Out of scope:
- ...

## Dependencies

- Track: <docs/project/tracks/<slug>/>
- ADRs:
  - ADR-XXXX: ...
- Futures:
  - FUT-XXX: ...
- Other tasks:
  - S##-T-YYYYMMDD-...: ...

## Acceptance Criteria

- [ ] ...
- [ ] ...

## Risks/Notes

- <only if it touches invariants, security, or major constraints>

## Links

- Intake draft (if any): <docs/project/to-do/TD-...>
- Context (CDD):
  - docs/context/product.md
  - docs/context/tech-stack.md
  - docs/context/workflow.md
```

## Track Spec

Location: `docs/project/tracks/<track-slug>/spec.md`

```markdown
# Track: <Title>

## Status

Draft | Active | Blocked | Done

## Problem / Context

What are we solving and why now? Link to supporting context and inputs.

## Goals

- ...

## Non-goals

- ...

## Requirements

Must:
- ...

Should:
- ...

Must not:
- ...

## Acceptance Criteria

- [ ] ...

## Dependencies

- ADRs:
  - ADR-XXXX: ...
- Futures:
  - FUT-XXX: ...

## Links

- Context (CDD):
  - docs/context/product.md
  - docs/context/tech-stack.md
  - docs/context/workflow.md
```

## Track Plan

Location: `docs/project/tracks/<track-slug>/plan.md`

```markdown
# Plan: <Track title>

## Phases

### Phase 1: <name>

- [ ] Task: <link to task brief>
- [ ] Verification: <what proves phase is complete>

### Phase 2: <name>

- [ ] ...

## Checkpoints

- Architecture checkpoint: do we need an ADR?
- Context checkpoint: does CDD context need updating?
```

## Track Context (CDD bridge)

Location: `docs/project/tracks/<track-slug>/context.md`

```markdown
# Context: <Track title>

## What this track changes

- ...

## Assumptions

- ...

## Key terms / glossary

- ...

## Open questions

- ...

## Links

- Global context:
  - docs/context/product.md
  - docs/context/tech-stack.md
  - docs/context/workflow.md
- ADRs:
  - ADR-XXXX: ...
```

## CDD Core Context Stubs

Create these in `docs/context/` if missing:

`product.md`:
```markdown
# Product

## One-liner

...

## Users

...

## Goals / Success metrics

...
```

`tech-stack.md`:
```markdown
# Tech Stack

## Languages / frameworks

...

## Data stores

...

## Deployment

...
```

`workflow.md`:
```markdown
# Workflow

## How we work (SDD/CDD)

- Context -> Spec & Plan -> Implement -> Verify

## Quality gates

- Tests, review, verification protocol, indexing updates
```
