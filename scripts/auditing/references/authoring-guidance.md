# Authoring guidance

Depth behind `SKILL_REVIEW_CHECKLIST.md`. The checklist is the bar; this file is how to apply it when a judgment call is not obvious. Read the section you need, not the file.

## Pruning: the five ways a skill accumulates dead weight

Named so a review can point at one rather than argue taste. Source pattern: `mattpocock/skills` → `writing-great-skills` (MIT), reimplemented.

| Failure mode | What it looks like | What to do |
| --- | --- | --- |
| **No-op** | A sentence that constrains nothing. `## Workflow (best performance, best results)`. "Follow best practices throughout." | A no-op that is itself one of `SKILL_REVIEW_CHECKLIST.md` §4's closed five — the heading-qualifier example above is closed-five item #4 — delete autonomously. A no-op outside the closed five (the "Follow best practices" example above): propose with evidence, never execute unilaterally. |
| **Duplication** | The same rule stated in two sections, often 10 lines apart, in slightly different words. | Keep the statement in its owning section; delete the other — closed-five item #3, One Rule One Home. Replacing it with a pointer is outside §4's closed five: propose with evidence, never execute unilaterally. |
| **Sediment** | Text that exists because a template demanded a slot: a heading restated as its first sentence, the frontmatter description repeated as line 1, a final step reading "assemble the report per the output contract". | Delete. |
| **Sprawl** | The skill has grown to cover adjacent topics it was never scoped for. | Propose the section for removal; name what it would belong to instead. |
| **Premature completion** | A step declares success without a check that could have failed. | Outside §4's closed five: propose a falsifiable check or the claim's removal, with evidence — never execute unilaterally. |

**The no-op test**, applied sentence by sentence: if this sentence were deleted, what would an agent do differently? No answer means no sentence.

## The differentiation judgment

The test is not "is this a real topic". It is: *does this skill change what a frontier model would do unprompted?*

Worked contrast, from this library, both verdicts measured by with/without counterfactuals (2026-08-22) rather than argued from the text:

- **WEAK — `database-architect` (measured, then removed 2026-08-22).** Its storage-selection → schema → migration workflow read as substantial, and two vendor arms plus a synthesis unanimously argued it WEAK from the text — but the with/without runs are what settled it: both vendors produced schema-enforced invariants, safe concurrent-write handling, and full checksum-gated expand/contract migrations without the skill. The skill contributed an idiom and an output shape, no correction. A restatement of baseline competence can look like expertise; only the counterfactual shows the model already had it.
- **STRONG — `testing`.** Carries embedded scripts that produce a deterministic report, a stated mocking default that overrides the model's own instinct, and decision points that branch on repo state. Remove it and behavior changes.

Text-only differentiation verdicts ran near coin-flip against measurement on the six-skill advisory cluster (both false-STRONGs and a false-WEAK — `cloud-architect`'s arms argued WEAK and measurement reversed it). Where a verdict will drive a consolidation or removal decision, measure; a text verdict is a hypothesis.

Report the verdict with its evidence. Do not act on it: differentiation is a flag with evidence, acted on by nobody but the operator — it is not a removal trigger.

## Over-constraint

Frontier models now lose more to being over-directed than to being under-directed. A rule that overrides judgment the model exercises better unaltered is a cost.

Constrain the **process** — what gets checked, in what order, against what gate, with what stop condition. Leave the **craft** — naming, phrasing, structure of the produced artifact, choice among equivalent idioms.

Tell for an over-constraint: the rule would produce a worse result than the model's default in a case the author did not consider, and the skill offers no escape hatch.

## Leading words

Where a skill has one central concept, anchor it on a compact term the model already thinks with — *seam*, *tracer bullet*, *deep module*, *red-capable command* — and use that term consistently throughout. Consistency of language is the mechanism; a concept named three ways is three concepts.

Crediting the term's owner ("a seam, in Feathers' sense") is a leading word, not a persona. Adopting the owner's voice is a persona.

## Teach by contrast

Where a failure is easy to fall into, show it. A wrong version beside a right one moves behavior more than a rule describing the difference, and it gives the reviewer something falsifiable to check.

A `Rejected framings` or `Anti-patterns` section is allowed and earns its place when the skill exists because of a common wrong approach.

## Behavioral gates

Available when a skill guards a real failure mode. **Earned, never mandatory** — a gate on a skill with no failure mode to guard is sediment. Source pattern: the operator's `ai-workflows` (`workflows/conventions.md` and the workflow catalog), reimplemented here.

- **Anti-rationalization table** — rows of `excuse | counter | what the gate protects`. Records the argument an agent will make for skipping a step, and the answer, at the point of temptation. Stays inline and full-length; it is a contract, not duplication of the gate it protects.
- **Forbidden claims** — a list of phrases banned from completion reports: "probably caused by", "should fix the issue", "appears to work". Cheap, mechanically checkable, and it forces evidence in place of confidence.
- **Completion self-check** — numbered verification where a failed item names the step to return to, rather than a list of things to mention.
- **Loop cap with a named stop state** — "maximum follow-up rounds: 2; on exhaustion mark `blocked` and escalate with all evidence". A cap without a named terminal state is not a cap.

## Falsifiable verification

Source pattern: the `dot-agent` operating model's `groom` skill.

A verification claim must name a check that could have failed and what its failure looks like. The canonical example: a word count falling is not evidence a pruning pass was lossless — it is equally consistent with having deleted content. Prove it (enumerate every identifier, command, and path in the original; grep each one back) rather than asserting it.

An output contract listing what to *report* is not verification. It describes a message, not a check.

## One Rule, One Home

Within a single file, each rule has exactly one owning section. Every other mention is a short pointer to it, or is deleted. Restating a rule in three sections does not enforce it three times; it creates three copies that drift.

Checklists and self-checks may name the fields they verify; they never restate a rule's full definition. They point at the owning section.

Deliberate duplication across files is different: it is declared as a parity family in `scripts/check_parity.py`, updated in one change, and verified by diffing the members. Undeclared duplication is a defect.

## How a skill is invoked

Vocabulary for describing where a skill sits in a verification loop. Useful in a `Use this skill when` section; not a required field.

- **Standalone** — the operator invokes it directly for a bounded task.
- **Embedded** — it runs inside a longer task the agent is already performing.
- **PR-time** — it runs against a diff or a proposed change rather than a working tree.

**Chained** — a skill invoking another skill by name — is rejected in this library. It requires the other skill to be installed, which breaks portability. Cross-skill sequencing belongs in the consuming project's `AGENTS.md`.

## Patterns rejected on purpose

Recorded so a future author does not import them from a source library that uses them well. Each is correct in a coupled, single-vendor product and wrong here, because this library's skills install individually into arbitrary repositories across Codex, Claude, and Copilot.

| Pattern | Where it works | Why it is rejected here |
| --- | --- | --- |
| Router / dispatcher skill | `mattpocock/skills` `ask-matt` | Requires the whole suite to be installed; a router with half its targets missing is worse than no router. |
| Cross-skill `/name` invocation | `mattpocock/skills` `wayfinder` | Hard dependency on another skill. Breaks the founding constraint. |
| Shared setup skill writing a config other skills read | `setup-matt-pocock-skills` | Introduces install order and shared state across skills. |
| Declared hard/soft dependency tiers | `mattpocock/skills` ADR 0001 | Manages coupling rather than avoiding it. This library avoids it. |
| Plugin-only distribution | Claude Code plugin packaging | Single-vendor lock-in; these skills must install for Codex, Claude, and Copilot alike. |
| Description-embedded activation triggers | Model-invoked skills generally | Frontmatter must load identically across three tools; cues stay in `trigger-cases/`. Settled; not re-opened. |
| Hard-wrapped prose | `dot-agent` skills, `ai-workflows` | Deliberate divergence: soft-wrap diffs better and edits better under an agent. Not drift. |
