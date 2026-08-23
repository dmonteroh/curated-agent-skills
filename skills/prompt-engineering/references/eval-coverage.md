# Eval Coverage for LLM-Backed Units

Coverage discipline for a prompt, agent, or tool call that ships to production. Complements `prompt-optimization-workflow.md`: that file is how a prompt gets better; this one is what must exist before it ships and what keeps existing afterwards.

## Two tiers, minimum

Every deployed unit that calls a model carries at least:

- a **gate eval** that blocks merge or release when it fails — it asserts a must-have behavior, not a quality score;
- a **periodic eval** that runs on a schedule and catches drift a gate never sees: a provider-side model update, input distribution shift, or a prompt edit merged somewhere upstream.

One tier is not coverage. A gate alone certifies the unit at merge time and says nothing about it a week later; a periodic run alone lets a regression ship and reports it after the fact.

## One registry, checked by the build

Map each unit to its gate eval and its periodic eval in a single file, and fail the build when a unit has no entry. Per-directory convention and tribal knowledge do not survive a refactor; a missing-entry check turns "nobody wrote the eval" from an eventual discovery into a build failure on the commit that introduced the unit.

## Judgment units: assert structure, not output

Where output is not deterministic — orchestration, routing, review, anything whose product is a judgment — the must-have is **structural compliance**, not exact content. Assert that the unit called the expected interaction in the expected shape, followed the required section order, and persisted the artifact it promised.

Where even a structural assertion is impossible, label that section explicitly: *judgment-dependent, not eval-protected*. The label is a coverage note, not a deletion warrant. Unprotected prose is usually the part carrying the judgment; deleting it because no test covers it removes the behavior instead of testing it.

## Report both error directions, together

Gate the two directions in one decision: a floor on the direction that catches the thing (detection, recall, correct tool use) and a ceiling on the direction that fires wrongly (false positives, overtriggering, needless escalation). Both thresholds are per-task choices — record them as chosen, with the cost that set them.

The one-sided gate is the standard failure. A false-positive ceiling on its own passes a build whose detection rate has collapsed, because a unit that never fires has no false positives.

Alongside pass/fail, report:

- **Confidence intervals on both rates**, not point estimates. A bare point estimate from a small case set invites a chase after noise.
- **Deltas against the previous version in percentage points**, both directions. Percentage points, not percent: "detection −11.1pp, false positives −21.2pp" states a trade a reader can judge; "false positives improved 45%" hides which way the other direction moved.
- **Every knob that produced the number, recorded beside it**: model and version, prompt version, aggregation or voting rule (below), confidence floors, timeouts, retry policy. A result detached from its configuration cannot be reproduced or compared against the next one.

### Establishing both rates when the grader is a model

The gate above presumes the two rates are known. A model judge does not arrive with them: its verdicts are an estimate of the criterion, with an error rate in each direction that nobody has measured. Calibrate it before its verdicts gate anything or enter a published number.

1. **Hand-label against the rubric that defined the criterion.** Collect human labels for the criterion this judge will grade, using the same rubric — or labelers tight enough to be interchangeable — that defined it in the first place. A judge calibrated against a different notion of "pass" than the one the eval was built on diverges from what the eval measures, and does it silently. Chosen floor: at least 100 labelled items, a starting size rather than a measured sufficiency.
2. **Split three ways and seal the last.** Few-shot examples for the judge prompt, an iteration set for fixing that prompt, and a sealed test set reported once. Chosen proportions, not derived: roughly 20-30 / 30-40 / 30-40. Sealed means sealed — if an iteration cycle moves the reported test-split number, that number has stopped being a generalization estimate, and the repair is a fresh sealed split, never another run against the touched one.
3. **Report the two rates separately, never blended accuracy.** True-positive rate (of the items a human passed, the share the judge passed) and true-negative rate, each on its own line. One accuracy figure hides which direction the judge is biased in, and on a skewed set a judge that says "pass" to everything scores well on it. This is the two-direction rule above applied one level down — to the grader rather than to the unit.
4. **Agree the bar per bucket before running.** Set it by what a false pass and a false fail each cost downstream, and record it as chosen alongside that reasoning. A common starting bar is 0.85 on both rates; it is a starting point, not a measured threshold, and tightening it per criterion is expected.
5. **Pin the judge, and record the pin beside the rates.** A fixed model snapshot, never a moving "latest" alias. The rates describe the judge that produced them, and an alias that moves invalidates them with no visible event.
6. **Use a different model family from the system under test**, on every cycle. A judge grading output from its own family is a biased grader, and that bias is systematic rather than random, so the correction below cannot remove it.

**Bias-correct the published rate.** A judge with unequal error rates does not report the unit's pass rate; it reports one skewed by its own asymmetry. Recover the estimate with the standard correction — the Rogan-Gladen estimator, not a constant chosen here:

```
corrected = (observed pass rate + TNR - 1) / (TPR + TNR - 1)
```

A near-zero denominator means the judge is near chance, and the correction then amplifies noise instead of removing bias. That is the signal to rewrite the judge prompt, not to divide by it.

**Recalibrate** on any change to the pinned judge, intentional or forced by a deprecation, *and* on a schedule regardless of change: what a hard case looks like drifts as the unit under test improves. Recalibration reruns the whole protocol, not the sealed split alone.

**A judge that misses the bar ships advisory-only.** Its verdicts surface for a human to read; they gate nothing and count toward no reported rate. Do not lower the bar to make it pass — that is the single move that makes calibrating pointless. Where the criterion can be reframed as a deterministic check, prefer that over a permanently advisory judge.

Two rules about the judge prompt itself:

- **Few-shot anchors are mandatory.** A judge prompt carrying no worked pass and fail examples drifts toward the model's own prior instead of the labelled criterion, which is what the calibration set exists to pin down.
- **An unparseable verdict is an operational failure, not a FAIL.** Retry the call or route the item to human review; never coerce it to negative. Coercion inflates the true-negative rate and corrupts the exact metric the separate-rates rule exists to establish.

**Say so when nothing routes to a model judge.** "Judge calibration: N/A — every graded criterion is deterministic" is a coverage statement; a blank is indistinguishable from a question nobody asked. Do not invent a subjective criterion just to have something to calibrate.

## Aggregation rules: sampling and voting

The knob list above requires an aggregation or voting rule beside every result, which presumes one exists. The usual one is **self-consistency**: where a single call is measurably not reliable enough and the task has a discrete, checkable final answer, run the same prompt n times at a non-zero temperature, extract the final answer from each sample, and take the majority. Report the winning answer's **vote share** as the confidence signal and keep the dissenting samples — unanimity and a bare majority are different results that one call cannot tell apart.

Reach for it only when all three hold: the answer is discrete enough to compare across samples, one call has been *shown* insufficient rather than assumed to be, and n× latency and spend are acceptable. Cost is linear in n and the benefit is task-dependent.

- n and the sampling temperature are caller choices set against that cost multiplier; this file states no default for either.
- Fix the answer-extraction rule and the tie-breaking rule before running, and record both as knobs. A vote taken over loosely extracted answers counts formatting variants as disagreement.
- Vote share is an **agreement** measure, not a calibrated probability. Recording it as a confidence knob is fine; reporting it as "the answer is 80% likely to be correct" is not.
- This is orchestration around the call, not scaffolding inside the prompt, so it applies to reasoning models as readily as to classic ones — the returns are usually smaller there, since the model already explores paths internally.
- It changes the unit under evaluation. Evaluate the voted result, not one sample, and record n and the voting rule with the number; a later run at a different n is otherwise not comparable.

## Cap the tuning, visibly

Carry a tuning-round counter in the result record — how many rounds of knob-twiddling produced this number. Pick its ceiling before tuning starts and label it a chosen budget; it is a spending limit, not a measured optimum. What the counter reliably does is keep the round count in the record instead of in someone's memory; that a ceiling also prevents overfitting to the benchmark is a plausible purpose, not a demonstrated one.

The hold-out set in `prompt-optimization-workflow.md` is the check that pairs with it: rounds spent against the visible cases are exactly what a hold-out exists to catch.

## Split the expensive run from the cheap check

Measurement and regression-guarding are different jobs:

- the **live run** — real model calls across the full case set — is slow and costs money, so it stays a deliberate, scheduled act;
- the **CI replay** — a deterministic replay of the recorded result — runs on every build in a fraction of a second and fails when the recorded shape or gate outcome changes.

The trade is explicit: a replay proves the recorded result is intact, never that live behavior still matches it. So the live run needs a schedule, not an invitation — otherwise CI stays green on a measurement nobody has refreshed in months.

## Result record shape

```json
{
  "unit": "<name>", "prompt_version": "<id>", "model": "<model@version>",
  "gate": {"detection_floor": "<chosen>", "fp_ceiling": "<chosen>", "passed": true},
  "detection_rate": 0.56, "detection_ci_95": [0.50, 0.62],
  "fp_rate": 0.23, "fp_ci_95": [0.18, 0.29],
  "delta_detection_pp": -11.1, "delta_fp_pp": -21.2,
  "knobs": {"voting_rule": "...", "confidence_floor": "...", "timeout_ms": "..."},
  "judge": {"model": "<model@snapshot>", "family_differs_from_unit": true, "tpr": 0.91, "tnr": 0.88,
            "bar": "<chosen, with the cost that set it>", "calibrated_at": "<date>", "gating": true},
  "tuning_rounds": 0,
  "methodology": {"live_run_at": "<timestamp>", "ci_mode": "replay"}
}
```

The `judge` block travels with the rates it produced, so a later reader can tell which judge said this and whether it was entitled to gate. Where no criterion routes to a model judge, the field says so rather than disappearing.

The rates and deltas above illustrate the shape of a record. They are not reference values, and no threshold in this file is a default to copy — each one is set by what an error in that direction costs the task at hand.
