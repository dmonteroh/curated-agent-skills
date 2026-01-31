---
name: brainstorming
description: Clarify ambiguous work through structured brainstorming: ask focused questions, propose 2-3 approaches with tradeoffs, and produce a concise design brief (goals, non-goals, constraints, risks, validation). Use when requirements are unclear or before large/irreversible changes.
---

# Brainstorming Ideas Into Designs

## Overview

Turn fuzzy ideas into a clear, testable design brief via short, structured dialogue.

Default posture: clarify, do not prematurely implement.

## The Process

### 1) Understand the idea (question loop)

- Briefly inspect current project context (relevant docs/files) when available.
- Ask one question at a time; prefer multiple choice when it speeds decisions.
- Clarify: purpose, users, constraints, success criteria, non-goals.

### 2) Explore approaches

- Propose 2-3 approaches with tradeoffs against the stated constraints.
- Make a recommendation, and explain why it wins *for this context*.

### 3) Present the design brief (incremental validation)

- Present a short design brief and ask for confirmation.
- If the user disagrees, return to the question loop and iterate.
- Cover only what matters for decision-making:
  - goals / non-goals
  - scope boundaries
  - main flows and key states
  - risks + mitigations
  - validation (how we know it worked)

## After the Design

### Documentation (optional)

- If the repo has a preferred planning/spec protocol, adapt the brief to that format.
- Otherwise, write a design note to an agreed path (example):

```text
docs/plans/YYYY-MM-DD-<topic>-design.md
```

Do not assume other skills exist; treat any integrations as optional.

### Implementation (optional)

- Ask: "Ready to move from design to execution?"
- If proceeding, produce a small execution plan (milestones + verification).

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense

## Output Contract (Always)

- A 3-7 bullet problem statement and success criteria.
- 2-3 approaches with pros/cons and a recommendation.
- A design brief with explicit non-goals, risks, and a verification plan.

## Resources (Optional)

- `resources/implementation-playbook.md`
