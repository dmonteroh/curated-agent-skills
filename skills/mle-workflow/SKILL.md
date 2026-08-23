---
name: mle-workflow
description: "Takes a trained model to production: a prediction contract and a data contract written before model code, a pipeline another engineer can rerun, promotion gates declared before training finishes and failing closed on a missing metric, a serving path with a proven train-serve equivalence test, and drift signals with a rollback artifact once live. Use when a model has to become a system."
metadata:
  category: ai
---

# MLE Workflow

Its unit is a decision the model's output changes — not a metric, and not a notebook.

The procedure exists because the failure modes here are quiet. A random split leaks the future into the test set and the offline number looks excellent. A feature transform is copied into the serving code and drifts from the training one over a quarter. A promotion gate never fires because the metric it gates on was never computed. None of these produce an error; they produce a confident number and a system that is worse than the rule it replaced.

## Use this skill when

- A model — ranking, recommendation, classification, forecasting, retrieval, embedding, anomaly detection — is being planned, reviewed, or hardened for production use.
- Notebook code has to become a training, evaluation, batch-scoring, or online-inference pipeline someone else can run.
- Promotion criteria, offline and online evaluation, experiment tracking, or a rollback path need designing.
- A production failure is being traced to drift, label leakage, stale features, an artifact mismatch, or divergence between training-time and serving-time logic.
- Monitoring, canary rollout, shadow traffic, or post-deploy quality checks are being added to a model that already serves.
- A model refresh or retrain is due and nobody can state what would make the new artifact better than the live one.

## Do not use this skill when

- There is no trained model and no offline evaluation set, and the work is shaping an instruction or an agent's behavior. Writing and testing prompts is its own discipline, and establishing whether an instruction change moved anything at all is a matched-pair measurement problem with its own control-arm design. Neither has a data contract to lock or a promotion gate to fail.
- The open question is which training or fine-tuning method fits the data and compute in hand, or how a preference or instruction dataset should be shaped. Choosing a training recipe sits upstream of delivery. This procedure starts once a candidate artifact exists, or is about to, and asks what must be true before it serves traffic.
- The work is assembling the training corpus itself — sourcing, labeling, adjudicating noisy labels, deduplicating, constructing the held-out sets. Building a dataset is its own discipline. This skill states the contract a dataset has to satisfy to be trusted downstream, and checks that contract against prediction-time availability; it does not govern how the set was built.
- The work is a one-off analysis, a chart, or an exploratory notebook that ships nothing. Contracts, gates, and a rollback plan are overhead against an artifact with no consumer.
- The open question is where the data lives or how it is modeled. Storage-model selection and schema evolution belong to data-layer design; query cost and locking belong to database performance work.
- Monitoring is wanted and there is no model version to slice on. Instrumentation, alert strategy, dashboards, and reliability targets are observability disciplines in their own right. This skill adds model-specific signals on top of an observability stack; it does not supply one.
- The decision rule is hand-written and has no learned parameters. A rules engine has no leakage path through a training set and no promotion gate to fail. It needs review and tests, not this.

## Required inputs

- The decision the model's output changes, and the person or system that owns that decision.
- A baseline to beat: the current production model, or the simplest non-learned rule that addresses the same decision.
- An offline evaluation set, with a stated relationship to production data — how it was held out, from what period, and by whom.
- The label definition, its timestamp, and how long after the event the label actually arrives.
- The serving mode and the latency budget attached to it.
- The cost of each kind of mistake, and who absorbs it.

An input filled in silently becomes a contract nobody agreed to, and it is discovered at rollout.

## Workflow

### 0. Justify the model before writing it

State the simplest non-learned rule that would address the same decision — a threshold, a lookup, a sort, a handful of conditions. If that rule would address it, build the rule and stop here. A model is a maintenance commitment with a data dependency, a retraining cadence, and a drift surface; it earns those by beating something.

If the codebase has no model in production today, write and merge the inference boundary before the training loop exists: the service class or endpoint that will hold the prediction, with its fallback behavior and a flag that turns it off. A model that arrives before its boundary gets wired in wherever it is convenient, and the fallback is written after the first incident.

- Check: the non-learned alternative is stated in one sentence and rejected for a named reason. "A model is more accurate" is not a reason until the baseline has been run.
- Output: the baseline decision, and in a greenfield codebase, a merged inference boundary with its fallback and flag.

### 1. Write the prediction contract

Before model code, capture: the prediction target and its decision owner; the input entity; the output schema, including the confidence or calibration field if one is exposed; the latency budget; the serving mode — batch, online, streaming, or hybrid; the fallback when the model or a feature dependency is unavailable; the human review or override path for high-impact decisions; and the privacy, retention, and audit obligations covering inputs, predictions, and labels.

Do not accept "improve the model" as a requirement. Tie the model to an observable product behavior and to a gate that can refuse it.

- Check: the contract names a behavior that visibly changes and a condition under which the model does not ship. A contract with no refusal condition is a description.
- Output: the prediction contract, reviewable by someone who will never read the model code.

### 2. Lock the data contract, then check leakage

Capture: entity grain and primary key; label definition, label timestamp, and label availability delay; feature timestamp, freshness expectation, and point-in-time join rules; the split policy already in force across train, validation, test, and backtest, recorded so the run reproduces and so leakage can be assessed against it; required columns with their allowed nulls, ranges, categories, and units; fields that must not enter training artifacts or logs; and the dataset version or snapshot identifier that makes the run reproducible.

Then check leakage before anything else runs. If a feature is not available at prediction time, or is joined using information that only exists after the label, remove it or move it to an analysis-only path. Leakage is the failure that produces the best offline number in the whole project.

- Check: for every feature, name the timestamp that makes it available strictly before the label. A feature with no answer is leakage until someone proves otherwise.
- Output: the data contract, the snapshot identifier, and a leakage finding per feature family.

### 3. Build a pipeline another engineer can rerun

- Typed configuration — files or frozen dataclasses — for every hyperparameter and path. No values that exist only in a cell.
- Pinned package and model dependencies.
- Seeds set, with any remaining nondeterminism documented rather than ignored.
- Every run records the dataset version, the code revision, a hash of the configuration, the metrics, and the artifact location.
- Preprocessing saved with the model artifact, never separately.
- Training, evaluation, and inference transformations shared, or generated from one source.
- Every step idempotent, so a retry does not corrupt an artifact or double-count a metric.

Prefer immutable values and pure transformation functions; avoid mutating shared frames or global configuration during feature generation.

- Check: a second engineer reproduces a reported metric from the recorded configuration, data version, and seed, on a machine that has never held the original session's state. Until that has happened, the pipeline is untested, not reproducible.
- Output: the run record — configuration, data version, code revision, metrics, artifact location — for every training run.

### 4. Declare promotion gates before training finishes

Gates decided after the numbers arrive are not gates. Declare them as a map from metric name to a direction and a threshold, and make the check fail on a *missing* metric before it evaluates any value — otherwise a metric that was never computed reads as a metric that never failed.

```python
# The three values below are illustrative placeholders, not recommended thresholds.
# Set them from this system's own baseline, cost of error, and latency budget.
PROMOTION_GATES = {
    "auc": ("min", 0.82),
    "calibration_error": ("max", 0.04),
    "p95_latency_ms": ("max", 80),
}


def assert_promotion_ready(metrics: dict[str, float]) -> None:
    """Refuse promotion on absent evidence before comparing any threshold."""
    missing = sorted(name for name in PROMOTION_GATES if name not in metrics)
    if missing:
        raise ValueError(f"promotion blocked, metrics never produced: {missing}")

    failures = {
        name: metrics[name]
        for name, (direction, threshold) in PROMOTION_GATES.items()
        if (direction == "min" and metrics[name] < threshold)
        or (direction == "max" and metrics[name] > threshold)
    }
    if failures:
        raise ValueError(f"promotion blocked, gates failed: {failures}")
```

Alongside the automated gate, the promotion decision needs: comparison against both the baseline and the current production model; guardrail metrics for latency, calibration, cost, fairness slices, and error concentration; slice metrics for the cohorts, regions, devices, languages, or sources that matter; a variance estimate from repeated runs wherever the metric is noisy; human review of failure examples for high-impact models; and explicit thresholds that mean *do not ship*.

Offline metrics are gates, not guarantees. Where the model changes product behavior, plan shadow evaluation, a canary, or a controlled experiment before full rollout.

- Check: delete one gated metric from the metrics record and run the gate. It must refuse. A gate that passes on absent evidence is decoration.
- Output: the gate definition, committed before training finishes, and its result per candidate artifact.

### 5. Package for serving

- The artifact carries its version, its training-data reference, its configuration, and its preprocessing.
- The input schema rejects invalid, stale, and out-of-range features rather than scoring them.
- The output schema carries the model version, and a confidence or explanation field where one is useful.
- The serving path has a timeout, a batching policy, resource limits, and defined fallback behavior.
- Compute requirements are explicit and tested, not inferred from the training machine.
- Prediction logs exclude sensitive fields and still carry enough identifiers to debug a case and to join labels later.
- Integration tests cover missing features, stale features, wrong types, empty batches, and the fallback path.

Never let training-time feature code diverge from serving-time feature code without a test that proves the two are equivalent.

- Check: one test feeds the same raw record through the training transform and the serving transform and asserts the outputs match. Without it, skew between the two is unmonitored no matter how similar the code looks.
- Output: the versioned artifact bundle, the serving contract, and the equivalence test.

### 6. Operate, and be able to roll back

System signals: availability, error rate, timeout rate, queue depth, and latency at the median and the tail.

Quality signals: feature null rate, range drift, categorical drift, and freshness drift; prediction and confidence distribution drift; label arrival health and the delayed quality metrics that depend on it; business guardrails with named rollback triggers; per-version views so a canary and its control can be compared.

Every deployment carries a rollback plan naming the previous artifact, its configuration, its data dependency, and the mechanism that switches traffic.

- Check: the rollback has been exercised at least once — the previous artifact was switched back in a drill, and the time it took was recorded. A rollback that requires retraining is not a rollback.
- Output: the monitored signal set with owners, and an exercised rollback plan.

## The error-analysis loop

Run this after every baseline, training run, threshold change, or configuration change. It is what makes iterations cumulative rather than merely numerous.

1. Split mistakes into false positives, false negatives, abstentions, low-confidence cases, and system failures.
2. Cluster errors by a shared trait: entity type, source, time, region, device, language, sparsity, recency, feature freshness, label source, or model version.
3. Separate model mistakes from data bugs, label ambiguity, product ambiguity, instrumentation gaps, and serving mismatches. These are five different repairs and only one of them is modeling.
4. Route each cluster to exactly one of four moves: better labels, better features, a better threshold or configuration, or a better product fallback. A cluster routed to two moves has not been diagnosed yet.
5. Preserve every important mistake as a regression test, an evaluation slice, a dashboard panel, or a runbook entry.
6. Write the next iteration as a falsifiable experiment, never as "improve the model".

Do not add model complexity until this loop shows the baseline failing for a reason that additional signal or capacity could plausibly fix.

## Common pitfalls

Five failure shapes the workflow above does not catch on its own, each with the tell that gives it away.

- A random split leaks future information into validation and test. The tell is an offline number better than anything the team expected, arriving before anyone has looked at a slice.
- The headline metric improves while an important slice regresses, and only the headline is reported. The aggregate is the one number that can hide the finding that matters.
- Thresholds are tuned repeatedly against the test set. It stops being held out the second time it is consulted, and every number after that is optimistic by an unknown amount.
- Delayed real-world feedback — clicks, dismissals, downstream conversions — is treated as ground truth rather than as labels carrying lag, bias, and coverage gaps. Retraining on it compounds whatever the model already got wrong.
- Monitoring watches availability and nothing about data or prediction quality, so a model returning confident nonsense at full uptime reports green until a human complains.

## Output contract

Every unknown from `Required inputs` is listed as an open item that blocks production readiness. State it rather than filling it with an assumption — an assumption recorded as a finding can be challenged, and one recorded as a fact cannot.

## References

- `references/README.md` — index.
- `references/framing-and-metrics.md` — framing an ambiguous model decision, choosing metrics from failure costs, and the feature and label hypothesis families.
- `references/iteration-artifacts.md` — the iteration compact and the observation ledger, as field templates.
