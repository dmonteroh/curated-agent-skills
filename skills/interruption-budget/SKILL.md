---
name: interruption-budget
description: "Governs when an agent interrupts a human and how it decides the rest alone: classify every question as a one-way or two-way door where it is declared, never shrink an option set to fit a tool's cap, and shape each question to be answered fast and audited later. Use when about to ask a human, when options exceed a tool's cap, or when designing a workflow that asks repeatedly."
metadata:
  category: workflow
---
# Interruption Budget

Provides the protocol that sits between two symmetrical failures. An agent that stops too often turns approval into reflex: it spends the human's attention *and* launders unreviewed decisions as approved ones. An agent that stops too rarely reaches the same place silently — the human never learns a choice was made for them.

Two mechanisms carry this skill because both are enforced rather than advised: door typing fixed at the declaration site, and option-set integrity under a tool's option cap. Rationing interruptions against a budget — the practice this skill is named for — is not implemented by this skill and must not be read as established practice.

## Use this skill when

- An agent is about to ask a human something that a standing preference or an automatic rule could suppress
- A question carries more options than the question tool accepts
- A multi-phase run will stop and ask many times, and the interruptions need shaping before it starts
- Questions can be declared ahead of the run and need a safety class attached to them
- The question channel is capped, erroring, absent, or attached to no human at all

## Do not use this skill when

- The decision is a consent gate for a mutation the human must authorize. Consent is not an advisory interruption: it is never rationed, batched away, or auto-decided.
- The question is irreversible and the reason for reaching here is to find a way not to ask it. One-way doors surface; nothing in this skill suppresses one.
- A single reversible question in a short interactive session — declaring, classifying, and shaping it costs more than asking it
- The human already answered. Re-confirming an answered question is a second interruption, not a safety measure.
- The problem is *what* to ask: framing, requirements discovery, option generation. This governs whether, how, and how many times, not the content of the inquiry.

## Decision points

1. **One-way or two-way?** Read the declaration, never the runtime wording. Undeclared → run the destructive-verb test and take the stricter answer. One-way → ask; no preference, budget, or automation may suppress it.
2. **Does a standing preference apply?** Project-local beats global. Suppression requires all three of: a two-way door, a stable question identifier, and exactly one unambiguous recommended option. Any one missing → ask.
3. **More options than the cap?** At or under the cap → ask normally. Over it → coherent alternatives that exclude each other → batch into groups; independent scope items carrying their own include-or-cut decisions → split into one question per option; unsure → split. Far over → ask how to proceed before firing anything. Chain behavior once split: see the mechanics below.
4. **Did the question call fail?** A suppression denial is not a failure → proceed with the named option, no retry. A genuine error where no answer could possibly have surfaced → retry once. Then branch on session kind: sub-agent → take the recommended option; no human attached → declare blocked and stop; interactive → prose fallback.

## Door typing at the declaration site

Each question an agent can ask carries a door type fixed where the question is *declared* — in the workflow definition, the catalog, the task template — and never derived at runtime from the question's own summary text. One-way means irreversible or destructive: delete, force-push, drop, overwrite, and beyond raw verbs, architecture forks, security and compliance choices, and scope additions large enough that undoing them costs real work.

The rejected alternative is the point of the rule. Runtime classification by parsing the question's prose was tried and rejected because **safety would depend on wording** — a destructive action phrased mildly is classified as reversible, which is unacceptable for a safety gate. The accepted cost is stated plainly by the same source: every new question has to be classified, and that governance burden is the price of the guarantee.

Three rules keep the classification from becoming fiction:

- **Completeness is enforced by something that fails loudly.** A check outside the agent's own diligence asserts that every ask site has a declaration, and fails on drift, renames, and duplicates. Declarations that nothing audits rot silently, and a rotted declaration set is worse than none because it is still trusted.
- **An unknown question falls back to the stricter class.** A question with no declaration runs through a destructive-verb test before anything else. This exists because of a real defect: an ad-hoc destructive question with no declaration defaulted straight to the reversible class and was auto-decided away by a standing preference.
- **One-way doors always surface**, regardless of any preference, cap, ranking, or budget. This precedence is stated, not left to be inferred — an earlier plan in the same source carried both "every one-way door surfaces" and "at most N questions per phase" without saying which wins, and that omission was itself recorded as a defect.

*Authored, not sourced:* where a harness has no declaration list and no completeness check, classify inline at the ask site and treat anything unclassified as one-way. The sources assume a repository with a build-time check and never state a degraded mode.

## Suppressing a question with a standing preference

A human may set a per-question standing preference — always ask, never ask, or ask only for one-way doors. Resolution runs on the rules below plus the two precedence rules in the ladder above, and every one of them belongs to whatever gates the question rather than to the agent's own compliance:

- **Key preferences on a stable, author-assigned identifier**, never on a hash of the question's wording. Wording-derived keys observe, they never decide. (*The stated design is the author-assigned key; the reason — a hash breaks the moment phrasing drifts, silently losing the stored preference — is inference from that design, not spelled out in the source.*)
- **Refuse to auto-decide on ambiguity.** The auto-chosen option is read from exactly one explicit recommendation marker. Two markers, or none that parses, means pass through and ask. Guessing here produces a silent-wrong decision the human discovers much later.
- **Multi-question calls are all-or-nothing.** One ineligible question in a batch makes the entire call ask.
- **Announce every auto-decision in band** and log it with a marker identifying it as auto-decided, so it can be reviewed afterwards.
- **Log from the suppression path itself.** Suppressing a question also suppresses whatever logs the answer, because that logging runs after a call that no longer happens. The audit trail lives on the path just removed — a trap for anyone building any kind of suppression, not only this one.

*Authored, not sourced:* where the harness offers no interception point before the question is asked, do not implement suppression at all. Every guarantee above then rests on prose compliance, which the sources themselves describe as weak, and an unenforced suppression rule is a silent auto-answer waiting to happen.

## Option-set integrity under a cap

Question tools cap the number of options they accept. **Never drop, merge, or silently defer an option to fit that cap.** The option set is the human's decision space; shrinking it silently is the bug, and it is worse than an error because it arrives with a plausible justification attached.

The recorded failure is a transcript of an agent narrating its own unilateral cut and moving the dropped item to a backlog, reproduced under Examples. Two compliant shapes exist instead — batching coherent alternatives into groups, or splitting independent scope items into one question each (decision point 3). Batching orthogonal scope items into a single question is the same failure as dropping one, which is why *unsure* resolves to split.

**Sizing.** At or below the cap, ask one normal question. A little above it, split, or batch when a clean grouping exists. Far above it, fire a meta-question first, offering: proceed with the full split, narrow the scope first, or batch into groups. That meta-question is a real interruption and counts as the chain's first one. *The source's boundary for "far above" was more than six options against a cap of four — a chosen, unexplained default with no derivation, so it cannot be rescaled to another cap by formula. Judge it against the human's tolerance for a long chain, not against arithmetic.*

**Split-chain mechanics:**

- **Check dependencies before firing anything.** If option 3 requires option 1, say so in option 3's own explanation. Without this the chain produces incoherent picked sets — include the dependent, cut its prerequisite, ship an unbuildable scope.
- **Label the chain stably**: a parent label, one child label per option, a distinct label for the closing summary, and a distinct label for a single-option redo.
- **Four buckets per option, not two**: include, defer, cut, hold.
- **Hold means stop, not queue.** Halt the chain immediately and wait for the human to resume. Queueing the remaining options behind a hold and firing them later, against context the pause invalidated, is the failure this bucket exists to prevent.
- **The closing summary validates before it confirms.** Re-prompt any dependency conflict as its own question offering keep the prerequisite, cut the dependent, or accept the broken state; then confirm the assembled scope; on a revise request, re-ask exactly one option and never the whole chain.
- **Give every option in the chain a unique, stable identifier**, so a never-ask preference on one option cannot auto-answer its siblings. Uniqueness alone was judged insufficient: as a second layer, force normal asking on every question in a split chain even when a matching preference exists, and say why in the question.
- **This rule outranks per-workflow batching guidance.** A stricter local rule — one issue per call — is compatible as a special case of it.

## Question shape

A question answerable in seconds and auditable in a month has a fixed shape: a stable label and one-line title, a grounding line naming the work, a plain-language statement of what is being decided and what breaks if it is decided wrong, real pros *and* cons per option, a recommendation line that is always present, and exactly one marker on the recommended option. That marker is load-bearing rather than cosmetic — the suppression path reads it, so a question with no unambiguous recommendation cannot be auto-decided at all. Two consequences are easy to lose: state effort on **both** scales, human time and agent time, so the compression between them stays visible at decision time; and where there is genuinely no preference, say so **and still mark a default**, since omitting the marker reads to every automatic path as an unparseable question.

Full format, the pre-emit self-check, and the source's chosen-default floors for pros and cons: `references/decision-brief-format.md`.

## When the question channel fails

Distinguishing a denial from a failure is what makes the rest safe (decision point 4). Two details carry the weight:

- **Retry at most once, and only when no answer could possibly have surfaced.** A missing-result error can arrive *after* the human already saw the question; retrying then double-prompts.
- **A prose fallback is a weaker gate than the tool**, so one-way doors get *stronger* handling on that path: require an explicit typed confirmation naming the exact option, state plainly what is irreversible, and never proceed on a vague, partial, or ambiguous reply. "ok" or "sure" without the explicit choice is not-yet-confirmed.

The prose fallback carries the same content the tool call would have, and each brief keeps a stable label so a bare reply can be matched to it. With more than one brief open — a split chain — do not guess which one a bare letter answers; ask. Layout and the continuation rule: `references/decision-brief-format.md`.

## Non-ASCII text in questions

Emit literal characters in every question and option string; never hand-escape them as codepoints. Only escapes the serialization format itself requires stay. The reason is a model-behavior fact rather than a formatting preference: escaping requires recalling each codepoint from training, which is unreliable, and the trigger for reflexive escaping — a long, multi-line question dense with non-Latin script — is exactly where miscoding is most damaging and where the human sees mojibake instead of a question. Length is not a reason to escape.

## Common pitfalls

- Trimming an option to satisfy a cap and reporting the trimmed set as the decision space
- Letting a standing "stop asking me this" answer a destructive question, because the question was never declared and defaulted to the reversible class
- Classifying a mildly-worded irreversible action as reversible by reading its prose
- Suppressing a question and losing its audit record along with it
- Hanging on a question in a session with no human attached, instead of declaring blocked
- Writing a pacing or ordering rule as a preamble sentence when the flow it must override is fixed downstream — the change is sequencing, not wording, so it needs a mechanism and quietly does nothing without one

## Examples

**Six independent scope items, cap of four.**

Wrong — the option set is edited to fit the tool, and the edit is reported as a judgment:

> "Cap is four. E4 is the largest-effort item and a natural follow-up, so it moves to the backlog. Re-firing with four."

Right — the shape changes, the set does not. Above the cap and far enough above to warrant it, a meta-question comes first ("full split of six, narrow scope first, or batch into groups?"), then one question per item, each with its own stable identifier and its dependencies named in the explanation, then a closing summary that re-prompts the conflict when E3 is included after E1 is cut.

**A destructive question with no declaration.**

Wrong: no declaration exists, so the question takes the reversible default, a standing never-ask matches, and the branch is force-pushed with an in-band note nobody reads.

Right: no declaration exists, so the destructive-verb test runs first, returns one-way, and the question surfaces despite the preference — in an interactive session with a prose fallback in play, requiring the exact option typed back before anything runs.

## Output contract

- Every question emitted in the fixed shape: stable label, plain-language stakes, pros and cons, one recommendation marker, and a default even when the posture is neutral
- Every auto-decided question announced in band and recorded with its identifier, the chosen option, and the fact that a preference decided it — written from the suppression path, not from the answer path
- For a split chain: one question per option with unique identifiers, and a closing summary that validates dependencies before confirming the assembled set
- At the end of a run, the split between what the human answered and what was decided for them, itemized enough to audit

## References

- `references/decision-brief-format.md` — the question format, its self-check, the prose-channel layout, and the continuation rule
