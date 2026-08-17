# Threats to validity

Each entry names a defect observed in the single worked instance this procedure generalizes, what it does to the result, and the guard that closes it. They are recorded together because a paired benchmark fails quietly: every one of these produced a report that looked finished.

No pass rate, delta, or score from that instance is carried here. Its numbers describe one private run against one private codebase and are neither targets nor reference values.

## Unblinded grading

**Observed.** Grading was manual on every assertion. The condition was written into the directory path *and* into a field inside the grading file itself, so the grader was told the answer twice before reading a line of output. No grader identity was recorded, no rubric was stored, and there was no second grader or agreement check.

**Effect.** A grader working toward an expected direction is a first-order threat to any positive delta, and it is unbounded: nothing in the artifact set constrains how much of the result it explains. This is the largest single gap between what the instance claimed and what it evidenced.

**Guard.** Opaque run ids; the condition absent from every path segment, filename, and record field; the mapping in a separate file opened only after grading closes; grading order shuffled. Verify by searching the records, their filenames, and their paths for the condition tokens — any hit voids the pass. Where the delta is small relative to the checklist size, a blind re-grade of a shuffled sample is the cheapest available defense.

**Residual.** Blinding removes the label, not every cue. With-skill output may carry the skill's own vocabulary, and a grader familiar with the skill can often tell. State that residual in the report rather than claiming full blinding.

Where the arm variable is the agent, the residual is larger: formatting habits, phrasing, and tool-call style identify an agent about as reliably as a label would, and a grader who recognizes one arm is unblinded on every eval at once rather than on the few where vocabulary leaked. Blinding is still worth doing — it removes the cheapest cue — but report how much of it plausibly survived instead of reporting that it held. (authored)

## One run per cell

**Observed.** Every cell was a single run. No repeats, no resampling record, no variance estimate across runs of the same cell.

**Effect.** At one sample per cell, a single assertion flipping moves the headline by one over the total assertion count — in that instance, the same magnitude as an arithmetic error found in its own rollup. There is no way to distinguish a real effect from run-to-run variation.

**Guard.** Record the repeat count in the run configuration and report the delta as an estimate from that many samples. No repeat count is established as sufficient; whichever is chosen is a chosen budget and is labelled as one. Where only one run per cell is affordable, say so in the limitations rather than reporting the delta as a measurement.

**Second guard, once repeats exist.** Repeats bought without an agreement figure are half-spent: report how many of each cell's repeats passed each assertion, and bucket a split assertion as unstable rather than as its majority (`record-shapes.md`). A mean over a split cell hides exactly what the repeats were bought to expose — that the cell disagrees with itself — and reads identically to a cell where every repeat agreed. (authored)

## Nothing recorded about the run

**Observed.** No model identifier, model version, temperature, seed, top-p, runner version, skill version, skill content hash, or per-run timestamp appeared anywhere in the artifact set. The claim that the arms were identical apart from the skill was asserted, never evidenced.

**Effect.** The result cannot be reproduced, cannot be compared with a later iteration, and cannot be defended against the obvious question of what else differed.

**Guard.** The configuration record described in `record-shapes.md`, written before the first run, with every field present or explicitly marked not recorded.

## The control arm was never defined

**Observed.** Nothing stated what "without the skill" meant operationally — whether the file was removed, loading was suppressed, or a fresh session was used.

**Effect.** Three different experiments share one label. A control that merely omits a mention differs from one that starts a clean session, and the two produce different baselines.

**Guard.** One sentence in the run configuration defining the control arm, written before the run and reported with the result.

## Grading records that cannot be joined to the spec

**Observed.** The grading record stored assertion text and dropped the assertion id, so alignment to the spec was positional only. The stored text was also a truncated paraphrase: parentheticals and qualifying clauses were dropped, and more than a third of the assertion texts no longer matched the spec by string.

**Effect.** No rollup can be computed mechanically. The clauses that go missing first — the negative clause closing the cheap pass, the named value, the count — are precisely the discriminating parts, so a text join fails on the rows carrying the signal.

**Guard.** Store the `id` and let the text live in the snapshot. Check that the id set in each grading record equals its snapshot's id set exactly, and void the join on any mismatch rather than dropping rows.

## The discrimination split done by eye

**Observed.** The keep-or-prune analysis existed only as prose in two places. No structured per-assertion cross-arm record existed anywhere, and the schema actively prevented building one. The prose named a few non-discriminating assertions; an exhaustive recomputation from the underlying records found several times that many.

**Effect.** The step with the most downstream value — deciding which assertions to retire — ran on memory. Assertions that measure baseline competence survive into the next iteration, inflating its score and masking regressions.

**Guard.** Compute the split from the records, partition every id into exactly one bucket, and check that the bucket sizes sum to the assertion count.

## A hand-transcribed rollup

**Observed.** One control cell was published with one fewer pass than its own grading record contained, while the same rollup's list of failed assertions for that cell contradicted the count it had just stated. The wrong figure then appeared in all three derived artifacts — machine record, human table, and review page — because all three were rendered from one hand-written intermediate rather than from the grading records.

**Effect.** The headline delta was overstated. Three artifacts agreeing with each other read as corroboration and were in fact one unverified source repeated.

**Guard.** Recompute every published number from the grading records in the same pass that renders the report, and run the cell-arithmetic check: passed plus the number of failed ids equals the total. That check alone would have caught it.

## A review surface showing one arm

**Observed.** The generated review page rendered the with-skill per-assertion grades in full and an empty list for the control arm in every eval. The control records existed on disk; the generator simply did not load them, and the page gave no sign.

**Effect.** The artifact a reviewer actually opens showed a complete-looking per-assertion breakdown for one condition. A reviewer using it could not audit the control arm at all, and had no way to notice the rollup error above.

**Guard.** The review surface loads both arms' grading records and renders their evidence side by side, keyed by assertion id. A paired benchmark whose viewer shows one arm is not a paired benchmark.

## Plans graded as though they were behavior

**Observed.** Both arms emitted proposal documents — plans describing commands the agent intended to run. Nothing was executed; no real change, review, or pipeline identifier appeared in any output. The assertion wording was honest about this ("the plan uses…"), but the spec's expected-output sentence claimed the agent carried the work through to completion.

**Effect.** The benchmark measured what the agent said it would do. That is a legitimate, cheap, deterministic thing to measure, and it is not what the spec claimed to measure.

**Guard.** Keep the expected-output sentence describing the artifact that is actually graded, and say "plans" in the report. An execution tier is a separate design with its own assertions and its own cost.

## A delta concentrated in unguessable facts

**Observed.** Two assertions carried most of the net gain, and both encoded facts unavailable to the base model — the existence of a proprietary review bot and the name of an internal gate. The control arm produced a competent, thorough verification plan and failed one of them solely for not naming two in-house gates it could not have known about.

**Effect.** The result measured transfer of a private convention far more than improved judgment, which is close to tautological: a file states a fact, and the agent that read the file repeats it. Reported as a headline pass-rate lift, it reads as better reasoning.

**Guard.** Report the concentration of the delta — the share carried by the top assertion and the top two — and score assertions encoding unguessable facts on a separate track from those testing judgment the model could have exercised unaided.

## Unstated statistical choices

**Observed.** The pass rate was weighted per assertion, giving the eval with the longest checklist proportionally more influence over the headline; that eval also had the widest arm gap. The reported standard deviations were population, not sample. Neither choice was stated anywhere and both were recovered by recomputation.

**Effect.** Two defensible choices, invisible to a reader, each moving the headline. Nobody could reproduce or contest a figure whose definition was not given.

**Guard.** Name the weighting rule and the standard-deviation estimator in the rollup record itself.

## Declared fields that were never populated

**Observed.** The token field was null in every timing record, so no cost comparison was possible. The grading-mode field said "manual" on every assertion, including several that were mechanically checkable. The iteration-comparison fields existed in the schema and were empty or false in every case, with only one iteration ever run.

**Effect.** The artifact set advertised capabilities it did not have: a cost comparison, an automated grading axis, and an iteration history. A reader takes a declared field for an exercised one.

**Guard.** Populate a declared field or delete it. Where one stays empty, record why in the same place — a comparison that was never possible should not look like one that came out even.

## Spec drift with no snapshot

**Observed.** The top-level spec and the graded snapshots disagreed for two evals: assertion ids and text had changed after the run. The snapshots matched the grading records, so they governed, but the direction of the drift could not be determined from the artifacts.

**Effect.** Without the per-run snapshot, that iteration's numbers would have been unreadable — nothing would say what a given assertion was counting.

**Guard.** Snapshot the prompt and assertion list into each eval directory at run time, above the arm split, and hash the spec before and after the iteration.
