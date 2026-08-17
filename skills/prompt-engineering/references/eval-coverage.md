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
- **Every knob that produced the number, recorded beside it**: model and version, prompt version, aggregation or voting rule, confidence floors, timeouts, retry policy. A result detached from its configuration cannot be reproduced or compared against the next one.

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
  "tuning_rounds": 0,
  "methodology": {"live_run_at": "<timestamp>", "ci_mode": "replay"}
}
```

The rates and deltas above illustrate the shape of a record. They are not reference values, and no threshold in this file is a default to copy — each one is set by what an error in that direction costs the task at hand.
