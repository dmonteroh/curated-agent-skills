# Brainstorming - Implementation Playbook

Use this when you need a deterministic structure for turning an idea into a usable design brief.

## Input Checklist

- Who is the user?
- What is the user trying to accomplish?
- What must be true for this to be considered "done"?
- What is explicitly out of scope?
- What constraints exist (time, tech, compliance, UX, backward compatibility)?
- What is irreversible or high-risk?

## Question Loop (One At A Time)

Ask one question per message. Prefer multiple choice when it makes progress faster.

Examples:

- "Which of these is the primary goal? (A) reduce time-to-complete, (B) reduce errors, (C) increase visibility"
- "Which scope is correct? (A) backend only, (B) frontend only, (C) full stack"
- "What is the failure mode we care about most?"

Stop when you can answer:

- what we’re building
- why now
- where it fits
- what it must not do

## Options Template (2-3)

For each option:

- One-line description
- Pros (2-5 bullets)
- Cons (2-5 bullets)
- Risks (1-3 bullets)
- When to choose it

## Design Brief Template

```md
# Design Brief: <topic>

## Problem

<1 paragraph>

## Goals

- 

## Non-goals

- 

## Users / Personas (optional)

- 

## Constraints

- 

## Proposed Approach

<1-3 paragraphs>

## Considered Options

- Option A:
- Option B:
- Option C (optional):

## Key Flows / States

- 

## Data / Interfaces (if relevant)

- 

## Risks & Mitigations

- 

## Rollout / Migration (if relevant)

- 

## Verification Plan

- 

## Open Questions

- 
```

## Compatibility Notes

- This skill should produce an output that can be pasted into a spec/track/task format if your repo uses one.
- If your repo uses ADRs, extract any architecture decisions into ADR candidates, but do not require ADR creation.
