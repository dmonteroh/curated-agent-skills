---
name: adversarial-plan-review
description: "Hardens a proposal before committing to it: reviewers with distinct attack vectors file independent findings, cross-attack them, then defend, refine, or concede each one; only survivors are distilled into constraints, decisions, risks, and open questions. Use before large or irreversible work, when a plan reads plausible but unchallenged."
metadata:
  category: workflow
---

# Adversarial Plan Review

Provides a debate protocol that puts a proposal under structured attack before any of it is committed to. The unit of work is a **finding**: one bounded claim, from one reviewer, holding one attack vector. Every finding must survive attack on the record before it reaches the output, and the material that does not survive is discarded before anything is synthesized.

The failure this addresses is unfounded confidence, not ambiguity. A single review pass — however hostile the wording — produces one round of mixed critique in which nobody's objection is itself objected to, and the plan that emerges is the plan that was written, lightly annotated.

## Use this skill when

- A stated plan, design, or approach exists and the cost of it being wrong is high: irreversible migrations, public interfaces, data model changes, large refactors.
- The plan reads plausible, agreement arrived quickly, and no one has produced a concrete reason it fails.
- The proposal came out of one pass by one agent, and its assumptions have never been contradicted by anything.
- Several concerns pull against each other — simplicity against coverage, structure against shipping — and a single reviewer would trade them off silently inside one voice.
- The record of *why* each surviving decision survived is part of the deliverable, not just the decision.

## Do not use this skill when

- The requirements themselves are unclear. Attacking a plan built on an unknown goal hardens the wrong thing; settle the goal with whoever owns it first, then run the panel on what comes out.
- No proposal exists yet. Round 1 attacks something stated; with nothing on the table it degenerates into ordinary ideation.
- The work is small, reversible, or well understood. The protocol costs several rounds of reviewer effort and returns a bundle nobody needed.
- The decision is already made and the request is execution. Running the panel then manufactures dissent against a settled call.
- Exactly one question is open and it has a cheap direct answer — "will this break the existing tests" is settled by running them, not by a panel.
- The reviewers cannot be kept independent. If every reviewer sees every other reviewer's output as it is produced, Round 1 is already contaminated and the rest of the protocol filters nothing.

## Required inputs

- The proposal under review, stated in full. Reviewers see only what is forwarded to them; anything left in the operator's head is not in the debate.
- Scope boundaries: what the proposal covers and what it deliberately excludes.
- The evidence reviewers may cite — repository access, measurements, prior incidents, documentation — or an explicit statement that there is none.
- A way to run each reviewer with its own context, and a way to wait for all of them before opening the next round.

## The panel

- **One attack vector per reviewer, and no two vectors overlap.** A vector is what the reviewer is hostile to, not a topic it covers. Two reviewers holding the same vector do not check the plan twice; they file the same finding twice, and it then survives the filter twice and reads as independent corroboration. (authored)
- **Roles are roles, not models.** The panel can be concurrent subagents, sequential prompts to one model, or repeated passes by one model under different briefs. No vector requires a particular model, vendor, or reasoning tier: the source protocol mapped each role onto a named model tier and offered no evidence for the fit, so that mapping is not carried here.
- **Expansion-biased vectors carry a limiting clause.** Structure and reframing both argue for adding something, and unbounded they generate plausible noise that then consumes a full round of attack. Their clauses below are part of the role, not decoration. A vector added later without one should not be added. (the general rule is authored; the two clauses are from the source)
- **Panel size is chosen.** The five vectors below are the set the source ran; nothing measures five as correct. Add a vector only with a distinct hostility and its own bound; run without one only by stating the degraded roster in the output.

| Reviewer | Attacks | Bound |
| --- | --- | --- |
| **Subtraction** | over-engineering, premature abstraction, scope creep, features held for a future that has not arrived | Subtracts only. Proposes no feature, no layer, no flexibility. |
| **Blast radius** | missed edge cases, unenumerated failure modes, cross-module interaction, pre-existing tests nobody checked | Names the specific interaction, state transition, or edge case. "This is risky" is not a finding. |
| **Evidence** | claims with no observation behind them: "I think it works this way", unread documentation, unverified behavior | Every finding cites a file and line, a document, or an explicit "no evidence found". |
| **Structure** | leaky abstractions, hidden coupling, brittle interfaces, debt the proposal creates | Not an over-engineer: demands the simplest structure that meets today's requirements, and rejects patterns that do not pay for themselves now. |
| **Reframing** | the first-found framing accepted as the only one; the literal request solved instead of the underlying need | Not novelty for its own sake: the conventional option may win, but it must earn that win against stated alternatives rather than by default. |

Briefing text to forward to each reviewer, and the per-round instruction blocks: `references/panel-roles.md`.

## Workflow

Three rounds, with a barrier between each. The count is not a dial to turn: each round does a job the others cannot — produce material uncontaminated by other reviewers, put every piece of it under attack, and let each reviewer answer only the attacks aimed at its own findings. Adding rounds of the same kind is repetition, and removing one removes a function.

### 1) Round 1 — findings only

- Each reviewer receives the proposal and its own brief. Nothing else, and nothing from another reviewer.
- Output is numbered findings: one claim each, specific in the way the vector requires.
- **Critique and synthesis are forbidden in this round.** There is nothing to critique yet, and a reviewer that opens with a recommended plan has skipped its vector to reach a conclusion everyone else will now anchor on.
- Cap findings per reviewer and length per finding, and state both caps in the brief so findings arrive comparable. Any specific cap is chosen: the source used three to seven findings of at most three sentences, with no derivation behind either number.
- Barrier: do not open Round 2 until every reviewer has returned.

### 2) Round 2 — cross-attack on the full bundle

- Aggregate every Round 1 finding into one bundle, attributed by vector, and forward the same complete bundle to every reviewer.
- Each reviewer attacks every finding except its own, from its own vector.
- **A finding the reviewer does not attack gets an explicit `STANDS — <reason>`.** Silence is not survival: an unmarked finding is indistinguishable from one nobody read. The explicit line makes survival something a reviewer asserted and can be held to.
- Do not soften the brief into a request for thoughts. Adversarial pressure is the mechanism; a collegial round returns the hedged mixed critique this protocol exists to replace.
- Barrier: wait for every cross-attack before re-keying.

### 3) Round 3 — defense on a narrowed input

- Re-key the attacks by the finding they targeted. Send each reviewer **only the attacks aimed at its own findings** — never the full Round 2 bundle, never another reviewer's defense.
- The asymmetry is deliberate: a reviewer that can see how others defended calibrates against their rhetoric instead of against the evidence.
- Exactly one verdict per attacked finding: `DEFEND` (rebut with concrete evidence), `REFINE` (the attack landed; restate the finding in its stronger form), `CONCEDE` (the attack defeated it; state what survives, if anything).
- No fourth option and no verdict-free discussion. A finding restated at greater length with no new evidence is a concession written as a defense.
- Barrier: wait for every reviewer before filtering.

### 4) Filter, then synthesize

Survivorship runs as its own step, before anything is written into the output:

- **Keep** findings that were uncontested, that were `DEFEND`ed with concrete evidence, or that were `REFINE`d — in their refined wording, not the original.
- **Drop** everything conceded, in full, including the parts that still read well. Drop any `DEFEND` that produced no evidence the attack had not already answered.
- **Count** what was dropped. The count is part of the deliverable, not bookkeeping.
- **Reconcile.** Every Round 1 finding ends in exactly one place: a bucket in the distillate, or the dropped count. Survivors plus drops must equal the number of findings the bundle carried, per vector. A mismatch is a finding lost or double-counted, not a rounding error — find it before writing the output. (authored)

Synthesizing before Round 3 returns preserves exactly the findings that round was about to kill.

### 5) Distill into four buckets

The product of this step is a distillate, not a plan:

- **Hard constraints** — invariants the plan must respect, each with the vector that surfaced it and why it survived.
- **Decisions** — what the debate converged on, each with its reasoning trail: who proposed, who attacked, on what grounds it was defended or refined. The trail is the point; a decision without one is an assertion.
- **Risks and mitigations** — paired. A risk whose mitigation nobody could name is an open question, not a risk.
- **Open questions** — where the debate did not converge. Each becomes an explicit input gate: dependent work does not start until a human answers it.

### 6) Hand the distillate to a separate author

- Whoever ran the debate does not write the plan. The distillate goes to a separate planning pass — another agent, another session, or at minimum a pass that does not carry the debate — which owns sequencing, dependencies, and per-task verification.
- **Do not pre-draft tasks before handing off.** A draft anchors the planner to it and turns independent planning into editing; this is the named failure mode the separation exists to prevent.
- Hand it over raw, with three carried requirements: every hard constraint is respected, every risk's mitigation lands in the task it belongs to, and every open question becomes a gate before the work that depends on it.

## Decision points

- A vector cannot be staffed → run without it and **state the degraded roster in the output**. A silently short panel produces the same-shaped report with a hole in it.
- The bundle outgrows what a reviewer can hold → summarize finding by finding, preserving each claim and its evidence, and record in the output that reviewers saw a summarized bundle. Never truncate to fit: the tail is then silently unreviewed. (the no-truncation rule is authored)
- A reviewer returns no findings → record zero for that vector. Do not send it back to try harder; a manufactured finding survives Round 2 as easily as a real one, because nobody bothers to attack it. (authored)
- Two vectors independently produce the same finding → keep it once and record the independent arrival. It is the signal a panel produces that one reviewer cannot. (authored)
- Every finding in a bucket was conceded → leave the bucket empty and say so. Back-filling it from pre-filter material re-admits what the protocol just discarded.
- The panel converges on "the proposal holds" → that is a result. Report it with the provenance block; a run that changes nothing ran correctly.

## Output contract

The deliverable is the distillate plus the provenance of the filter that produced it.

```md
# Adversarial review: <proposal>

## Proposal under review
<restated verbatim>

## Hard constraints
- <constraint> — surfaced by <vector>; survived <attack> because <reason>

## Decisions
- <decision> — proposed by <vector>, attacked by <vector> on <grounds>, defended/refined by <evidence>

## Risks and mitigations
- <risk> — <mitigation>, from <the finding it came from>

## Open questions (input gates)
- <question> — <the contention> — blocks: <work that waits on the answer>

## Provenance
- Panel: <vectors run; name any vector that could not be staffed>
- Findings surviving, per vector: <vector>: <n>
- Findings dropped as conceded or undefended: <n>
- Bundle summarized before forwarding: <yes/no>
```

The dropped count belongs in the output because six constraints read differently as the residue of forty findings than as forty findings reworded.

## Examples

One finding, traced through the protocol:

- **Round 1 (Evidence)** — "3. The plan assumes the retry wrapper is idempotent. No caller was checked: `queue/worker.py:112` retries a handler that writes before it validates."
- **Round 2 (Subtraction)** — "ATTACK: idempotence is not this plan's problem. Delete the wrapper and let the queue redeliver."
- **Round 2 (Blast radius)** — "STANDS — redelivery without idempotence is the same defect one layer down, and the worker's own tests do not cover the write-then-validate order."
- **Round 3 (Evidence)** — "REFINE: whether the wrapper exists is out of scope; the finding is that any retry path, wrapper or queue, needs validate-before-write fixed at that call site first."
- **Filter** — refined, so kept in its refined wording. **Bucket** — hard constraint: "validate before write on every retry path".

Round 1 shape, wrong beside right:

- Weak — "There may be idempotency concerns around retries." Survives nothing: nothing to attack, nothing to defend, and it distills into a risk with no mitigation.
- Strong — the finding above: one claim, a named call site, and an explicit statement of what was checked and what was not.

## Common pitfalls

| Pitfall | Why it defeats the protocol |
| --- | --- |
| Dropping a round to save time | The rounds are the filter. One pass of mixed critique is the default behavior this replaces. |
| Softening the briefs into a request for feedback | Adversarial pressure is the mechanism; politeness returns hedges. |
| Synthesizing before Round 3 returns | Preserves precisely the findings Round 3 was about to kill. |
| Carrying conceded material because it still reads well | Conceded means defeated. The distillate holds survivors only. |
| Broadcasting the full Round 2 bundle into Round 3 | Removes the input asymmetry; defenses converge on each other instead of on evidence. |
| One reviewer holding two vectors | Its findings stop being separable, and the louder vector quietly absorbs the other. |
| Writing the plan in the same pass that distilled it | A distiller holding a draft has already decided; the separation is the point. |
| Treating a vector as needing a particular model tier | Unevidenced in the source, and it constrains who can run the panel for no reason. |

## Provenance

Rewritten from one host-bound implementation of this protocol, with its dispatch layer, session mechanics, and product identities removed. Read off that source: the five vectors and their bounds, the three-round structure with its deliberate input asymmetry, the three-valued per-finding verdict, the survivorship rule, the four-bucket distillation, the provenance block, and the critic/author separation with its named failure mode.

Its numbers are asserted, never measured — panel size, findings per reviewer, sentence caps, and a byte ceiling on the forwarded bundle — and appear here only as qualitative rules or as figures labelled chosen. Its table assigning each role to a named model tier is deliberately not carried: no evidence was offered for the fit, and the vectors stand on their own. Rules tagged **(authored)** are not from the source.

## References

- `references/panel-roles.md`
