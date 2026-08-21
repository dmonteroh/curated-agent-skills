---
name: finetuning-method-selection
description: "Routes a fine-tuning request by the data shape actually in hand — demonstrations, preference pairs, unpaired feedback, or a checkable pass/fail — then clears that branch's precondition gate before a run is configured. Use when scoping a training effort, or when it is unclear whether training is the right tool at all."
metadata:
  category: ai
---

# Fine-Tuning Method Selection

Provides a routing procedure for training-recipe decisions on a language model. A method picked first and fitted with data afterwards still trains cleanly — on a signal nobody meant to give it.

This procedure carries no hyperparameter values. Rank, learning rate, batch size, epoch count and sampling width are settings, and the routing decision does not depend on any of them.

## Use this skill when

- A request arrives as "fine-tune the model so it…" and nobody has established that training is the right tool.
- Graded examples, scored traces, or reviewer feedback exist and the open question is which training method they actually support.
- A choice is open between preference optimization and reinforcement from a checkable signal for the same task.
- A method has already been proposed and its preconditions have not been checked against the data.
- A finished run produced a model that optimizes something other than the intended target, and the branch choice is back in question.
- A method and size class need sizing against available memory before a run is committed.

## Do not use this skill when

- There is no way to tell whether a run helped: no graded examples, no scored traces, no automatically checkable criterion. Every branch below ends in a gate that reads a measurement, so without one the routing decision cannot be wrong in any detectable way. Building the measuring stick is the prior task.
- The method is already chosen and the open question is what a setting should be. That is framework documentation, and this procedure deliberately holds no such values.
- The work is taking an already-trained model to production — serving contracts, promotion gates, rollback, drift monitoring. Choosing the training recipe is upstream of that pipeline, not part of it.
- The unit being changed is a prompt, an instruction file, or an agent's configuration rather than model weights. None of the branches below apply when the weights do not move.
- The conclusion is already "retrieval, not training" and the question is how to build the retrieval system — corpus selection, chunking, indexing, ranking. This procedure can *return* that verdict; it does not design what comes after it.
- The question is a deployment format, a quantization target, or serving hardware.

## Required inputs

- A statement of the gap in behavior, concrete enough to say what a correct output looks like.
- An inventory of the data actually in hand right now, by shape and count — not the data someone intends to collect.
- How a candidate output is graded today, and by what.
- The memory budget and the size class under consideration.

## Workflow

### 1. Take the off-ramps in order, before reading the data shape

Most requests phrased as "fine-tune this" are answered better somewhere else. Two of the three off-ramps end the routing outright.

- **The gap is facts that change on their own schedule** — prices, inventory, documents, current events. **Routing verdict: this is a retrieval problem, not a training problem. Stop here.** Training bakes in a snapshot, and the snapshot goes stale faster than the source it was taken from. Record the verdict and hand it off; the design of the retrieval system is a separate job and this procedure does not carry it.
- **The wanted behavior is not stable yet** — it is still being figured out, or it changes per request. **Routing verdict: iterate on the prompt, not on the weights. Stop here.** Training locks a behavior in. Locking in one that is still moving buys a rerun of the whole training loop every time it moves.
- **The gap is stable, dense domain knowledge** that no demonstration set can express and retrieval cannot cover, and a large domain corpus exists. Continued pretraining runs ahead of supervised training rather than instead of it. It runs at a learning rate roughly an order of magnitude below the one that produced the base model — a chosen default in every source consulted, not a measured optimum. Volume thresholds circulate for this decision in bytes of raw text; they are unsourced, tied to neither token count nor model size, and are not reproduced here. Decide it on whether retrieval has already been tried and failed to cover the gap.

- Check: each off-ramp is answered yes or no with the evidence that settled it. An unanswered off-ramp is an open routing decision, not a default to training.
- Output: the off-ramp record — which were checked, which were rejected, and why.

### 2. Let the data shape select the branch

Inventory what exists and read the branch off it. The ordering is the rule and it only runs one way. Choosing a method first and reshaping data to fit is how a pile of unpaired approve/reject clicks becomes a synthesized pair set encoding an ordering nobody ever expressed.

| Data actually in hand | Branch |
| --- | --- |
| Input/output demonstrations of the wanted behavior | Supervised training |
| Two responses to the *same* request, one marked better | Preference optimization |
| Per-response approve/reject with no matched counterpart | The unpaired-feedback preference method — never synthesized pairs |
| An automatically checkable pass/fail: a test suite, a parser, a schema, a ground-truth answer | Reinforcement from verifiable rewards |

Where two shapes are present, the branch is chosen on which one the *gap* is expressed in, not on which pile is larger.

- Check: name the rows that selected the branch. If the answer is a plan to collect data rather than data, the branch is not selected yet.
- Output: the named branch, with its selecting rows.

### 3. Clear the branch's precondition gate

A branch that fails its gate does not open. Each gate below fails in a way that is readable before a run rather than after one.

**Supervised training** has no routing gate beyond the data shape itself — its failure modes live in how the rows are built, not in the routing. Recording that explicitly keeps a missing gate from reading as an unchecked one. (authored)

**Preference optimization** — the pair gate. A pair is two attempts at the *same* task. A set assembled from the best output of one task and the worst of another encodes a preference between tasks rather than between responses, and it is not preference data yet. Also: this pass runs at a learning rate *below* the one that produced the supervised checkpoint it aligns. Carrying the supervised-stage rate forward is the ordinary failure on this branch, not an edge case.

**Reinforcement from verifiable rewards** — two gates, both mandatory, in this order.

1. *Nonzero base success.* Confirm the model already succeeds at the task at least sometimes. Reinforcement sharpens a capability by reweighting toward the samples that already work; it does not install one from zero. If the model never succeeds — low temperature, many samples — the gap is task or format understanding. Route to supervised training and return only once the base success rate is nonzero.
2. *Reward inspection.* Run the checker over a sample of real sampled outputs and read every verdict by hand before anything is configured. Where the checker disagrees with a human reading, fix the checker. Sample size is a budget, not a technique — read as many as can be read carefully in one sitting. This gate exists because an unread reward does not fail loudly: the run optimizes cleanly toward the wrong target, and that never surfaces as a training-loop bug. Tuning settings to compensate for a mis-scoring checker is the same failure with more steps.

If grading the output needs human judgment or a subjective rubric, the signal is not verifiable. That is a grading problem, and it does not become a reinforcement problem by skipping the grader.

- Check: state the gate result and the evidence read. "The gate passed" with nothing quoted from a real output is not a gate result.
- Output: gate results per branch, with the sample that produced them.

### 4. Reach for a variant only after its symptom appears

The base method on each branch is the default. A variant is a response to an observed failure mode, never a pre-selection.

| Observed symptom | Variant class | What it changes |
| --- | --- | --- |
| Entropy collapse, degenerate long reasoning traces | Decoupled-clip variants (DAPO) | Relaxes the regularization that suppresses exploration on long traces |
| Reward or output length trends upward regardless of quality | Length-debiased variants (Dr.GRPO) | Removes the length normalization so reward tracks correctness rather than length |
| Training a mixture-of-experts model | Sequence-level importance sampling (GSPO) | Per-token ratios are unstable under expert routing; here the variant is required rather than optional |

Method-variant choice is low-leverage against data quality and model scale. The corpus behind this rule cites a large study for a specific leverage ratio and reproduces no table, metric, or task set from it, so the figures are not carried here — only the direction, which is well enough attested to act on: spend the decision on the data and the size class, not on a loss-function bake-off. Rankings among variants also invert with scale, so a winner from a small pilot is not a winner at deployment size until it is re-checked there.

- Output: the variant selected with the symptom that triggered it, or "base method, no symptom observed" — which is the expected result on a first run.

### 5. On the preference branch, move the reference forward each round

A single offline pass over a static preference set is a first iteration, not the pipeline. As training proceeds the policy leaves the distribution the pairs were sampled from, and the set goes stale against that drift.

Each round: sample from the current checkpoint, score the samples, run the pass with the *current* checkpoint as the reference, and let the result become both the next round's policy and its reference. Scoring forever against a frozen initial checkpoint is what keeps the signal off-policy.

- Check: the reference used in round *n* is the checkpoint produced by round *n−1*. A configuration still pointing at the initial checkpoint in round two has not iterated.
- Output: the round record — which checkpoint was policy, which was reference, and what scored the samples.

### 6. Size the chosen combination before committing

Total footprint is weights plus optimizer state plus gradients plus activations, and each term depends on the method as well as the parameter count. Describe the model by size class, never by name — a named-model list turns over on the vendors' schedule and is not carried here. Worksheet, dtype tables, and worked size-class examples: `references/memory-feasibility.md`.

- Check: the estimate names the dtype and the method it was computed for. A weight-memory figure reused across methods is wrong by the ratio of their dtypes.
- Output: the sizing estimate, or an explicit "does not fit" that sends the branch back to step 2 with a smaller size class or an adapter method.

## Output contract

A routing record, not a recommendation paragraph. The shape below is authored for this procedure; the sources it draws on define no reporting format. (authored)

- The off-ramp record from step 1, including any verdict that ended the routing.
- The named branch and the rows that selected it.
- Gate results, each with the evidence read.
- Any variant selected, with the symptom that triggered it.
- The sizing estimate, with its dtype and method.
- What would change the answer — the data shape or gate result whose arrival re-opens the decision.

## Examples

- *"Users want the assistant to follow our support macros exactly."* Behavior is stable and demonstrable from transcripts → demonstrations → supervised training.
- *"Reviewers click approve or reject on individual responses; nothing is matched."* Unpaired signal → the unpaired-feedback method. Not synthesized pairs: pairing an approved response with a rejected one from a different request encodes a preference between requests.
- *"The model already solves some of these problems and we can check answers automatically."* Verifiable signal → reinforcement from verifiable rewards, and only after the base success rate is confirmed nonzero and the checker has been read against real outputs.
- *"We want the model to know this week's pricing page."* Volatile facts → routing verdict: retrieval, no training run at all. The record says so and stops.

## Common pitfalls

- Picking the method first, then reshaping the data until it fits.
- Synthesizing preference pairs out of unpaired approve/reject signal.
- Opening a reinforcement run against a model that never succeeds at the task, and reading the flat reward curve as a hyperparameter problem.
- Comparing loss-function variants before checking whether data quality or size class is the actual constraint.
- Carrying the supervised-stage learning rate into the preference pass.
- Treating continued pretraining as the standing answer to "the model does not know our domain".
- Reading a reward function's aggregate score without ever reading its verdicts beside the outputs that produced them.
- Reusing a weight-memory number computed for one dtype when sizing a method that loads weights at another.

## References

- `references/memory-feasibility.md` — the four memory terms, dtype and optimizer tables, adapter overhead, and worked size-class examples.
