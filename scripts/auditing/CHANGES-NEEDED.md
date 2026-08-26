# Changes needed in the auditing system

Source: the `writing-style` measurement campaign, 1,645 agent runs across four models. The lessons behind each change: `tmp/writing-style-skill/LEARNINGS.md`. The numbers: `tmp/writing-style-skill/measure/RESULTS.md`. This file proposes edits and does not make them — the quality bar is the operator's to change. Each item names its target file.

## 1. `SKILL_REVIEW_CHECKLIST.md` — the description section

The description is the whole activation surface: both vendors select on it alone and never see the body until after selection. The checklist should demand of every description:

1. **Imperative, pre-emptive framing** — "Use this skill whenever you are about to…", read before the work starts, never a passive what-then-when summary. Measured across three A/B rounds: passive framing activated 12% of the time, imperative 55%, the artifact-enumerating imperative 90%.
2. **Artifact enumeration** — name the deliverable types, and know that naming alone is not enough (1 of 5 without the framing above).
3. **Self-containedness** — no reference the reader cannot resolve from the description itself. One such phrase cost 30 activation points between otherwise identical wordings.
4. **No keyword lists.** `Triggers on:` lists measured worse than the same framing without one. The existing rejected-pattern convention gets a measured basis and moves from convention to requirement.
5. **Stop reviewing the name and category for fit.** Identity was irrelevant in two matrices: 359 of 360 on one model, then a 3x3 across four models. Every miss traced to a probe and never to an identity. Keep only the mechanical name-matches-folder check.

## 2. `SKILL_REVIEW_CHECKLIST.md` — the body section

The body is a program loaded on every activation, and section order is behavior.

1. **Carve-outs sit after the pipeline they carve out of.** A reply section placed above the workflow swallowed deliverables typed into chat and halved the gate-run rate. The same text below the output contract restored it.
2. **Skills claiming more than one surface state the boundary explicitly** — what decides which path applies is the artifact, never the channel. Models classify by channel unless told otherwise.
3. **Every loaded token must change behavior.** Provenance, credits, and licence text belong in a reference file that nothing advertises from the body. Reviewers should ask of any body sentence: what does the model do differently because this is here?
4. **No completion contracts at the top of the body.** A "Done means:" block, plausible-looking discipline, suppressed tool runs from 10/20 to 4/20 at floor size. A stated definition of done reads as satisfiable without the tool.

## 3. `SKILL_REVIEW_CHECKLIST.md` — a new section for tool-bearing skills

For any skill that ships a script:

1. **The invocation prose is a review point of its own.** The differentiating half of a tool-bearing skill is the tool, and the tool only matters if it runs. The invocation prose is the most vendor- and tier-sensitive text in the skill. One wording took one vendor from 2/10 to 10/10 and did nothing for another. One model never engaged the tool at all.
2. **No arguments the model must invent.** Every choice handed to the model at invocation time is a failure surface. A four-option profile flag produced nonexistent names in 15% of traced invocations, each one a dead run. Remove the choice or fail open with a notice, never with a retry-teaching error.
3. **Rules that need to know what the text is FOR stay out of the tool.** A linter reads text. "Is this a procedure step" is a fact about the deliverable. Such rules live in the body as prose.
4. **State the enforcement cost.** The measured gate roughly doubled cost per deliverable. A value claim without its cost claim is half a claim.

## 4. `SKILL_REVIEW_CHECKLIST.md` or `references/authoring-guidance.md` — references

1. Split references by **reader and moment of need**, never by topic: who opens this file, at which workflow step?
2. **No stored copy of anything live.** Two mirrored copies drifted in one campaign, each silently invalidating what used it.

## 5. `references/authoring-guidance.md` — the depth

Absorb the three-products frame: description = retrieval target, body = per-activation program, references = on-demand memory. Absorb the surface map question — which vendor loads a skill where, and what needs a project instruction-file block instead — with the measured numbers as rationale. `LEARNINGS.md` is the source to compress.

## 6. `reviewer-prompt.md` and `synthesis-prompt.md` — what reviewers may claim

Runs found every shipped defect in this campaign. Reading found zero. Extend the differentiation rule (measured, never asserted from text) to activation:

1. A reviewer may flag description **shape** violations — passive framing, keyword lists, unresolvable references — as checkable facts.
2. A reviewer may not assert that a description does or does not activate, and may not grade register or output quality from reading. Those claims carry run evidence or the label "not measured".

## 7. `audit_skills.py` — mechanical checks only

The audit is shape-only, and two of the lessons are shape:

1. **Warning: `activation_keyword_list`** — a description containing a `Triggers on:`-style enumeration. Measured worse than framing, and mechanically detectable.
2. **Warning: `body_provenance_section`** — a `## Provenance`, `## Credits`, or `## Sources` heading in `SKILL.md`. Credits do not change behavior and belong in a reference file.

Nothing else from the campaign is decidable from shape. Resist encoding the rest as regexes — that is how a rule that needs intent ends up in a tool.

## 8. `trigger-cases/` convention — one addition

A trigger-case file should carry at least one positive case per artifact class its description names. The campaign found a model that silently dropped one whole class — code-comment requests activated 1 in 9 on haiku against 9 of 9 on three other models — and only a per-class probe surfaces that. No format change, just coverage.

## Sequencing

Items 1-4 are checklist edits and land together as one ruling. Item 5 follows them. Item 6 touches the dispatched prompts and should land before the next review batch runs. Item 7 is tooling and can land any time with its fixtures. Item 8 is a convention note in the auditing README.
