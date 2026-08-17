---
name: training-data-curation
description: "Turns graded examples and traces into a training set: selects which rows earn a place, holds evaluation items out by identifier at the one seam where that is still possible, shapes rows to the target method, masks loss to response spans, and emits a provenance card that gates the run. Use when building or auditing training data."
metadata:
  category: ai
---

# Training Data Curation

Provides the procedure that turns graded material into rows a training run can consume, and refuses to start one that has not been checked.

**Selection and shaping are one procedure because the holdout can only be enforced between them.** The identifiers that say which items are reserved for evaluation live on the graded records. The training shapes — a message list, a prompt/chosen/rejected triple — carry no identifier at all. So there is exactly one moment, after the rows are selected and before they are reduced to their training shape, when the holdout can be checked. Split that moment across two procedures and it belongs to neither: the evaluation set quietly becomes training data, and every later score against it reads high for a reason nobody can see.

The other rules here guard failures that do not raise. A template applied in the wrong order, a loss mask that covers the prompt, a concatenation bug — all of them train to completion with an ordinary-looking loss curve and surface hours later as unexplained evaluation quality.

## Use this skill when

- Graded traces, scored runs, or reviewer-corrected outputs exist and need to become a training set.
- A training set is being assembled from a mix of collected and generated examples.
- A run is about to start and nobody can say what is in its training data or where the rows came from.
- A checkpoint scores well on the evaluation set and the result is not believed.
- Rows need reshaping for a different training method than the one they were built for.
- An existing training set needs auditing before it is reused.

## Do not use this skill when

- The examples carry no verdict, no score, and no human correction yet. This procedure consumes verdicts; it does not produce them. Grading comes first.
- The corpus is being assembled for retrieval rather than training. Choosing passages to index has different failure modes and no loss mask.
- The open question is which training method to use, or what a training setting should be. Row construction starts after the method is fixed.
- The evaluation set itself is what needs building. This procedure holds that set out; it does not decide what belongs in it.
- The data is already a validated training set with a complete card, and the question is how the run is configured, served, or promoted.

## Required inputs

- Graded records: each carrying a stable source identifier, a verdict, and a score where the task supports one.
- The identifier set reserved for evaluation.
- The target method, and therefore the row shape the trainer expects.
- The exact conversation template identifier that will be used at inference and evaluation time.
- Whatever training data already exists, for deduplication to run against.

## Workflow

### 1. Refuse anything ungraded

A record with no verdict, no score, and no human correction is not convertible. Route it back to grading. Do not hand-label it here to unblock the batch, and do not re-judge it in passing: a conversion step that has to decide whether an output was good is evidence the grading side is missing a grader, not a gap for this step to paper over.

- Check: every candidate carries a verdict, a score, or a correction. Report the ones that do not as **blocked**, with their count, rather than dropping them silently — a dropped row and a blocked row mean different things upstream. (authored)
- Output: the convertible set, and the blocked count with its reason.

### 2. Select rather than accept

Clearing the pass bar is not the same as earning a place.

- **Rank passing rows by score and keep a top fraction**, not everything above threshold. A row that barely passed is a weaker signal than one well clear of it. Tune the fraction against *this* batch's score distribution rather than fixing it across batches — a harder prompt set shifts the whole distribution down, and a fixed fraction then keeps rows that would not have survived an easier one.
- **Human-corrected failures go in directly.** A person already validated the corrected output, so it needs no score threshold. The original failing output never enters the set.
- **Mask bad steps instead of discarding trajectories.** Where a record is a multi-step trajectory and only some steps are bad, mask the loss on those steps and keep the rest. Discarding the whole trajectory throws away every good step in it to remove a few bad ones.
- **For paired data, pair two attempts at the same task.** The higher-scoring attempt is `chosen`. Select `rejected` *above* the score distribution's minimum, not at it: a best-versus-absolute-worst pair is the easiest possible contrast and stops teaching much as scale increases. A common construction targets a point two standard deviations below the mean. That multiple is a chosen starting point with no derivation in any source consulted, and it carries a floor on candidate count that none of them states: no value in a set of *n* can sit more than `√(n−1)` standard deviations below the mean, so with fewer than five attempts per task the target is always under the lowest score and the selection *is* best-versus-worst whatever the formula says. Sample enough attempts per task for the rule to bind, and check that it bound rather than assuming it. (authored: the bound and the check — the sources note the two-candidate case as a curiosity, not as a floor.) Selection code carrying that check: `references/conversion-and-holdout.md`.

- Check: the kept count, the fraction used, and the score distribution it was tuned against are all recorded. A fraction with no distribution beside it is a guess.
- Output: the selected rows, still carrying their identifiers.

### 3. Enforce the holdout, before anything is reshaped

Every identifier reserved for evaluation is held out of every training row, matched by identifier, **while the identifiers are still attached**.

- **Ordering constraint.** Shaping strips the identifier: a message list and a preference triple have nowhere to put one. Once shaping has run, the check has nothing to match against and re-adding identifiers afterwards only tests the copy. Run the holdout filter on the selected rows from step 2, before step 4.
- **Fail loudly.** The filter returns kept and dropped sets, and the dropped set is logged rather than discarded. A large dropped count is a finding, not housekeeping — it usually means the collection step is resampling the evaluation set instead of real traffic.
- **Deduplicate against the training data that already exists**, not only within this batch, and record what the comparison ran against.

- Check: re-join the finished card's per-row provenance against the reserved identifier set and count the intersection. It is zero or the batch is void. This works after shaping precisely because the card kept the link the rows dropped. (authored)
- Output: the held-out identifier set used, the dropped rows with their identifiers, and the intersection count.

### 4. Shape rows to the target method's fields exactly

Field names are copied, not paraphrased — an approximation of the expected shape is a silent no-op or a mis-parse, depending on the trainer. Shapes per method, and the field-level detail: `references/row-shapes.md`.

- Check: compare the field names on a shaped row against the target's expected names character for character, not by reading them as words. `response` where `completion` was expected is not a near miss.
- Output: the shaped rows, and the shape they were built to.

### 5. Apply the template before any concatenation, and mask loss to response spans

- The conversation template goes on **before** any concatenation, never after. Concatenating raw text and templating the result afterwards lands role markers in the wrong place relative to each example.
- Keep the data in message-list shape and let the trainer apply the template and the mask. Pre-rendering conversations into a flat text field destroys the turn boundaries the mask needs — and that path still runs, computing loss over the entire sequence including the prompt and the role markers. It is correct only where full-sequence loss is actually intended, and never for conversational supervised training.
- **The same template identifier used in training is used at inference and at evaluation.** A mismatch degrades output without erroring anywhere.
- **Where rows reference attached media**, confirm the placeholders in the text map one-to-one to the attachments on *every* example. A mismatch raises nothing and produces a run that trains without ever learning from the attachment.

- Check: decode only the unmasked positions of a batch and read them. Expect response text and nothing else. Anything from the prompt or a role marker appearing there means the mask is wrong, and the run would not have told you.
- Output: the decoded unmasked sample, read and recorded as read.

### 6. If concatenating examples, decode a handful and read them before scaling

Batching variable-length examples at a fixed sequence length spends compute on padding, and concatenating several examples into one sequence recovers much of that waste. It also changes what a "step" means.

- Decode several concatenated sequences and read them: example boundaries where expected, each sub-example's markers intact, and the mask still response-only *inside* each concatenated sequence.
- Recompute any schedule keyed to example count. The unit changed, so steps-per-epoch and every milestone derived from it moved with it.

- Check: the inspection happened on real concatenated output before the full run, and the reader can say what they saw. Concatenation bugs are silent — the loss curve looks normal and the damage appears in evaluation quality much later, which is exactly why this is a gate and not a nicety.
- Output: the sequences that were read, and the recomputed schedule milestones.

### 7. Scan for secrets and personal data, and fail closed

Records sourced from production traffic carry credentials, tokens, and customer data. Scan every row, redact what is found, and **drop** any row that still holds sensitive content after redaction rather than shipping it. The failure mode is permanent: a secret trained into weights cannot be revoked from them.

- Check: the scan ran over the final row set, after shaping, not over the pre-conversion records only.
- Output: what the scan found, what redaction fixed, and the count dropped because it could not be fixed.

### 8. Hold a floor of rows this system did not generate for this task

A training set whose share of self-generated rows grows across successive runs degrades, and the guard is a floor of rows that came from somewhere else.

Treat the floor as a decision for this run, recorded with its reasoning. The source corpus states a specific percentage as though it were measured, shows no measurement, and then widens the definition of the protected category until pre-existing rows from any corpus satisfy it — a floor that any set can meet by adding rows from anywhere is not the guard the number claims. So: set the floor deliberately, write the classification rule that decides which rows count toward it, and record both in the card so a later audit can disagree with the rule rather than guess at it. (authored)

Generation-method ladder, filter-funnel ordering, and replay-mix construction — including the rule for changing a replay fraction between runs without confounding the comparison: `references/synthetic-and-replay.md`.

- Check: the card states the floor, the classification rule, and the resulting ratio. A ratio with no rule beside it cannot be re-derived by anyone who did not build the set.
- Output: the floor, the rule, and the count of rows on each side of it.

## Output contract

The dataset's provenance card, and no run starts without it — the card is a gate, not a summary written once training is under way. It carries at minimum:

- **Provenance** — the source run and item identifier for every row. A row with no traceable source is not ready to merge.
- **Counts** — total rows, and rows per split.
- **Holdout** — the reserved identifier set used, the count the filter dropped, and the intersection count from step 3's check. (authored: the sources carry the holdout as a rule but not as a card field, which is how it goes unrecorded.)
- **Generated share** — the ratio, plus the classification rule that decided which rows counted as not-self-generated.
- **Deduplication** — the method, and what it ran against.
- **Template** — the exact identifier, which must match inference and evaluation.
- **Concatenation** — whether it was used, at what sequence length, and confirmation that the decode-and-read inspection happened.

A card missing any field is a dataset that is not ready, not a dataset with incomplete documentation.

## Examples

**Wrong — the identifier is gone before the check runs:**

> Convert every passing trace to `{"messages": [...]}`, write the JSONL, then filter out anything that appears in the evaluation set.

Nothing in the written rows says which trace produced them. The filter can only compare content, so it misses any evaluation item that was reworded, and it passes silently when the shaping step normalized whitespace.

**Right — the check runs while the link still exists:**

> Rank the passing traces, keep the top fraction, filter the kept set against the reserved identifier list and log what it dropped, *then* reduce the survivors to `{"messages": [...]}` and write the provenance card that records each row's source identifier.

## Common pitfalls

- Shaping rows first and holding the evaluation set out afterwards, when there is no longer anything to match on.
- Hand-labelling an ungraded record to unblock a batch, which puts an unverified verdict into the set under the same field name as a graded one.
- Keeping every row that cleared the pass bar and calling that selection.
- Building preference pairs from the best output of one task and the worst of another.
- Pre-rendering conversations to a flat text field, then reporting that loss masking is enabled.
- Applying the template after concatenation.
- Turning on concatenation and leaving a schedule keyed to the old example count.
- Deduplicating within the new batch only, so every earlier batch's rows come back.
- Recording a generated/not-generated ratio without the rule that classified the rows, leaving the number unauditable.
- Treating the card as documentation to write once the run is under way.

## References

- `references/README.md` — index.
- `references/row-shapes.md` — the row shape each method expects, and the flat-text masking trap.
- `references/conversion-and-holdout.md` — graded record to training row, pair selection, top-fraction selection, and the holdout filter with its ordering constraint.
- `references/synthetic-and-replay.md` — generation-method ladder, filter-funnel ordering, and replay-mix construction.
