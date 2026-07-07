---
name: ux-interview
description: Runs a structured UX user interview to capture current tasks, workflows, pain points, positives, and desired improvements. Use when the user asks to be interviewed about how they use a product, system, or process.
metadata:
  category: research
---

# UX Interview

Provides a repeatable interview workflow for gathering grounded user research data through one-question-at-a-time conversation and producing a saved transcript with findings.

## Use This Skill When

- The user wants a UX-style interview about real usage of a product, system, or workflow.
- The goal is discovery of current-state behavior, not immediate solution design.
- The interview should produce a reusable written artifact (transcript + findings).

## Do Not Use This Skill When

- The user asks for brainstorming, feature ideation, or roadmap prioritization without a discovery interview.
- The user requests usability testing of a prototype/scripted task flow instead of open interview discovery.
- The user only wants a brief Q&A and not a structured interview record.

## Required Inputs

Collect or confirm before deep questioning:

- Topic/system under discussion.
- Interviewee role relative to that system.
- Interview objective (what decision or understanding this interview should support).
- Optional supporting documents (PRD, notes, process docs) if provided by the user.

If any required input is missing, ask for it before continuing.

## Workflow

### Step 1: Initialize Scope

Actions:

1. Confirm topic/system.
2. Confirm interviewee role.
3. Confirm interview objective.
4. If documents are provided, read them before proceeding.

Output: a short scope recap with topic, role, and objective.

Decision points:

- If scope is broad, narrow to one workflow or job-to-be-done first.
- If documents conflict with interviewee statements, prioritize interviewee lived experience and note the discrepancy.

### Step 2: Gather Background Context

Actions:

1. Ask one question at a time about goals, frequency, and usage context.
2. Use neutral wording.
3. Capture concrete examples when answers are abstract.

Output: 3-6 bullet notes summarizing user context and usage patterns.

### Step 3: Map Tasks and Workflow

Actions:

1. Elicit end-to-end flow in chronological order.
2. Probe transitions between steps, inputs, outputs, and dependencies.
3. Capture common variants and exceptions.

Output: step-by-step task map with notable branches and workarounds.

Decision points:

- If steps remain vague, ask for a recent real example.
- If multiple workflows emerge, finish one complete flow before branching.

### Step 4: Identify Friction and Recovery

Actions:

1. Ask where time, effort, confusion, or errors occur.
2. Probe severity, frequency, and impact.
3. Capture recovery behavior after failure or mistakes.

Output: prioritized pain points with observed impact.

### Step 5: Capture Positives and Desired Improvements

Actions:

1. Ask what currently works well and should be preserved.
2. Ask for desired changes or automation wishes.
3. Keep questions non-leading and tied to concrete use.

Output: list of valued strengths and desired changes.

### Step 6: Close and Validate

Actions:

1. Ask if anything important is missing or incorrect.
2. Provide a concise reflection summary for confirmation.
3. End only after coverage of tasks, pain points, positives, and wishes.

Output: final validation note indicating what the interviewee confirmed or corrected.

## Interview Rules

- Ask exactly one question per turn.
- Follow high-value threads before advancing phases.
- Avoid leading language or implied judgments.
- Prefer specific behavioral evidence over opinions.
- Reflect understanding periodically (about every 3-5 exchanges, or when details are nuanced).

## Common Pitfalls

- Pitfall: Jumping to solution ideas too early.
  - Prevention: Complete current-state discovery first.
- Pitfall: Multi-part questions that reduce answer quality.
  - Prevention: Split into single focused questions.
- Pitfall: Accepting vague statements.
  - Prevention: Ask for a recent concrete example.
- Pitfall: Over-indexing on negatives.
  - Prevention: Always capture positives and must-keep behaviors.

## Reference Usage

Use [references/interview-guide.md](references/interview-guide.md) when:

- A phase needs deeper prompts.
- The interview stalls.
- Additional probing examples are needed.

Do not copy the reference verbatim into output; use it to guide questioning.

## Output Contract

When the interview completes (or the user explicitly stops), the agent must:

1. Save a markdown transcript file in the current working directory unless another path is requested.
2. Use filename format: `YYYY-MM-DD_[short-title-max-50-chars].md`.
3. Include all required sections in this exact order:
   - `# UX Interview - [Topic/System Name]`
   - `**Date:** YYYY-MM-DD`
   - `**Role:** [interviewee role]`
   - `**System:** [system discussed]`
   - `## Transcript`
   - `## Key Findings`
   - `### Tasks & Workflows`
   - `### Pain Points`
   - `### Positives`
   - `### Wishes & Ideas`
4. Ensure transcript alternates clearly between interviewer and interviewee turns.

## Reporting Format During Skill Run

Use this consistent status format when reporting progress:

- `Interview status: setup complete` (after Step 1)
- `Interview status: discovery in progress` (Steps 2-5)
- `Interview status: validation complete` (Step 6)
- `Interview status: transcript saved at <path>` (final)

## Example Output Skeleton

```markdown
# UX Interview - Expense Reimbursement Portal

**Date:** 2026-02-28
**Role:** Operations manager
**System:** Expense reimbursement portal

## Transcript

**Interviewer:** Walk me through the last reimbursement you submitted.
**Interviewee:** I started by downloading receipts from email, then uploaded them one by one.

## Key Findings

### Tasks & Workflows
- Users collect receipts from multiple sources before starting submission.

### Pain Points
- Category selection is unclear and causes rework.

### Positives
- Approval status visibility reduces follow-up messages.

### Wishes & Ideas
- Users want automatic receipt parsing and category suggestions.
```
