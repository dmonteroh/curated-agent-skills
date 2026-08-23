# Generated rows, filtering, and replay mixes

Detail behind the workflow's selection and floor steps: how generated rows are produced, the order filters run in, and how to build the general-domain share of a mix without confounding the next comparison.

No figure in this file is a measurement. Where the sources quote one, it is said so and the rule is stated without it.

## Generation-method ladder

Roughly weakest to strongest for sample efficiency at the same generation budget. Each level composes with the ones above it rather than replacing them — a rejection-sampling pipeline still needs something generating its candidates.

1. **Seed-set bootstrapping.** Have a model paraphrase and extend a small set of hand-written prompts. Cheapest and weakest: diversity plateaus fast and quality tracks the seed set closely.
2. **Iterative complexity rewriting.** Rewrite prompts across generations to add constraints, deepen reasoning, or broaden scope. Better difficulty coverage than plain bootstrapping, still seed-dependent.
3. **Template-prior extraction.** Sample from the target model's own conversation-template prior at the user-turn position, with no seed prompt at all. This removes seed-set bias rather than reducing it, which is why it is a workhorse rather than a niche trick.
4. **Persona conditioning.** Condition prompt generation on a sampled role or persona description to widen style and topic coverage beyond what one unconditioned policy produces.
5. **Rejection sampling.** Generate several candidate responses per prompt and keep only those a filter, checker, or judge accepts. A response-side filter, not a prompt-generation method — it layers onto any of the four above.

**Steering generation at the current model's actual failure modes** beats sampling uniformly, and it layers on top of any level. It requires a live signal about what those failure modes are; without one, generation is untargeted whatever it is called. The sources attach a sample-efficiency multiple to this claim and show no measurement, so the multiple is not carried here — the direction is the usable part.

## Filter funnel

Each stage is cheaper than the next, so each one exists to reduce the volume the next one runs on. **The ordering is the technique; the thresholds are not.**

1. **Exact deduplication.** Normalize whitespace and casing, hash, drop identical rows. Cheapest, so first: it removes generation-loop repeats before anything downstream pays for them.
2. **Near-duplicate removal.** Embed and drop rows too similar to one already kept. Catches paraphrase-level duplicates that exact matching misses. The similarity cut-off is a per-corpus choice; the figures circulating for it have no derivation, so set it by looking at what a few borderline pairs actually are.
3. **Length filter.** Drop candidates below a minimum or above a maximum for the task. Too short is usually degenerate; too long is usually rambling or off-task.
4. **Language check.** Drop candidates that fail a language check against the target language. Generation drifts language on under-specified prompts.
5. **Coarse score cut.** Score what remains and keep the better part, as a cheap quality pass before the expensive stage. The fraction is a budget decision, read off this batch's distribution.
6. **Judge or human check, last.** The most expensive check runs on the smallest remaining set. A row failing here is dropped regardless of how well it did upstream.

**Generate the full candidate set first, then filter it.** Capping generation up front to the size of the wanted output set means the filter has nothing to choose between and the funnel degrades into a pass/fail check. The selection is where the quality comes from; the generation budget only decides how much there is to select from.

Plan raw generation volume against the **end-to-end** yield of the whole funnel, never any single stage's pass rate. The sources quote a typical yield range; none derives it. Budget the first batch from a quoted range if nothing better exists, label that as a chosen budget, and replace it with this pipeline's own measured yield after the first run.

## Distillation as a provenance label

Sampling responses from a stronger model and training a weaker one on them produces an ordinary set in an ordinary shape. Run those responses through the funnel above — a distilled set is a generated set like any other and gets the same deduplication and quality stages — and record in the card which model produced them and under what sampling and prompting configuration. "Distilled" is a provenance fact, not a format.

## Replay-mix construction

A replay mix is the share of general-domain rows carried alongside the target-task rows to protect a capability the target-task data would otherwise erode. Five decisions, in the order they arrive. Record each one in the card: every one of them changes what the mix teaches, and none of them is visible in the finished rows.

**1. Source selection.** Pick a source that is genuinely general for the capability being protected, not a convenient narrow slice.

- *Do not teach to the gate.* If the replay source is drawn from the same distribution as the suite used to check for capability loss, the resulting score partly measures whether the model saw similar items in training. Not automatically disqualifying, but it must be disclosed, and a broader source is the more defensible default when one exists.
- *Match the source to what was actually lost.* Where error analysis shows a specific lost capability, a source targeting it recovers faster than a generic mix — and narrows what "general" means. State in the card which capability the mix targets.

**2. Prompt shape.** Replay rows can take the source's own phrasing (lowest effort, least targeted), the checking suite's exact phrasing (most directly addresses an instruction-following loss, and inflates the score on that specific suite — disclose it), or bare inputs with no instruction wrapper (closest to raw continued-pretraining signal, weakest at restoring instruction-following). Pick on the observed loss signature, not by default.

**3. Answer reformatting.** Decide whether replay reference answers are rewritten toward the target task's output convention or kept as-is. This changes what the model emits on replay-domain prompts, so record the exact transformation applied — or "none, kept source format".

**4. Validation-split treatment.** A task-only validation split keeps the loss directly comparable across runs that differ only in replay fraction, at the cost of no in-loop visibility into replay fit. Adding replay rows to validation buys that visibility and ends the apples-to-apples comparison against a prior run's task-only split. Neither is universally right; state which was chosen, and do not compare validation loss across runs that chose differently without saying so.

**5. Disjointness verification — required.** Before training, verify replay rows do not overlap the reserved evaluation identifiers or the capability-check suite, regardless of the source picked in step 1.

- *Split-level separation.* Draw replay rows only from a source split disjoint from whatever split the check suite draws from.
- *Exact-match text filter.* Normalize and compare replay prompt text against the check suite's items and the reserved evaluation set; drop any hit. Record the overlap count found — expect zero, and record a nonzero count even after dropping it, because it says the source pool needs a tighter split boundary next time.

## Changing a replay fraction between runs: swap, do not add

When a later run moves the replay fraction, implement it by **swapping rows out, not adding rows in**. Adding replay rows on top of the existing set changes the replay fraction *and* the total optimizer steps in one move, and no later change in capability-check score can then be attributed to either variable alone.

**Row count is not token count.** Swapping one-for-one holds the *row* count constant, but replay rows and target-task rows are rarely the same length, so a swap can still move total training tokens — and therefore the step count under a fixed batch size and concatenation scheme — while the row count sits still. Hold total training tokens, or the step count directly, constant between the two runs, and record the packed-token count for each run in the card rather than the row count alone. A run that swapped rows but grew its token count has the same attribution problem as one that added rows outright.
