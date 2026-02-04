# Tutorial Engineer - Implementation Playbook

Provides a reliable tutorial structure, onboarding sequence, or workshop series with quality gates.

## Default Output Contract

- A tutorial outline (sections + checkpoints).
- A runnable path (commands/files) or explicit "pseudo" labeling if code isn't runnable.
- A troubleshooting section with the top likely failures.
- A final verification checklist.

## Tutorial Types

Select the smallest format that fits.

- Quickstart: setup + first successful run.
- Guided build: step-by-step feature implementation.
- Deep dive: explains tradeoffs + multiple approaches.
- Workshop series: staged learning objectives + exercises.

## Deterministic Workflow

### 1) Define Audience + Objective

- Audience: newcomer, internal dev, customer, on-call.
- Objective: what they can do at the end (measurable).
- Prereqs: tooling, accounts, baseline knowledge.

### 2) Choose The "Golden Path"

- One canonical path that always works.
- Keep branches optional and clearly marked.

### 3) Create Checkpoints

A checkpoint should be independently verifiable.

- Expected result: X
- Command Y should return output Z
- Endpoint A should return response B

### 4) Write The Tutorial

- Use short sections.
- Provide copy-pasteable commands.
- Explain the *why* only when it changes decisions.

### 5) Add Troubleshooting

- Symptom -> likely cause -> fix.
- Include environment-specific pitfalls.

### 6) Validate

- Do a full run-through when feasible.
- Verify on a clean environment when possible.

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
  - Verify
- Troubleshooting
- Summary

## Quality Gates

- Every step has a verification.
- The tutorial has a clean stopping point.
- Errors are anticipated (at least 5 common failures for non-trivial tutorials).
- Commands are safe-by-default (no destructive operations without warning).
