# Synthesis prompt

Dispatch context: this run is a dispatched subagent of the repository's review pipeline, and the orchestrator has already handled the CLAUDE.md/AGENTS.md session-bootstrap. Skip every bootstrap step - do not run .agent/scripts/status.sh, do not read .agent/ files - and begin the synthesis immediately.

Goal: high-quality agent skills. Every skill in this library must work for any vendor's agent - Codex, Claude, and Copilot alike - and must be correct against the review checklist. Judge every proposed change against both: does it make the skill better for every vendor, and is it grounded in a named section of the checklist.

A review is evidence, not authority. Apply a finding because it is grounded in the checklist and verifiable in the skill file - never because of which agent wrote the review, and never because its wording reads as familiar. A change that would serve one vendor's agent better than another's fails the first requirement above, whoever proposed it.

Record the checklist section behind every finding you apply. Acceptance is anchored to the bar, not to which review sounded more convincing.

Task: synthesize every review of one skill into the single change that actually lands. Read the reviews, apply the tie-break chain below, and write the result - or write QUESTIONS and write nothing.

Read first, in this order:
- scripts/auditing/SKILL_REVIEW_CHECKLIST.md, the placeholder CHECKLIST_PATH below - the binding bar. It outranks every review's characterization of it.
- SKILL_DIRECTORY and everything under it - the one skill this run is synthesizing for.
- REVIEW_ARTIFACTS - every reviewer arm's finished review of SKILL_DIRECTORY for this run, in supply order. Refer to them only by position: Review 1, Review 2, and on through Review N. The set may hold any number of reviews; nothing here fixes the count at any particular number, and none of them is treated as identity-stripped - a review may well read as the work of a particular arm, and that readability is never itself evidence for or against its findings.
- SKILL_NAME - SKILL_DIRECTORY with the leading skills/ and the trailing slash removed. Needed only to name this skill's own trigger-case file, scripts/auditing/trigger-cases/SKILL_NAME.md.

## Scope and write authority

Write only inside SKILL_DIRECTORY, plus that skill's own trigger-case file, scripts/auditing/trigger-cases/SKILL_NAME.md. Nothing else. That is exactly the write authority a single reviewer already holds under checklist section 4 - no wider.

Every review in REVIEW_ARTIFACTS is read-only input to this pass. This synthesis run is the only writer for this skill: it does not defer an edit to a later pass, and it does not ask a review to make one.

Removing a whole section, a file under references/ or scripts/, or the skill itself stays propose-never-execute, exactly as it does for a single reviewer: name it in the removal-proposals block described below, with evidence and what would be lost, and make no edit for it.

## Tie-break chain

Apply in order, for however many reviews REVIEW_ARTIFACTS holds:

a. A finding is actionable only if it cites a specific checklist section and the cited condition is verifiable in the skill file. A finding no review can ground in the checklist is not applied.

b. Where two or more positions are grounded in the checklist and conflict, subtraction wins. Normalize each proposed cut to the set of whole text units it deletes - a sentence, a list item, a paragraph, a heading qualifier, a section, at the granularity checklist section 4's delete-without-asking list is written at - then apply the union of those sets. Every unit any review proposed deleting on grounded evidence is deleted whether or not another review named it, so overlapping, nested, and disjoint cuts all resolve by the same operation: no cut is measured against another, and no size metric or tie-break between cuts is ever needed. A deletion that leaves part of a text unit standing is a rewrite, not a cut - this step does not govern it, and a rewrite that conflicts with a cut reaches step c. Whole sections, files under references/ or scripts/, and whole skills stay propose-never-execute regardless of which review proposed them, tested against the resolved union and not only against each individual proposal - a union that amounts to a whole one of those units is proposed with evidence, never executed.

One narrowing applies to the union, and only one: it never deletes the last statement of a rule. Before applying the union, group its units by the rule each one states - two or more units state the same rule when each would satisfy checklist section 4's "a second statement of a rule already stated elsewhere in the same file" with the others as its elsewhere, judged on the rule stated rather than on identical wording, so a paraphrased copy groups exactly as a byte-identical one does. That grouping needs no judgment step a did not already require: where the skill file will not support the determination, the finding was never verifiable and step a has already dropped it. For each group of two or more units, look for a statement of that rule standing outside the union: if one stands - three or more copies with only some of them cut - apply the union unchanged for that group, because a home survives; if none stands - reviews cutting different copies of the same rule - delete every unit of the group except the one appearing earliest in the file, and retain that one. Record the group, the retained statement with its location, and each deleted copy, as an applied finding. Nothing else narrows the union: a unit that is not one of two statements of the same rule applies in full, and a single grounded cut is never held back for being the only statement of anything.

c. Only a conflict surviving steps a and b - two or more positions grounded in the checklist, on the same span, and not settled by step b - ends the run with QUESTIONS instead of a change. State every surviving position as a numbered list: each entry names the file path (with the line number where the span is line-scoped), the position itself, the checklist section it cites, and the single decision the operator must make, written as a closed choice among the surviving positions. No other kind of disagreement ends a run this way.

The chain ranks positions by how well each is grounded in the checklist, and by nothing else. Which arm wrote which review, and where a review sits in the supplied order, are never evidence - that is true whether or not the wording of a review makes its author guessable, because guessing an author was never part of the test.

## Read the bar yourself

Do not take a review's account of what the checklist says as the bar itself. Open CHECKLIST_PATH and check the cited section directly before applying or rejecting a finding. A review that mis-cites the bar is caught here, not carried forward into the output.

## Output

One contiguous restatement, in this order, under this heading only:

- Files changed under SKILL_DIRECTORY or the trigger-case file, or "none".
- For every finding this pass applies: the checklist section it rests on, named directly - section 4, section 7, and so on - never "the bar" or "the reviews" left unnamed. Acceptance is anchored to the section cited, not to which review sounded more convincing.
- A removal-proposals block: numbered, each entry naming the file and section, the evidence, and what would be lost, written as none when there are none.
- A differentiation line, placed inline the way this sentence places it: STRONG or WEAK, with one line of evidence, never standing alone on its own line.
- Where step c of the chain above still applies once everything above is settled: the numbered list of surviving positions that step c describes, in place of a change.
- Exactly one final line, alone and flush left, closing the artifact - transcribed word for word from the checklist's own Verdicts section: NO-CHANGE, meaning the skill meets the bar, a first-class outcome; CHANGED, meaning edits applied; or QUESTIONS, meaning blocked on ambiguity, and do not guess. Alongside NO-CHANGE or CHANGED, always include the differentiation line and the removal-proposals block from above, written as none when there are none. QUESTIONS ends the artifact immediately and carries neither, and nothing landed for this skill on this run.

Record this artifact's result by running, exactly once, when the artifact above is finished:
- For NO-CHANGE or CHANGED: RESULT_TOOL_PATH --status <no-change|changed> --differentiation <strong|weak> --removals "<none, or the numbered removal-proposals block from the artifact above, passed verbatim and in full - it is recorded for the operator's ruling, and a summary records nothing>"
- For QUESTIONS: RESULT_TOOL_PATH --status questions

Running that command is what files this artifact's result. A status written in prose above is commentary for the reader and is filed nowhere, so an artifact that only writes prose leaves no result on record.
