---
name: ux-interview
description: "Interviews a user about how they work today and produces an interaction spec: required product behaviors traced to observed usage, saved with the transcript that evidences them. Use when a product spec or an interaction design needs grounding in real usage rather than assumption."
metadata:
  category: research
---

# UX Interview

One question per turn, one section at a time, each section closed by a stated saturation condition rather than by a question count. Every requirement that leaves this skill names the moment in the transcript it came from.

## Use this skill when

- A product's interaction design needs grounding in how one or more real people work today.
- The deliverable is a spec of required behavior backed by a transcript, not by assertion.
- Current-state behavior is the unknown, and solution design comes after it.

## Do not use this skill when

- Brand, positioning, identity, or voice is what is undecided. That work sits upstream of interaction design and outside this skill: the interview here assumes what the product stands for is already settled and asks only how a person needs to work with it. Discovering what a product should stand for is a different interview with a different question set and a different artifact.
- The request is brainstorming, feature ideation, or roadmap prioritization with no discovery pass behind it.
- A prototype exists and the request is a scripted task run against it. That measures a design; this describes current behavior.
- Only a short Q&A is wanted, with no written record.

## Required inputs

Confirm all four before deep questioning, and ask for any that is missing before continuing.

- The product, system, or workflow under discussion.
- The interviewee's role relative to it.
- The decision this spec has to support.
- Supporting documents the user supplies (PRD, notes, process docs).

## Workflow

### Step 1: Frame the interview

Read any supplied documents, then state the scope back in one recap: product, role, decision.

Decision points:

- If the scope spans more than one workflow, narrow to a single job-to-be-done and take that one to saturation before opening another.
- If a document conflicts with what the interviewee says, lived experience wins; carry the discrepancy into the output rather than resolving it silently.

### Step 2: Background and usage context

Ask about goals, frequency, and the conditions the work happens under. Capture a concrete instance whenever an answer is abstract.

Output: notes on who this person is relative to the product, and when they reach for it.

### Step 3: Map the task flow

Elicit the end-to-end flow in chronological order, probing transitions, inputs, outputs, and dependencies, then the variants and exceptions.

Output: a step-by-step task map with its branches and workarounds.

Decision points:

- If a step stays vague after one probe, ask for the most recent real occurrence instead of a general description.

### Step 4: Friction and recovery

Ask where time, effort, confusion, or error occurs. Probe severity, frequency, and impact, then capture what the person does to recover.

Output: pain points ordered by observed impact.

### Step 5: Positives and desired change

Ask what works and must survive a redesign, then what they would change. Keep both tied to concrete use.

Output: the behaviors to preserve, and the changes asked for.

### Step 6: Draft the spec and validate it

Turn the findings into interaction requirements: one line each, stated as a behavior the product must support, each carrying the transcript moment behind it. Read the list back, ask what is missing or wrong, and apply the corrections.

Output: the confirmed requirement list.

## Stop criterion

A section closes when two consecutive probes into it return nothing the notes do not already hold — a restatement, a shrug, or a generality where a concrete instance was asked for. Saturation ends a section; running out of prepared questions does not. Two is a chosen default, not a measured one: raise it for an interviewee who is warming up slowly, lower it for one who is visibly done.

The interview closes when every section has either saturated or been explicitly deferred by the interviewee, and the Step 6 requirement list has been read back and confirmed. A deferred section is named in the output as a gap, never dropped quietly.

Close early, and say why, when the interviewee asks to stop, when answers turn speculative rather than experiential ("I guess I'd probably…"), or when the same friction keeps resurfacing in every remaining section — the last means the spec already holds that requirement and the interview is circling.

## Interview rules

- Ask exactly one question per turn.
- Follow a high-value thread to its end before advancing.
- Use neutral wording, with no leading language or implied judgment.
- Prefer what the person did over what they think.
- Reflect understanding back periodically, and always before closing a section.

## Common pitfalls

- Writing a requirement from a stated preference rather than an observed action. Only described behavior becomes a requirement; a preference is recorded as a wish and marked as one.
- Recording a solution the interviewee proposed as if it were the need. Ask what that solution would fix and record *that*; the proposal rides along as a candidate.
- Advancing past a "usually" or a "mostly". Those words name an unmapped branch, and branches are where an interaction spec breaks.

*(Authored: these three replace four pitfalls the file previously stated, each of which repeated a workflow step or an interview rule already above.)*

## Output contract

Save a markdown file in the working directory unless another path is requested, named `YYYY-MM-DD_<short-title>.md`, carrying these sections in this order:

1. `# UX Interview - <product or system>`, followed by `**Date:**`, `**Role:**`, and `**System:**` lines.
2. `## Interaction Requirements` — the spec. One line per required behavior, each tagged `observed` or `wish` and each naming the transcript moment behind it.
3. `## Key Findings`, holding `### Tasks & Workflows`, `### Pain Points`, and `### Positives`.
4. `## Open Questions` — sections the interviewee deferred, and every conflict left unresolved.
5. `## Transcript`, alternating clearly between interviewer and interviewee turns.

## Examples

```markdown
# UX Interview - Expense Reimbursement Portal

**Date:** 2026-02-28
**Role:** Operations manager
**System:** Expense reimbursement portal

## Interaction Requirements

- `observed` Accept several receipts in one upload; today they are attached one at a time after being collected from email. (Transcript: "I uploaded them one by one.")
- `observed` Show why a category was rejected at the point of selection, not after submission. (Transcript: "I find out it was the wrong category a week later.")
- `wish` Suggest a category from the receipt contents. (Transcript: "it would be nice if it just knew.")

## Key Findings

### Tasks & Workflows
- Receipts are gathered from multiple sources before submission starts.

### Pain Points
- Category selection is unclear and causes rework.

### Positives
- Approval status visibility reduces follow-up messages.

## Open Questions

- Month-end batch submission deferred by the interviewee; unmapped branch.

## Transcript

**Interviewer:** Walk me through the last reimbursement you submitted.
**Interviewee:** I started by downloading receipts from email, then uploaded them one by one.
```

## References

- `references/interview-guide.md`: deeper prompts per phase, for a thread that stalls before it saturates. Draw on it to shape a question; never read it out verbatim.
