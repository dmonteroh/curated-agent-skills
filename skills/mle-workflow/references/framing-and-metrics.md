# Framing, metrics, and hypotheses

Read this when the prediction target, the metric, or the candidate signals are still open. Once they are settled, the delivery workflow takes over.

## Framing an ambiguous decision

Work this before a metric is chosen. Its purpose is to stop a project from optimizing a number nobody trusts.

1. **Start from the decision, not the model.** Name the action that changes downstream behavior when the output changes. If no action changes, there is no model to build.
2. **Name who cares, and why.** Different parties pay different costs for false positives, false negatives, latency, compute spend, opacity, and missed opportunities. The metric follows from whose cost dominates.
3. **Convert ambiguity into hypotheses.** What signal would separate the outcomes? What evidence would disprove that? What simple baseline should be hard to beat?
4. **Look for prior art or a nearby known problem** before inventing a bespoke formulation.
5. **Consider the adversarial case:** incentives to game the output, selective disclosure by the parties supplying data, distribution shift, and feedback loops where today's predictions shape tomorrow's training data.
6. **Prefer the simplest change that reduces the most important mistake.** Simplicity here is not modesty; it is the shortest path to finding out whether the framing was right.
7. **Record the decision, the evidence, the strongest counterargument, and the next reversible step.**

The source for this loop included a scoring step that multiplied a two-element tuple of probability and confidence by a four-element tuple of cost, severity, importance, and impact. It defined no operation for that product, so it cannot be computed and is not carried here.

## Choosing metrics from failure costs

Choose from the cost of being wrong, not from habit.

- Build a confusion matrix early, so the discussion is about concrete false positives and false negatives rather than about abstract accuracy.
- Favor precision when an incorrect positive decision is the expensive one.
- Favor recall when a missed positive is the expensive one.
- Use a harmonic mean of the two only when the trade really is balanced and the balance is explainable to whoever owns the decision.
- Use ranking or area-under-curve metrics when ordering quality matters more than any single threshold.
- Treat latency, throughput, memory, and cost as first-class metrics: they decide which model complexity is reachable at all.
- Compare against both a baseline and the current production model before treating an offline gain as real.
- Treat real-world feedback signals as delayed labels carrying lag, bias, and coverage gaps. They are evidence, not ground truth, until that lag and bias have been characterized.

Every metric choice states three things: which mistake it makes cheaper, which mistake it makes more likely, and who absorbs that cost.

## Feature and label hypotheses

Features come from a theory of separation, not from availability.

- Text, categorical fields, numeric histories, graph relationships, recency, frequency, and aggregates are candidate signal *families*, not automatic features.
- For each family, state why it should separate the outcomes, and how it could carry information from after the label.
- For noisy labels, weigh adjudication, an explicit label-confidence field, soft targets, or confidence weighting.
- For class imbalance, compare weighted loss, resampling, threshold movement, and a calibrated decision rule before reaching for a larger model.
- For missing values, decide whether absence is itself informative, imputable, or grounds to abstain.
- For outliers, decide whether to clip, bucket, investigate, or preserve them as rare but important signal.
- For correlated features, establish whether they are redundant, unstable, or proxies for state that will not be available at prediction time.

Do not add model complexity until error analysis shows the baseline failing for a reason that more signal or more capacity could plausibly fix.
