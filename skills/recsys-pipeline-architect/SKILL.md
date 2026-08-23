---
name: recsys-pipeline-architect
description: "Designs the stages around a scorer for systems that pick the top K items for a subject and context - feeds, recommenders, notification digests, task prioritizers - as an ordered source, hydrate, filter, score, select, side-effect pipeline. Use when structuring or decomposing ranking plumbing, not when changing what a retriever returns."
metadata:
  category: architecture
---
# Recsys Pipeline Architect

Provides a design procedure for systems that must choose the top K items for a (subject, context) pair: enumerate where candidates come from, decide what must be known about each one, drop the ineligible, score the survivors, cut to K, and fire the consequences. Produces a stage-by-stage specification plus a scaffold in the requester's stack. The scoring function itself — the model, the embedding, the prompt — stays the requester's; this is the plumbing around it.

## Use this skill when

- A request amounts to "pick the top K items for this subject, in this context": a feed, a home timeline, a related-items rail, a notification digest, a task or alert priority order, a triage queue
- A scoring function exists and the plumbing around it does not — what feeds it, what it is allowed to see, what it must never be given the chance to return
- An existing ranker is one relevance score and the product now needs several competing objectives balanced at serving time
- A ranking path has grown ad hoc, and eligibility rules, enrichment calls and scoring have entangled into one function that nobody can change safely
- The candidate set is fixed and the open question is what order it goes out in and which members get dropped

## Do not use this skill when

- **The question is what comes back, not what order it goes out in.** Recall work — index and embedding choice, chunking, query rewriting, lexical and vector fusion, pushing predicates down into the query, recall@k — changes the candidate set. This skill never changes the candidate set: it takes candidates as given and decides eligibility, order, and the cut. *(The discriminator is authored for this library, not carried from the source: if the fix is "return different candidates", it is a retrieval question and nothing here helps; if the fix is "keep these candidates and change what survives or what comes first", it is a pipeline question.)* A reranking request sits directly on that line — reranking a retrieved set that is fixed is in scope, making the retrieved set better is not. Answering a recall complaint with a pipeline decomposition hides the fact that no reordering recovers an item that was never retrieved.
- Model or embedding architecture: transformer design, two-tower retrieval models, feature engineering, loss functions, negative sampling, training data. This is plumbing around the model, never the model.
- Training and offline evaluation: label collection, backtests, offline metrics, experiment analysis.
- Operating a pipeline whose shape is already settled: latency regressions, autoscaling, cost, alert thresholds, incident triage. Those are runtime questions about an existing decomposition; this skill decides the decomposition.
- The surface returns everything that matches, in a fixed order the product already dictates (chronological, alphabetical, by explicit user sort). There is no ranking decision to make, and six stages around a `SELECT ... ORDER BY` is overhead.

## Required inputs

- The item type being ranked, and every place items can come from
- What the (subject, context) pair is at request time, and what is known about the subject before the pipeline runs
- K, and whether K is fixed or varies per surface
- The objectives the product is balancing (engagement, safety, freshness, diversity, revenue, contractual obligation to show), and which of them are in tension
- Eligibility rules that are legal or policy-bound rather than product preferences — these become non-tunable filters and must be identified before the filter list is ordered
- Target runtime and language, and whether the scaffold has to fit an existing codebase or stands alone
- The surface's latency budget, if one exists — supplied by the requester, never assumed here

## The six stages

| # | Stage | Job | Concurrency |
| --- | --- | --- | --- |
| 1 | Source | Fetch candidates from one or more origins | Sources run in parallel |
| 2 | Hydrator | Attach the data that filters and scorers need and the sources did not return | Independent hydrators run in parallel |
| 3 | Filter | Remove candidates that must never be shown — ineligible, blocked, expired, duplicate, already served | Sequential; each filter sees fewer items |
| 4 | Scorer | Assign each surviving candidate one or more scores | Sequential; later scorers see earlier scores |
| 5 | Selector | Sort on the final score and cut to K | One operation |
| 6 | SideEffect | Cache served IDs, emit impressions, update counters, log | Asynchronous; never blocks the response |

### Why the boundaries sit where they do

- Sources first: know which candidates exist before paying to enrich any of them.
- Hydration before filtering: most filters need data the source did not return, and a filter that has to fetch its own data is a hydration hiding inside a filter.
- Filtering before scoring: scoring is the expensive stage, and every ineligible candidate that reaches it is budget spent on an item that cannot be shown.
- A scorer chain rather than one scorer: real surfaces compose a predictor, a combiner across objectives, a diversity pass, and business overrides. Collapsing them into one function makes each of those changes a change to all of them.
- Selection after scoring: scoring stays per-candidate, deterministic and cacheable, and the sort and the cut become the only place ordering is decided.
- Side effects last and asynchronous: a cache write or an impression emit that fails must degrade the analytics, never the response.

## Workflow

1. **Clarify in one round, then stop asking.** Three questions: what items, what context is available at request time, what runtime.
   - Output: a problem statement naming subject, context, item type, and K.
2. **Enumerate candidate sources.** Split in-network (owned, followed, subscribed, assigned) from out-of-network (retrieved, trending, similar-to-recent, editorially injected).
   - Output: a source list, each entry naming the fields it returns and its approximate cardinality.
   - Decision: a source is specified by its contract only. If a source's own quality is the problem, that is out of scope — say so and stop rather than restating it as a pipeline change.
3. **Derive hydration from the filter and scorer lists, never from the item model.** Walk every filter and scorer named in the next two steps and list the data it needs that no source returned. That list *is* the hydration stage.
   - Output: hydration list, each entry naming its consuming stage and whether it batches across candidates.
   - Decision: a hydration with no named consumer does not enter the pipeline. Fetching a field because it may be useful charges every candidate for something nothing reads.
4. **Order the filters cheap before expensive, universal before subject-specific.**
   - Output: an ordered filter list, each entry carrying its cost class (in-memory, cached lookup, remote call) and its kind (policy or preference).
   - Decision: policy filters are marked non-tunable and are never merged into a scorer as a large negative weight — a weight can be outvoted, a filter cannot.
5. **Design the scorer as a chain.** Primary predictor, then the combiner across objectives, then diversity and de-duplication, then business overrides.
   - Output: per stage, its inputs, its output range, and whether it may reorder candidates or only rescale them.
6. **Specify the selector.** Sort descending on the final score, cut to K, state the tie-break.
   - Output: selector spec including any stratification (a floor on out-of-network items, a cap per author) and the tie-break rule.
   - Decision: a random tie-break is the one deliberate non-determinism in the pipeline. Either make it stable on a candidate identifier, or state that it is random and why.
7. **List the side effects and show they cannot block.**
   - Output: side-effect list, each entry naming its trigger point relative to the committed response, its failure behavior (dropped, retried, queued), and what breaks if it never runs.

## Decision points

Three trade-offs are decided in every pipeline of this shape. Each has a default here; the default is announced to the requester with its consequence, never applied silently.

**Single score, or multi-action with serving weights.** A single score means one model predicts relevance, and changing what the surface promotes means retraining. Multi-action means predicting a probability per action — read, dwell, like, share, skip, hide, report — and combining them with weights at serving time, negative weights included, so changing what the surface promotes means changing configuration.

- Decision: choose multi-action when the product will want to retune more often than it can retrain, or when the objectives are in genuine tension. Choose a single score when there is one objective and one owner. State the consequence in those exact terms — **retrain versus reweight** — because that is the fact the requester is actually choosing between.

**Isolated or joint candidate scoring.** Isolated scores each candidate on its own: deterministic, cacheable, and it composes with the later chain stages. Joint lets candidates attend to each other in one pass: more expressive, and its output depends on which other candidates happened to share the batch.

- Decision: default to isolated. Choose joint only for an effect that cannot be expressed as a later reranking stage. Batch-aware diversity usually can be, and should be.

**Request-time or precomputed.** Request-time runs the pipeline per request: freshest, and bounded by the surface's latency budget. Precomputed runs it on a schedule and serves cached results: cheapest per request, stale by the interval. Hybrid precomputes candidate generation and keeps scoring and selection at request time.

- Decision: default to request-time, and move a stage offline only against a latency budget the requester supplied. No latency figure is stated here on purpose — the budget belongs to the surface, and a number invented in this file would be exactly the fabricated benchmark that Constraint 1 forbids.

## Constraints

1. Do not invent benchmark numbers. "How much faster is this?" is answered "it depends on the workload — measure it on yours". This binds for latency, throughput, and quality lift alike, and it binds on figures presented as ranges or as rules of thumb.
2. Filter order is part of the specification, not an implementation detail left to whoever writes the code.
3. Side effects never block the response, in any stack. The specification names the mechanism that guarantees it.
4. Every trade-off under Decision points is surfaced with its default and its consequence. A silently applied default is indistinguishable from a decision the requester made.
5. The scaffold runs. Pseudocode presented as code fails this. When the target stack cannot be exercised in the current environment, the scaffold ships with the exact command that exercises it plus an explicit statement that it has not been run — never an implied green result.
6. A stage never reaches around its neighbours: a filter does not fetch, a scorer does not filter, the selector does not score. A stage that needs data it was not handed is a missing hydration, and the fix belongs in stage 2.
7. Name the artifact for what it does — candidate pipeline, feed pipeline, ranking pipeline. Never name it after the product the decomposition is credited to, and keep that product's branding out of identifiers, module names, and documentation. The pattern is free to reuse; a product name is not.

## Output contract

Two artifacts, in this order.

**1. The pipeline specification.**

```md
# <name> pipeline
- Subject / context / item type / K:
- Sources: <name - fields returned - approximate cardinality>
- Hydrations: <field - consuming stage - batchable?>
- Filters (ordered): <name - cost class - policy | preference>
- Scorers (chained): <name - inputs - output range - may reorder?>
- Selector: <sort key - K - stratification - tie-break>
- Side effects: <name - fires after - failure behavior>
- Trade-offs surfaced: single vs multi-action / isolated vs joint / request-time vs precomputed - chosen, and the consequence stated
- Out of scope: <what this pipeline does not decide - candidate quality included>
```

**2. The scaffold**, in the requester's stack: one interface per stage, a runner composing them in the six-stage order, at least one working implementation per interface, and a test per stage boundary. Report the command that exercised it and its result. A scaffold that has not been run is reported as not run.

## Examples

**Wrong** — "Retrieve candidates with a vector search, score them with the ranking model, sort, return 20." One stage boundary and no hydration step, so filtering has nowhere to live: blocked authors and already-seen items reach the scorer and consume its budget, and the eligibility rules end up scattered inside the scoring function where no reviewer can audit them.

**Right** —

- Sources: followed-authors (~400), out-of-network retrieval (~600), trending (~50)
- Hydrations: author block state (consumer: filter 4, batchable), item age (filter 3), engagement counters (scorer 1)
- Filters: self-authored → already-served → older than the surface's freshness window → blocked or muted author → policy ineligibility. The free in-memory checks cut the set before the block lookup, which is a cached remote call. Policy ineligibility is marked non-tunable.
- Scorers: multi-action predictor → weighted combiner, weights held as configuration rather than code → per-author diversity penalty → pinned and editorial overrides
- Selector: sort descending, take 20, at least 5 out-of-network, tie-break stable on item ID
- Side effects: cache served IDs, emit impressions, increment counters — all after the response is committed, all fire-and-forget
- Trade-offs surfaced: multi-action, because the team retunes weekly and cannot retrain weekly; isolated scoring; request-time
- Out of scope: the retrieval source's own recall. If obvious items are missing from the feed, that is a candidate-generation problem and this specification does not address it.
