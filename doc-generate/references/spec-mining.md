# Spec Mining (Reverse-Spec from Code)

This reference provides a repeatable approach to reverse-engineer a baseline spec when requirements are missing or stale.

## Output

One file: `docs/specs/reverse-spec.md` containing:
- Scope and actors.
- Functional requirements in EARS format.
- Non-functional requirements (security, reliability, performance, observability).
- Constraints and invariants.
- Assumptions and open questions.

## Workflow

1) Inventory truth sources (routes, CLI commands, jobs, schema, config, tests).
2) Two-pass reading: architecture first, then behavior and edge cases.
3) Write observable behavior before implementation details.
4) Express behavior using EARS patterns.
5) Distinguish observed vs assumed behavior.

## EARS patterns

- Ubiquitous: `The system SHALL <capability>.`
- Event-driven: `WHEN <trigger> THEN the system SHALL <response>.`
- Unwanted behavior: `IF <condition> THEN the system SHALL <mitigation>.`
- State-driven: `WHILE <state> the system SHALL <response>.`
- Optional feature: `WHERE <feature enabled> the system SHALL <response>.`

## Evidence rules

- Every requirement includes evidence: `path/to/file.ext:line` or `symbolName`.
- If evidence is missing, record an open question instead of guessing.

## Reverse-spec template

```md
# Reverse Spec (Derived from Code)

Generated: YYYY-MM-DD (UTC)
Source: repo scan + code/config/tests

## Scope

- In scope:
- Out of scope:

## Actors & Primary Flows

- Actor:
  - Flow:

## Functional Requirements (EARS)

### Core Behaviors
- OBS-CORE-001: The system SHALL ...
  - Evidence: `path/to/file.ext:123`

### Error Handling
- OBS-ERR-001: IF ... THEN the system SHALL ...
  - Evidence: `path/to/file.ext:123`

## Non-Functional Requirements

- Security:
- Reliability:
- Performance:
- Observability:

## Constraints & Invariants

- Invariant:

## Assumptions

- Assumption (needs confirmation):

## Open Questions / Follow-Ups

- Question:
```
