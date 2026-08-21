---
name: skill-benchmark-harness
description: "Measures what one change does to agent behavior: each eval prompt runs twice under one arm variable — the skill loaded or absent, or one agent against another — both arms graded blind against one id-stable assertion checklist. Reports the pass-rate delta, which assertions discriminate, and which regressed. Use when the case for a skill or an agent rests on impression rather than measurement."
metadata:
  category: ai
---

# Skill Benchmark Harness

Provides a paired-control procedure for measuring what one change does to agent behavior. The unit of measurement is a matched pair: one task prompt, run twice under a single named **arm variable** — the skill, loaded in one arm and absent in the other, or the agent, with the skill and task set held fixed — both arms emitting the same fixed document set and graded against one shared checklist of falsifiable assertions. The result is the **delta** between arms; the arm carrying the change is the **treatment**, the other the **control**. Vary one or the other, never both in one run: a delta from two moving variables is attributable to neither.

A treatment-arm pass rate is not a result on its own. Without the control arm there is no way to separate what the change contributed from what the base model already did, and a high score reads as success when half the checklist was passing regardless.

## Use this skill when

- A skill has been authored or substantially revised and the case for it rests on reading it rather than on measurement.
- An existing assertion checklist needs pruning, and only a cross-arm comparison shows which assertions carry signal.
- A skill is suspected of having made the agent worse at something it previously handled.
- Two iterations of the same skill need comparing on the same evals.
- A reviewer asks what the skill changes and the honest answer is currently an opinion.
- Two agents or models are candidates for the same task set and the choice rests on reputation.

## Do not use this skill when

- The agent cannot be run without the skill loaded, and the skill is the arm variable. There is no control arm, so nothing the run produces is interpretable — report that gap rather than publishing a one-arm pass rate. (An agent-variable run still has one.)
- The properties in question need holistic judgment ("reads well", "idiomatic"). No falsifiable artifact assertion exists yet and grading collapses into taste; restate the property as a checkable claim first, or leave it unbenchmarked.
- The skill's whole content is facts the base model cannot know — a private tool name, an internal convention, a proprietary gate. The run will confirm the agent read the file, at the cost of a full paired benchmark; one prompt asking for the fact answers it more cheaply. (authored)
- Neither an artifact nor a trace exists to assert against: the run leaves no output document *and* the harness emits no machine-readable record of the calls the agent made. A tool-call trace is itself a durable artifact, so a skill that shapes behavior rather than deliverables is measurable wherever that record can be captured (step 2). Only the absence of both is grounds to stand down.
- The question is which agent is *generally* better, with no task set and no checklist behind it. A paired run reports a delta on one fixed set of prompts and nothing more; a general-capability ranking is a procurement judgment it cannot produce. (authored)

## Required inputs

- The exact skill file or files under test, pinned by name, version, and content hash.
- Where the agent is the arm variable: each arm's binary, version, and model, one named as the baseline, and the task set identical across arms.
- A one-sentence operational definition of the control arm: for a skill arm, what "without the skill" means — file absent, loading suppressed, fresh session, or something else. An undefined control is an undefined experiment.
- Realistic task prompts covering the skill's decision points, varied in register, including at least one off-register request (terse, lowercase, an issue reference and little else) — that one tests whether the skill fires when the user does not write a well-formed request. No prompt count is established; whatever is chosen is a chosen budget, recorded with the run.
- Where the question is whether the skill fires at all, a strictness ladder over one held-constant task: the same task named with the skill, described neutrally, and carrying a competing instruction. Each level is its own eval id, run in both arms (`references/behavioral-compliance.md`).
- The fixed set of output documents both arms must emit, named by role. Where behavior rather than a deliverable is under test, the harness's machine-readable trace of the calls made stands in for that set.
- A grader — human or model — that can be run without being told which arm it is grading.

## Workflow

### 1. Freeze the eval set as data

Write one spec file holding the skill identity and an `evals[]` array, each entry carrying an id, the verbatim prompt, a one-sentence description of what a good run produces, any fixture inputs, and the assertion list. Prose specs drift; a data spec can be hashed, snapshotted, and joined.

Keep that one-sentence description true to the artifact that will actually be graded. A spec claiming the agent shipped and merged a change, where the graded artifact is a proposal document, has silently changed what the benchmark measures.

- Check: hash the spec before the first run and after the last. A changed hash mid-iteration voids the iteration.
- Output: one spec file, unmodified for the run's duration.

### 2. Write assertions as falsifiable claims about a named artifact or trace event

Each assertion names a concrete, checkable property of a specific output document. Where a cheap pass exists, close it with an explicit negative clause. Where a count settles it, state the count.

Wrong — unfalsifiable, and it grades the grader:

> Follows good branching hygiene. Verifies the change properly.

Right — checkable against a named document, cheap pass closed:

> `worktree-isolation` — The execution plan uses a git worktree in a sibling directory, not the main working directory.
> `multi-commit` — The plan uses 2 or more commits for the multi-file change.

Identity is two-level: a per-eval `id` that joins the two arms, and a `concept` shared by assertions testing the same property across different evals. Without the concept, a rollup either double-counts one property under several names or needs a hand-merge, and a hand-merge is not a computation. (authored)

Tag each assertion with how it will be graded, automated or manual, and prefer automated wherever the property is string- or count-checkable. A field that always says "manual" is a declared axis nobody used.

Assertions come in two classes. An **artifact assertion** names a property of an output document, as above. A **trace assertion** names a behavioral step the run should contain — an entry in the harness's record of the calls the agent made — with its own stable id, a required flag, and any ordering constraint against another step. It is what makes a skill with no deliverable measurable at all. Classifying events against step meaning is grading and inherits step 6's rules; ordering is then checked deterministically against the recorded timestamps. Shapes and the two-pass grading: `references/behavioral-compliance.md`.

- Check: every assertion can be judged by pointing at a passage in a named document, or at an event in the trace. One that cannot is a judgment, not an assertion.
- Output: the assertion list inside the spec, each entry with `id`, `concept`, `text`, class, and grading mode.

### 3. Record the run configuration before the first run

"Identical in every respect except the arm variable" is worth nothing when nothing was recorded. Write a configuration record covering at minimum: the agent's model and version, per arm where the agent is what varies; sampling parameters (temperature, top-p, seed) or an explicit note that provider defaults were used unpinned; the runner version; the skill's name, version, and content hash; the grader's identity, with model and version if a model grades; the control-arm definition; the repeat count per cell; and a timestamp per run. (authored)

- Check: every field is present or explicitly marked "not recorded". A blank is indistinguishable from a default and makes the run unreproducible.
- Output: one configuration record per iteration.

### 4. Lay the workspace out so shared material sits above the arm split

Anything that must be identical across arms is stored once, above the arm boundary, which makes divergence structurally impossible rather than merely discouraged. Keep the workspace outside any agent's own skills or configuration tree, so the benchmark never becomes part of the context it measures.

```
<benchmark-workspace>/
  spec.json                    # skill identity + evals[]; frozen before the first run
  iteration-<n>/
    run-config.json            # step 3
    arm-map.json               # opaque run id -> condition; the grader never opens this
    eval-<k>/
      eval-snapshot.json       # prompt + assertions, copied from spec.json at run time
      <run-id>/                # opaque id, carries no condition token
        outputs/               # the fixed document set, same names in every run
        grading.json
        run-meta.json          # duration, tokens, repeat index
    rollup.json                # recomputed from grading.json, never transcribed
    rollup.md                  # rendered from rollup.json
```

The per-run snapshot is load-bearing: when the spec later moves, the snapshot is what keeps an old iteration's numbers readable. Field-by-field record shapes: `references/record-shapes.md`.

Pin the state of the material the agent works on, not only the benchmark's own files. The layout above governs the workspace and says nothing about the codebase each run acts against, and two runs over a working tree that moved between them are not a matched pair — nor can either be re-derived against the code it measured. Give every run its own isolated checkout, created fresh from one recorded revision and discarded afterwards, and carry that revision in the run configuration (`references/record-shapes.md`).

- Check: no file inside a run directory contains a prompt or an assertion list. If one does, the arms can be graded against different checklists.
- Check: every run of an eval resolves to the same recorded revision. A checkout taken from a moving branch tip instead of a pinned one leaves the arms incomparable and the iteration unreproducible, and nothing in the outputs shows it happened.
- Output: the tree, with a snapshot per eval matching its spec entry exactly at run time.

### 5. Run both arms

Run each prompt once per condition per repeat, changing only the arm variable — the skill's presence, or which agent runs the prompt. Write every run's outputs under the same fixed document names, so the grader looks in the same places both times and neither arm can win by reshaping its deliverable. Assign each run an opaque id; the condition lives only in the arm map.

- Check: the document set in every run directory is identical — same names, no omissions, no extras.
- Output: populated run directories and one timing record each.

### 6. Grade blind, per assertion, with an evidence quotation

Grade each run against its own eval snapshot, recording for every assertion: the `id`, a pass bit, a quotation from the output that settles it, and which document the quotation came from.

The evidence rule is what makes the run auditable. A pass quotes the passage satisfying the assertion. A failure quotes **what the agent did instead**, which converts a red cell into a next-revision edit:

> Pass — `"Uses ../wt/feat-search as the worktree path"` (execution-plan.md)
> Fail — `"Uses a plain branch checkout; no worktree isolation anywhere in the plan"` (execution-plan.md)
> Not evidence — `"Assertion not met"` / `"Does not use a worktree"` — a restatement, which proves nothing and cannot be re-derived.

Blinding is a requirement, not a nicety: an unblinded grader working toward an expected direction is a first-order threat to any delta it produces. (authored)

- The condition appears in no path segment, no filename, and no field inside the grading record. The arm map is a separate file, opened after grading closes, and grading order is shuffled across evals and arms so position leaks nothing.
- Blinding removes the label, not every cue — with-skill output carries the skill's vocabulary, and an agent's output style identifies it. Report that residual rather than claiming full blinding.
- Check: search every grading record, its filename, and its path for the condition tokens. Any hit voids the grading pass and it is re-run.
- Output: one grading record per run, carrying assertion ids, not paraphrased assertion text.

### 7. Join on id, recompute the rollup, split by discrimination

Join each arm's grading record to the eval snapshot on `id`. Never join on assertion text: paraphrase drops exactly the qualifying clauses — the parentheticals, the named values, the counts — that carry the discrimination, so a text join fails silently on the rows that matter most.

Recompute every number in the report from the grading records. Nothing is transcribed from a note, a draft, or a previous report.

- Check (join): the id set in each grading record equals its snapshot's id set exactly. A mismatch voids the join rather than dropping rows.
- Check (arithmetic): for every cell, passed + number of failed ids equals the total. A cell failing this is a transcription error — the exact shape of error a hand-written rollup produces, and it propagates identically into everything derived from it.
- Check (partition): every assertion id lands in exactly one bucket and the bucket counts sum to the total.

State the weighting rule explicitly. Per-assertion weighting gives an eval with a longer checklist proportionally more influence over the headline; per-eval weighting equalizes them. Either is defensible; an unstated one is not.

Where the eval set uses strictness levels, never average across them. Each level is reported as its own number, per arm. An agent that follows the skill unprompted and then yields when the user explicitly asks for something else behaved correctly at both levels, and a mean over the ladder reports that as a compliance failure; the gaps between levels are the finding, and the mean is what hides them.

Compute each cell's repeat agreement in the same pass — how many repeats passed each assertion — and bucket on the majority; an assertion whose repeats split in either arm buckets as unstable. (authored)

Partition every assertion by its cross-arm outcome, computed from the records:

| Bucket | Condition | Action |
| --- | --- | --- |
| Discriminating | The arms differ, treatment ahead | Keep — it is carrying the signal |
| Non-discriminating | Identical outcome in both arms | Prune or downweight next iteration |
| Regression | Control passed, treatment failed | Keep, and open a revision (step 8) |
| Unstable | Either arm's repeats disagree on it | Report the split; no verdict this iteration |

Non-discriminating assertions measure baseline model competence, not skill value; left in place they inflate every later score and mask real regressions. Expect a first checklist to lose a substantial share this way — in the single instance behind this procedure, about half the graded assertions passed identically in both arms. One observation, not a target.

One exception to the prune: an assertion added to guard a regression the skill previously caused stays even while both arms pass it. Deleting it removes the guard, not the redundancy. (authored)

Report the delta's concentration: the share of the net gain carried by the largest-contributing assertion, and by the top two. A delta that is one assertion in disguise is a different finding from a broad lift, and the aggregate hides which it is. (authored)

- Output: the rollup record and its rendered table, per the output contract.

### 8. Name regressions, report the cost, version the iteration

Any assertion the control arm passed and the treatment arm failed gets its own named section — both arms' evidence quoted, plus a concrete next action: a skill edit, or where agents vary, the condition under which the candidate loses. It is the highest-value row in the report and the one an aggregate score erases. A regression is visible at all only because the paired design supplies a control.

Report the cost side without spin: duration per arm with the estimator named (population or sample standard deviation — they differ, and an unlabelled figure is unusable), token or call counts or an explicit "not recorded", and the spread as well as the mean, since a skill can leave the mean unchanged while widening variance. Where per-eval durations contradict the headline, say so rather than claiming a uniform effect.

Version the run as an iteration, recording the previous iteration's id and rollup location in the new configuration. An iteration field declared but never populated is not iteration support.

Hold prompts back. Repeated iteration against a fixed eval set tunes the skill to that set; keep prompts no iteration has seen and run them before declaring an improvement. (authored)

- Check: every regression id in the rollup appears as its own named section with a proposed next action. A regression mentioned only inside a count is not reported.

## Constraints

- **Sample size.** One run per cell yields no variance estimate, and a single assertion flip moves the headline by one over the total assertion count — often the same magnitude as the effect being claimed. Record the repeat count and report the delta as an estimate from that many samples. No repeat count is established as sufficient; whichever is chosen is a chosen budget, labelled as one. Where only one run per cell is affordable, say so in the limitations rather than reporting the delta as a measurement. Repeats also settle what their count cannot — whether a cell agrees with itself (step 7). (authored)
- **Plans are not behavior.** If the outputs are proposal documents, the report says "plans" and claims stated intent, nothing more. Plan grading is cheap and deterministic; an execution tier is the only one that measures behavior, and it is a separate, more expensive design with its own assertions — the trace class in step 2. State which tier was used.
- **Review surface.** Whatever renders the results shows both arms' per-assertion evidence side by side. A viewer displaying only the treatment arm hides the control and every rollup error with it.
- **Declared fields get populated or removed.** A field that is always null, always the same value, or never read is a claim the artifact does not support.

## Decision points

1. **Is this an assertion?** Checkable against a passage in a named output document, or an event in the run's trace → assertion. Requires judgment → rewrite it or drop it. The assertions sitting closest to judgment are the ones that produce ambiguous regressions.
2. **Automated or manual grading?** String- or count-checkable → automated, always. Everything else → manual, and blind.
3. **Keep, prune, or escalate an assertion?** Branch on the recomputed cross-arm split, per the bucket table in step 7 — never on impression.
4. **Judgment or information transfer?** Check whether the discriminating assertions encode facts the base model could not have known. If they do, the delta measures transfer of a private convention; report it as that, and score those assertions on a separate track from ones testing judgment the model could have exercised unaided. (authored)
5. **Iterate or ship?** Fix the stopping rule before the first run — a target, a cap on iterations, or a cost ceiling, each labelled a chosen budget. Without one, the loop invites tuning a skill against its own eval set indefinitely. (authored)

## Output contract

- Run configuration in full, including the control-arm definition, the repeat count, and the blinding status.
- Per-cell pass counts, with the per-assertion records reachable from them.
- Per-condition pass rates and the delta in percentage points, with the weighting rule named.
- The four-bucket split by assertion id, with counts summing to the checklist size.
- Per-cell repeat agreement, with every split assertion named.
- Concentration of the delta: the share carried by the top assertion and by the top two.
- Every regression as its own named section, with both arms' evidence and a proposed next action.
- Cost side: duration per arm with the estimator named, and token or call counts or an explicit "not recorded".
- Limitations: repeat count, residual blinding cues, and whether the graded artifacts were plans or executed work.

## References

- `references/README.md` — index.
- `references/record-shapes.md` — record shapes, the id join, and the recomputation checks.
- `references/threats-to-validity.md` — the defect catalog behind these rules, each with its symptom and guard.
- `references/behavioral-compliance.md` — the strictness ladder, trace assertions, and the per-level reporting rule, for runs where behavior rather than a deliverable is under test.
