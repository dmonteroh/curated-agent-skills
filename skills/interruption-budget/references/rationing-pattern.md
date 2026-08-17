# Rationing pattern — design under review

**Status: not established practice.** The source document's own status line reads *not yet implemented*. A search across the accompanying source drop found no implementation of its ranking step, its per-phase state, its visible list of auto-accepted decisions, or its reopen command. Its genuine contribution is the gap analysis below: an unusually honest account of why the design could not ship as written. Use it to build and validate a budget, never to justify one already in flight.

## The intended shape

1. Rank the decisions pending in a phase.
2. Surface only the top few as real questions.
3. Auto-accept the remainder into a list the human can see, one line each.
4. Offer a command that reopens any auto-accepted item as a real question.

## Accounting rules

These were folded in from a parallel effort and approved as a decision, so they carry more weight than the unimplemented machinery around them — but they remain untested.

- **Chain-scoped.** A chained phase deducts from what is left and never resets.
- **Handoffs carry the spend forward.** A phase that hands work to another agent hands the interruptions already spent along with it.
- **Approval and mutation gates never count against the budget.** It rations advisory interruptions, not consent.
- **Spend on the hardest-to-reverse decisions first.**
- **Work scale sets the budget; ranking decides what the budget buys.** Two separate steps.
- **A one-shot prompt that fires outside the work is exempt from the work's budget** — first-run setup lands before any phase begins — but it still counts against the human's patience for that first run, and the preferred fix is suppressing it in favor of a voluntary opt-in, not charging it to a phase.
- **One-way doors surface uncapped.** Only two-way decisions are capped. Stating this precedence *is* the safety property: an earlier revision of the same plan carried both "every one-way door surfaces" and a per-phase maximum without saying which wins, and recorded that omission as a defect.

## Numbers: what the source actually says

| Figure | What it is |
| --- | --- |
| Per-phase cap on two-way prompts | **Uncalibrated by the source's own admission.** Neither candidate scoring scheme behind it was validated against a real distribution of findings. |
| Ratio of surfaced to auto-accepted decisions | **A target for a calibration pass that was never run**, phrased as "instrument the log, pick the threshold from real data". Reading it as an observed ratio is wrong. Carry the intent — most decisions auto-accepted, a small minority surfaced — and none of the figures. |
| severity × irreversibility × does-the-human's-opinion-matter | **Recorded as broken, not chosen.** The multiplicative form collapses the scale into a handful of sparse values; an additive alternative with a threshold was considered; neither was validated. Carry the three factors as ranking inputs. Carry no combining rule. |
| A disengagement threshold in interruption count | **An unexplained assertion.** It sits next to one real observation — a single non-technical reviewer, one multi-phase session of dozens of prompts, ending in blanket approval — but is stated as a general threshold with no study behind it. The observation is evidence that the failure exists; it is not a number to gate on. |
| Acceptance targets against a captured baseline | **Chosen targets**, honest as targets, not evidence of anything. |
| Constants inherited from an adjacent effort | **Explicitly refused** by the source, on the grounds that the effort those constants came from had already replaced them. The most transferable line in the document. |

## Gaps to close before building it

Each of these blocked the design. They generalize past this one implementation.

- **Prose cannot invert existing control flow.** A ranking instruction added to a preamble does not reliably override a stop-and-ask sequence fixed further down the flow. The behavioral change wanted here is *sequencing*, not wording — so it needs a mechanism, and without one the fix appears shipped and changes nothing. This is the test for whether a pacing change belongs at the instruction layer at all.
- **A registry of declared questions does not cover findings discovered at runtime.** Door typing enforced at the declaration site cannot classify a finding the agent generates mid-run — which is exactly the population a budget is meant to rank. Either the declaration mechanism accepts runtime registration, or a runtime classifier covers the gap. Until one exists, one-way safety is not enforceable for ranked findings, and the budget must not be applied to them.
- **Budgeting needs state and a phase label, and neither existed.** What surfaced, what was auto-accepted, and what remains reopenable need a backing store; counting against a phase needs a phase field on the decision log. The plan simultaneously claimed no schema change was required.
- **A reopen command with no parser, no store, and no replay is prose, not a feature.** Worse: if the conversation compacts and the list of auto-accepted decisions leaves context, those decisions become unrecoverable. Any offer of "the rest were decided automatically and can be reopened" must answer where that list lives when the context that held it is gone.
- **Meta-prompts are interruptions too.** Setup and configuration prompts land before any real work and spend the same patience.
