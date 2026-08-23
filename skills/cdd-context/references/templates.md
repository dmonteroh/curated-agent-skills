# Templates (Minimal)

These are minimal, safe defaults. If the repo already has conventions, prefer those.

## docs/context/product.md

```markdown
# Product

## One-liner

<what are we building?>

## Users

<who is this for?>

## Problem

<what pain are we solving?>

## Goals / Success metrics

- ...

## Non-goals

- ...

## Open questions

- ...
```

## docs/context/tech-stack.md

```markdown
# Tech Stack

## Overview

<languages, frameworks, infra targets>

## Data stores

- ...

## Architecture notes

- ...

## Constraints

- ...

## Open questions

- ...
```

## docs/context/workflow.md

```markdown
# Workflow

## How we work

- ...

## Quality gates

- code review
- testing
- security checks (as appropriate)

## Release / deploy (if applicable)

- ...

## Open questions

- ...
```

## docs/context/product-guidelines.md (optional)

Add this only when the repo produces user-facing text. It answers "how should this product sound", which none of the three core files owns.

```markdown
# Product Guidelines

## Voice and tone

- <how the product addresses its user, in a few concrete adjectives>
- <what it never does — jargon, exclamation marks, blame, apology loops>

## Terminology

| Preferred term | Avoid | Why |
| --- | --- | --- |
| <term the product uses> | <synonyms that must not appear in user-facing text> | <what the distinction protects> |

## Error messages

Format: <the required shape, e.g. what happened, then what the user can do next>
Example: <one message in that exact shape>

## User-facing copy standards

- <capitalization, punctuation, person, and length rules that apply to labels and buttons>

## Open questions

- ...
```

## docs/context/README.md (index file)

```markdown
# Context

<!-- CONTEXT-INDEX:START -->
| File | Purpose |
| --- | --- |
<!-- CONTEXT-INDEX:END -->
```
