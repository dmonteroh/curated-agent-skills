---
name: brainstorming
description: "Clarify ambiguous work through structured brainstorming: ask focused questions, propose 2-3 approaches with tradeoffs, and produce a concise design brief (goals, non-goals, constraints, risks, validation). Use when requirements are unclear or before large/irreversible changes."
category: workflow
---

# Brainstorming: Ideas → Design Brief

## Use this skill when

- The user’s requirements are ambiguous, conflicting, or incomplete
- The cost of “building the wrong thing” is high (irreversible changes, migrations, public APIs)
- A fast, structured way to compare 2–3 approaches and pick one is needed

**Trigger phrases**
- "Not sure what the right approach is"
- "We need to decide between a few options"
- "Let's do a quick design/plan first"
- "Requirements are still fuzzy"

## Do not use this skill when

- The request is already clear enough to plan and implement directly
- The user explicitly requests immediate implementation without upfront design
- The work is tiny/low-risk and a design brief would be overhead

## Required inputs

- The user's current goal or problem statement (even if vague)
- Known constraints (time, scope, tech, risk, compliance)
- Success criteria or definition of done (if known)
- Stakeholders/users and any explicit non-goals (if known)

## Overview

Provides a structured dialogue that turns fuzzy ideas into a clear, testable design brief.

Default posture: clarify, do not prematurely implement.

## Workflow

### 1) Understand the idea (question loop)

- Briefly inspect current project context (relevant docs/files) when available.
- Ask one question at a time; prefer multiple choice when it speeds decisions.
- Clarify: purpose, users, constraints, success criteria, non-goals.
- **Output:** a short problem statement and list of open questions.

### 2) Explore approaches

- Propose 2-3 approaches with tradeoffs against the stated constraints.
- Make a recommendation, and explain why it wins *for this context*.
- **Output:** 2–3 options with pros/cons/risks and a recommendation.

### 3) Present the design brief (incremental validation)

- Present a short design brief and ask for confirmation.
- If the user disagrees, return to the question loop and iterate.
- Cover only what matters for decision-making:
  - goals / non-goals
  - scope boundaries
  - main flows and key states
  - risks + mitigations
  - validation (how we know it worked)
- **Output:** a design brief plus a confirmation request.

### 4) Decide next step

- If the user is ready, ask to move to execution planning.
- If not, continue the question loop.
- **Output:** a single next-step question.

### Decision points

- If constraints make all options invalid, ask which constraint can change.
- If the user rejects the recommendation, return to step 2 with updated criteria.
- If the user wants to implement, move to execution planning.

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

## Common pitfalls

- Skipping constraints and non-goals during questioning
- Listing options without explaining tradeoffs
- Producing a design brief without asking for confirmation
- Moving into implementation without explicit user approval

## Examples

**Input**
"We need to improve onboarding but aren't sure what to build yet. Can you help us pick a direction?"

**Output (abridged)**
- Problem & success: reduce drop-off in first session by 20% without increasing support load.
- Approaches:
  1) Guided walkthrough (pros: fast; cons: brittle)
  2) Goal-based checklist (pros: flexible; cons: requires UX work)
- Recommendation: checklist, aligns with user diversity.
- Design brief: goals, non-goals, constraints, risks, verification.
- Next step: "Want an execution plan next?"

## Trigger test

- "I'm not sure which architecture to choose—can you help me decide?"
- "We need a short design brief before coding; requirements are still fuzzy."

## Output Contract (Always)

- A 3–7 bullet problem statement + success criteria
- 2–3 approaches with pros/cons and a recommendation
- A design brief with explicit non-goals, risks, and a verification plan

## Reporting format

```md
## Problem & Success
- ...

## Approaches
1) Option A — pros/cons/risks
2) Option B — pros/cons/risks
Recommendation: ...

## Design Brief
- Goals:
- Non-goals:
- Constraints:
- Key flows/states:
- Risks & mitigations:
- Verification plan:

## Next Step
- ...
```

## References (Optional)

- `references/implementation-playbook.md`

## Scripts

- None. Use instructions only unless the user requests automation.
