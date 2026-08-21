---
name: brainstorming
description: "Clarify ambiguous work through structured brainstorming: ask focused questions, validate load-bearing premises as falsifiable claims, propose 2-3 approaches with tradeoffs, and produce a design brief (goals, non-goals, constraints, risks, validation) or a time-boxed spike note. Use when requirements are unclear or before large/irreversible changes."
metadata:
  category: workflow
---
# Brainstorming: Ideas → Design Brief

## Use this skill when

- The user’s requirements are ambiguous, conflicting, or incomplete
- The cost of “building the wrong thing” is high (irreversible changes, migrations, public APIs)
- A fast, structured way to compare 2–3 approaches and pick one is needed
- One technical unknown blocks the design and a time-boxed spike must settle it before committing

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

Default posture is to clarify and avoid premature implementation.

## Interview posture

Agreement is not clarification. Take a position on every answer and state what evidence would change that position — that is rigor, not hedging and not false certainty. Challenge the strongest version of the user's claim, never a strawman.

### Phrases to replace

Each hedge on the left is banned while questioning, validating premises, and comparing approaches (steps 1–3 below); use the move on the right instead.

| Never say | Do instead |
| --- | --- |
| "That's an interesting approach" | Take a position on it |
| "There are many ways to think about this" | Pick one and name the evidence that would change it |
| "You might want to consider…" | Say "this is wrong because…" or "this works because…" |
| "That could work" | Say whether it *will* work on the evidence at hand, and name the evidence that is missing |
| "I can see why you'd think that" | If the reasoning is wrong, say it is wrong and why |

### Pushback patterns

Each pair below is the same input answered softly and rigorously. The weak line is the default an unprompted model reaches for; the strong line is the one this skill requires.

**1. Vague scope → force specificity**

- User: "We're building an AI tool for developers."
- Weak: "That's a big space — let's explore what kind of tool."
- Strong: "That space is crowded. Which specific task does a specific developer waste hours on every week that this eliminates? Name the person."

**2. Social proof → demand test**

- User: "Everyone I've talked to loves the idea."
- Weak: "That's encouraging — who specifically have you talked to?"
- Strong: "Liking an idea is free. Has anyone committed budget or time? Has anyone asked when it ships? Has anyone been blocked when a prototype broke? Enthusiasm is not demand."

**3. Platform vision → wedge challenge**

- User: "We need to build the whole platform before anyone can really use it."
- Weak: "What would a stripped-down version look like?"
- Strong: "That's a red flag. If no one can get value from a smaller version, it usually means the value proposition isn't clear yet — not that the thing needs to be bigger. What is the one piece someone would use this week?"

**4. Trend citation → thesis test**

- User: "Everyone is moving to this architecture; the market is growing every year."
- Weak: "That's a strong tailwind — how do you plan to capture it?"
- Strong: "A trend every competitor can cite is not a rationale for this system. What is the specific claim about how *your* users' world changes, and why does that change make this design more essential rather than less?"

**5. Undefined terms → precision demand**

- User: "We want to make onboarding more seamless."
- Weak: "What does your current onboarding flow look like?"
- Strong: "'Seamless' is a feeling, not a feature. Which specific step loses users? What is the drop-off at that step? Has anyone watched a real user go through it?"

### Standing rules

- **Calibrated acknowledgment, not praise.** When an answer is specific and evidence-based, name what was good about it and immediately raise the difficulty — the best reward for a good answer is a harder follow-up. Do not linger on the compliment.
- **Bounded insistence.** When the user pushes to skip the questioning, push back once with a stated reason and then ask only the most decision-critical remaining questions. On a second refusal, comply immediately and move on — do not ask a third time. The budget of one pushback is a chosen default, set so insistence cannot become a loop; it is not a measured figure.
- **A full skip is earned by evidence, not impatience.** Skip the question loop entirely only when the user supplies concrete evidence — existing users, measurements, named customers or constraints. Even then, premise validation (step 2) and the alternatives step (step 3) still run.

## Workflow

### 1) Understand the idea (question loop)

- Inspect current project context (relevant docs/files) when available.
- **Keep discovered facts and business constraints in two separate lists.** The repository is evidence about the system, never about the business: it shows how the code behaves today, its conventions, and its contracts. Business rules, compliance and regulatory obligations, contractual SLAs, pricing, data-retention policy, prioritization, and target users cannot be read from code. A value observed in code — a hardcoded limit, a tier threshold, a retention window — is recorded as an assumption to confirm, never filed as a discovered fact, until the user or an authoritative product artifact (PRD, contract, policy document) states it as a business rule. Inferring "the business rule is X" from "the code currently does X" is the specific error this split prevents.
- Ask one question at a time; prefer multiple choice when it speeds decisions.
- Clarify: purpose, users, constraints, success criteria, non-goals.
- Reframe from the pain described, not the feature requested: probe for specific incidents rather than hypotheticals, then name the larger thing that pain implies and say plainly where it differs from the original framing.
- **Output:** a short problem statement; a `Discovered facts` list, each entry citing the file or command that showed it; a `Business constraints` list, each entry citing who supplied it (or "none supplied yet"); and a list of open questions.

### 2) Validate premises

- State the assumptions the design would rest on as a numbered list of falsifiable claims about the problem or the system — claims that could turn out to be false. Not "does this sound good?".
- Ask the user to **agree, disagree, or adjust** each claim.
- Include, where they apply: what happens if nothing is built; what existing code already solves part of this; and, for a new shippable artifact (binary, library, package, image, app), how users would actually obtain it — an artifact with no distribution channel is one nobody can use.
- Promote every business constraint still carrying an assumption-to-confirm marker into this list, phrased as the claim the user must accept or correct. An unconfirmed business rule that never reaches the premise list becomes a design constraint nobody agreed to.
- Treat every accepted premise as binding: the approaches, the recommendation, and the brief may not quietly assume otherwise. When a premise is later revised, return to step 1 for whatever depended on it.
- **Output:** a numbered premise list carrying the user's verdict on each.

### 3) Explore approaches

- Propose 2-3 approaches with tradeoffs against the stated constraints and the accepted premises.
- Required shapes: one **minimal-viable** option (fewest files, smallest diff, ships first) and one **ideal-architecture** option (best long-term trajectory). A third is optional and should be lateral — a different framing of the problem.
- Give each option: summary, effort, risk, pros, cons, and **reuses** — the existing code, patterns, or infrastructure it leverages.
- Where both human and agent execution are in play, estimate effort in both units. A single unit collapses the difference between them and reads as commensurate when it is not.
- Recommend one and explain why it wins *for this context*.
- **Stop for explicit approval of the approach before any of it lands in the brief.** An option that clearly wins is still a decision the user makes. Writing the recommendation into prose and continuing is the failure this gate exists to prevent.
- **Output:** 2–3 options with pros/cons/risks/reuses, a recommendation, and the user's recorded choice.

### 4) Present the design brief (incremental validation)

- Walk through it section by section, asking for confirmation on each before moving to the next.
- If the user disagrees, return to the question loop and iterate.
- Cover only what matters for decision-making:
  - goals / non-goals
  - scope boundaries
  - discovered facts and business constraints, kept apart and each sourced
  - main flows and key states
  - risks + mitigations
  - validation (how we know it worked)
- Run the brief self-check (below) against the draft before showing the first section. It gates delivery: an item that fails is fixed in the brief, not delivered with a caveat attached.
- **Output:** a design brief that passed the self-check, plus a confirmation request.

### 5) Decide next step

- If the user is ready, ask to move to execution planning.
- If not, continue the question loop.
- **Output:** a single next-step question.

### Decision points

- If constraints make all options invalid, ask which constraint can change.
- If the user rejects the recommendation, return to step 3 with updated criteria.
- If the user wants to implement, move to execution planning.
- If a premise cannot be settled by discussion because it is a technical unknown, run a time-boxed spike (below) and resume at step 2 with its answer.
- If the questioning stops early under the bounded-insistence rule, carry every still-unanswered question into the brief as an explicit open risk.

## Brief self-check

The `Phrases to replace` table governs what the agent *says* while questioning. This governs what the delivered artifact *claims* — a brief can be written in perfectly rigorous dialogue and still assert things no reader could ever check.

Run every item against the draft before showing it, and again after any revision. Any "no" is fixed before delivery.

- [ ] Does every claim the brief makes about behavior name a scenario, an observable result, and how that result gets verified?
- [ ] Is every unfalsifiable qualifier — "correctly", "securely", "fast", "robust", "intuitive", "seamless", "scalable" — either replaced with an observable outcome plus a named verification method, or explicitly marked as a human-judgment call with an owner?
- [ ] Are business constraints listed as supplied or assumed, with none inferred from code?
- [ ] Are non-goals stated explicitly rather than implied by omission?
- [ ] Does every risk carry a mitigation someone could actually execute?

The test behind all five: a reader who was not in the conversation can look at any line and independently judge whether it was met.

**Contrast — a single verification line**

- Fails: "Export works correctly and is secure." No scenario, no observable result, no verification method. Two readers can disagree about whether it shipped.
- Passes: "An authenticated user with at least one visible row clicks Export; the browser downloads a CSV whose columns are `id`, `name`, `created_at`, containing no row belonging to another user. Verified by an integration test plus a manual schema spot-check."
- Also passes: "Onboarding copy reads as approachable rather than clinical — human-judgment call, reviewed by the design owner before release." The qualifier survives because it is marked as judgment and given an owner, not because it was made measurable.

## Time-boxed technical spike

When one unknown blocks the design, the artifact is a spike note, not a design brief. It answers exactly one question, cites the source of its answer, and states what it did not settle.

```md
# Spike: <topic>

Status: complete — <date>
Surfaces: <which open decision this spike settles>
Downstream consumers: <which planned work is blocked on it>

## Question this spike answers

<one question, stated before any investigation content>

## Answer

**<Yes/No/the verdict in one line>.** <The mechanism.> Source: <doc, file, or experiment that establishes it>

## <Finding that could not be reproduced> — UNVERIFIED

**Open question we could NOT settle:** <exactly what could not be forced or observed>
**Experiment that would close it:** <the specific procedure, and what result would promote the finding to verified>

## Open questions

- <unresolved, for the design that consumes this>
```

Two rules carry the weight:

- **Mark what could not be reproduced, in the heading itself.** If a finding could not be forced in the available environment, put `UNVERIFIED` in the section heading — not in prose further down where a reader skimming headings will miss it. State exactly what could not be reproduced, and write down the specific experiment that would close the gap.
- **Ship over an unsettled question only where the unverified piece is inert.** Prefer the option that does nothing when the expected path succeeds, and does nothing if the uncertain path is never exercised at all. Keep the behavior that must be guaranteed at a separate, already-verified layer, so the unverified piece is a bonus rather than the mechanism. Unit-test that option's decision logic against synthetic inputs; do not claim coverage of the integration path that could not be reached.

## After the Design

### Documentation (optional)

- If the repo has a preferred planning/spec protocol, adapts the brief to that format.
- Otherwise, writes a design note to an agreed path (example):

```text
docs/plans/YYYY-MM-DD-<topic>-design.md
```

Does not assume other skills exist; treats any integrations as optional.

### Implementation (optional)

- Asks: "Ready to move from design to execution?"
- If proceeding, produces a small execution plan (milestones + verification).

## Key Principles

- **YAGNI ruthlessly** - Removes unnecessary features from all designs

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
- Premises: (1) drop-off concentrates in the first session, not later — agree/disagree/adjust; (2) support load, not engineering time, is the binding constraint — agree/disagree/adjust.
- Approaches:
  1) Guided walkthrough — minimal viable (pros: fast; cons: brittle; reuses: existing tooltip component)
  2) Goal-based checklist — ideal architecture (pros: flexible; cons: requires UX work; reuses: user-state model)
- Recommendation: checklist, aligns with user diversity. Awaiting explicit approval before writing the brief.
- Design brief: goals, non-goals, constraints, risks, verification.
- Next step: "Want an execution plan next?"

**Contrast — a context entry**

- Fails: `Discovered facts: free-tier users are limited to 100 exports per month.` A per-tier cap is a business rule. The code proves the code enforces that number today, not that the business requires it.
- Passes: `Discovered facts: the export path enforces a per-tier cap read from FREE_TIER_EXPORT_CAP in billing/limits.ts.` plus `Business constraints — to confirm: whether that cap is the intended commercial rule or a leftover default.`

## Output contract

- A 3–7 bullet problem statement + success criteria
- Two separate lists: discovered facts (each citing the file or command that showed it) and business constraints (each citing who supplied it, or marked as an assumption to confirm)
- A numbered premise list with the user's agree/disagree/adjust verdict on each
- 2–3 approaches with pros/cons and a recommendation, including one minimal-viable and one ideal-architecture option
- A design brief with explicit non-goals, risks, and a verification plan, whose every claim is observable-and-verified or marked as a human-judgment call
- A single next-step question
- For a spike instead of a brief: one question, one answer with its source, every unreproduced finding marked `UNVERIFIED` with the experiment that would close it

## Reporting format

```md
## Problem & Success
- ...

## Context
- Discovered facts (technical; each with the file or command it came from):
- Business constraints (supplied by user or product artifact; "none supplied yet" if so):
- Assumptions to confirm (values seen in code that are not yet stated business rules):

## Premises
1. <falsifiable claim> — agreed / adjusted to: ... / rejected
2. ...

## Approaches
1) Option A (minimal viable) — pros/cons/risks/reuses
2) Option B (ideal architecture) — pros/cons/risks/reuses
Recommendation: ...
Approved approach: <recorded user choice>

## Design Brief
- Goals:
- Non-goals:
- Constraints:
- Key flows/states:
- Risks & mitigations:
- Verification plan:
- Self-check: every item passing (anything that failed was fixed, not caveated)

## Next Step
- ...
```

## References

- `references/implementation-playbook.md`

## Scripts

- None. Use instructions only unless the user requests automation.
