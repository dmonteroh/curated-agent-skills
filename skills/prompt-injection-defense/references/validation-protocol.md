# Adversarial validation protocol

## Harness shape

1. Run every case of an adversarial corpus through the full detector stack, not through one layer in isolation.
2. Report detection rate **per attack type**, false-positive rate, bypass rate **per injection strategy**, and latency percentiles.
3. Fail the build against a gate declared before the run.
4. Expose the same harness as an operator-runnable command, not only as a CI job. A defense that can only be evaluated by the build system is not one an engineer will re-run while changing it.

Per-strategy reporting is the point of the whole exercise. An aggregate detection rate is fully compatible with one evasion family passing every single time, and the aggregate is what hides it.

## Corpus and hermeticity

The source evaluated against a public adversarial corpus spanning several thousand cases, multiple attack types, injection strategies, distractor types, domains, and linguistic styles. Those counts are properties of that corpus, not targets to reproduce.

Cache the corpus locally and commit the cache or its checksum. Fetching it at test time makes an outside host a build dependency — an explicit finding from the source's own engineering review.

## Two-speed methodology

From the source's first-party evaluation artifact, and more useful than the design document's protocol: split the harness into a live run against real models, behind an explicit flag, and a deterministic replay of recorded responses that runs on every commit. In the source these differed by roughly four orders of magnitude in wall-clock time.

The replay path is what makes a per-commit gate enforceable at all. The live path is what keeps the recordings honest, and needs its own cadence — a replay corpus that is never re-recorded certifies the behavior of a model version nobody is running any more.

## Provenance case study — why the gate is declared in advance

The figures below are from the source material (design document March 2026, evaluation artifact April 2026). **None of them is a target for anything built from this skill.** They are recorded because the gap between them is the argument for the rule.

- The design document declared a gate of 90% detection and 5% false positives in its red-team section — and, about 195 lines earlier in the same document, a different target of >95% detection and <1% false positives against the same dataset. Two incompatible gates, unreconciled, in one file.
- The first-party evaluation artifact, dated 25 days later, measured the shipped classifier ensemble on a 500-case split (260 attack, 240 benign) at **56.2% detection and 22.9% false positives** — 114 of 260 attacks missed, 55 of 240 benign inputs flagged. It was recorded as **passing**, against a gate of 55% and 25%. The system passed because the bar moved.
- Between two tuning revisions the same system traded 11.1 points of detection for 21.2 points of false-positive reduction: an explicit choice to catch fewer attacks in exchange for interrupting the user less. That is a defensible engineering decision and it belongs in the report as a decision. An aggregate score hides it.

Detection rate is a joint property of a corpus, a classifier, and a threshold — all three deployment choices — so no detection target transfers between deployments. Cite these numbers only as evidence for the rule they support: a competently built LLM guardrail measured a 43.8% miss rate against a public corpus, which is why an LLM guardrail is never the last line of defense. The evidence comes from the team that built the guardrail.

## Attribution of the figure that motivates normalization

The widely repeated result that encoding tricks bypassed a production injection classifier roughly 36% of the time is **Lasso Security's red-team measurement of Perplexity's BrowseSafe classifier** — a third party's test of a third party's model. It is the motivation for normalizing before classifying, and it says nothing about whether normalization works. Do not restate it as a result of any system that adopts this stack.

The same discipline applies to model cards. Accuracy, recall, and precision published by a model's vendor describe the vendor's own evaluation set. They are a reason to shortlist a model, never the deployment's expected performance.

## What does not transfer

- **Vendor and model picks.** The source named three different classifiers for the same product across three documents. Specify the *role* — a fast classifier over incoming spans, a classifier over the session transcript — and let the implementer choose and re-choose.
- **Latency figures.** The source's per-component inference budget was a projection for an implementation that was never built.
- **Threshold constants.** They were tuned against one 500-case split with no derivation recorded. Any deployment reusing them inherits the tuning of a corpus it has never seen.
