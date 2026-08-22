# Tutorial Engineer - Implementation Playbook

Provides a reliable tutorial structure, onboarding sequence, or workshop series with quality gates.

## Tutorial Types

Select the smallest format that fits.

- Quickstart: setup + first successful run.
- Guided build: step-by-step feature implementation.
- Deep dive: explains tradeoffs + multiple approaches.
- Workshop series: staged learning objectives + exercises.

## Templates

### Quickstart Template

- Title
- Result overview
- Prerequisites
- Setup
- Run it
- Verify
- Next steps

### Guided Build Template

- Title + goal
- Prereqs
- Architecture sketch (optional)
- Step 1..N
  - Intent
  - Change (files/commands)
  - Verify, with the step's common failure and its fix inline
- Practice exercises
- What you built

## Quality Gates

- Every step has a verification.
- The tutorial has a clean stopping point.
- Errors are anticipated (at least 5 common failures for non-trivial tutorials).
- Commands are safe-by-default (no destructive operations without warning).
