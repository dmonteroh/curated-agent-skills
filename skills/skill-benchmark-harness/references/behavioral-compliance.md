# Behavioral compliance: strictness levels and trace assertions

For runs where the graded property is what the agent *did* — which steps it took, in what order — rather than what a deliverable contains. Everything in the paired design holds unchanged: two arms, blinding, a recorded configuration, repeats, the id join, a recomputed rollup. This file adds three things that design does not otherwise carry — a prompt ladder that varies how much support the request gives the skill, an assertion class graded against the run's trace, and the one reporting rule that keeps the levels from being averaged into a number that means nothing.

Sourced from a third-party compliance-measurement tool read during intake. Its ladder and its trace assertions transfer; its scoring does not — see the last section.

## The strictness ladder

One task, held constant, asked three ways. Three levels is a chosen ladder, not a measured optimum; the ordering is the point.

| Level | The prompt | What the result means |
| --- | --- | --- |
| Supportive | Names the skill or its procedure outright — "use the review checklist to…" | Whether the agent can follow it when told to. A failure here is a defect in the skill's content, not in its activation. |
| Neutral | The same task described normally, with no mention of the skill | Whether the skill fires unprompted. This is the level any activation claim actually rests on. |
| Competing | The same task plus an instruction that cuts against the skill — "just get it working, skip the ceremony" | Whether the skill survives a conflicting instruction, or correctly yields to it. |

- Each level is its own eval id and runs in **both** arms, like any other eval. The ladder multiplies evals, never arms.
- Hold the task fixed across the three and change only the framing. The moment the underlying task differs, the levels are not comparable and the curve carries nothing.
- Strictness and register are separate axes. An off-register prompt — terse, lowercase, an issue reference and little else — tests whether a badly formed request still triggers the skill; the ladder tests how much support the request gives it. A prompt can be off-register and supportive at once, and a suite needs both axes covered rather than one standing in for the other.

## Trace assertions

A trace assertion names a behavioral step the run should contain and is graded against the harness's machine-readable record of the calls the agent made, not against an output document. Per step:

- `id` — stable, and what the grading record stores. Same rule as an artifact assertion: never the description text.
- `description` — what the step *means*, in one sentence. Classification matches meaning, not tool names: "reads the failing test before editing source" survives a renamed tool, a match on a literal tool name does not.
- `required` — whether its absence is a failure or an observation. A step marked neither way is a step nobody decided about, and it will be counted inconsistently.
- ordering constraints — optional, naming another step this one must fall after, or before.

Grading runs in two passes, in this order:

1. **Classify.** Map each trace event to the step it satisfies, if any. This is grading, so it inherits the blinding, evidence-quotation, and id-not-text rules in step 6 of the procedure. Where a model does the classifying, establish its agreement with hand-labelled events before its output counts toward any number — a classifier nobody checked is an ungraded grader sitting underneath every figure in the report. (authored — the source ships no fixture, no agreement check, and no blinding for its classifier.)
2. **Order.** Check the ordering constraints deterministically against the recorded timestamps, never inside the classification pass. Ordering is arithmetic on timestamps; asking a model for it converts a settled check into a second judgment.

Record the two failure kinds apart: a step that never appears is **absent**, a step that appears in the wrong position is **out of order**. They lead to different edits, and collapsing both into "failed" throws away the distinction that says which.

The harness has to emit, per event: a timestamp, the action or tool name, its input, its result, and a run identifier. Where no such record exists there is nothing to assert against, and the behavioral half of the run is unmeasurable — report that rather than substituting the agent's own narration of what it did, which is an output document about behavior and not the behavior.

## Never average across strictness levels

Report each level as its own number, per arm. Do not blend them into one compliance rate.

An agent that follows the skill at the supportive and neutral levels and abandons it at the competing level — where the user explicitly asked for something else — behaved correctly at all three. A mean over the ladder scores that run down, and what it erases is the finding itself: the supportive-to-neutral gap is the activation result, and the neutral-to-competing gap is how hard the skill pushes back against a user who wants otherwise.

This is the source's own defect stated as a rule. It averaged the three levels, compared the mean against a single threshold, and drove its only recommendation off that comparison — so it could not distinguish "the skill never fired" from "the user overrode it", which is the exact distinction the ladder was built to draw. Take the ladder; rebuild the scoring.
