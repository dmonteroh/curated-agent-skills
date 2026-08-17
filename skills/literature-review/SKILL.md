---
name: literature-review
description: "Takes a research question through one reproducible pass over a body of academic or technical literature — protocol before collection, logged searches, deduplication, staged screening with recorded exclusions, per-study methodological appraisal, and confidence-tiered synthesis. Use when a corpus has to be found, screened, appraised, and cited rather than a single answer looked up."
metadata:
  category: research
---

# Literature Review

Provides one ordered pass over a *body* of literature, where each step ends in an artifact somebody else could re-run: a protocol, a search log, a deduplication count, an exclusion record, an appraisal record, an extraction table, and a synthesis whose claims are tiered by how well the evidence behind them holds.

Two failures this exists to prevent. The first is a synthesis assembled from whatever the first search returned, with no record of what was searched, what was dropped, or why — reproducible by nobody, including its author. The second is subtler and more common: screening for **relevance** and treating that as quality. A study can be exactly on topic, match every inclusion criterion, and still not support the claim it is about to be cited for. Relevance decides whether a study enters the corpus; appraisal decides what weight its findings carry once inside.

## Use this skill when

- A research question needs the state of the art established across many sources rather than answered from one.
- A citation-backed background, related-work, or evidence section has to be produced and later defended.
- Gaps, contradictions, or unanswered questions in a field have to be identified from the literature itself.
- Evidence has to be compared across peer-reviewed papers, preprints, technical reports, and standards.
- A search has to be reproducible by a reviewer, a supervisor, or a regulator — the queries, filters, and exclusions all recorded.
- A set of already-exported records has to be deduplicated, screened, appraised, and synthesized.

## Do not use this skill when

- The ask is a single fact, definition, identifier, or date, or an orientation answer — "roughly, what does the field think about X". Assembling a screened corpus is disproportionate there; the right shape is the lightest source that settles the question, with each claim labeled by how it was known.
- The scan is commercial — market size, competitors, vendors, pricing. Different sources, different authority rules, and no peer-reviewed corpus to screen.
- The ask is revision feedback on the user's own unpublished draft: a manuscript, a proposal, a thesis chapter. Judging whether a source may enter a synthesis is a different job from advising an author on their own text, and this skill deliberately does not cover the second.
- One paper has already been chosen and only needs summarizing or explaining. No screening or inclusion decision is in play.
- The work is citation formatting, style compliance, or bibliography management.

*[authored: the source candidate carries no stand-down at all; these five cases are this skill's own.]*

## Workflow

### 1. Frame the question and set the rigor level

Convert the prompt into a searchable question using an explicit slot frame — for clinical or biomedical work, population / intervention or exposure / comparator / outcome; for technical work, system or domain / method / comparison baseline / evaluation metric. A question with an empty slot produces an unbounded search.

Rigor: default to a scoping pass for exploratory work and a systematic pass when the output backs a publication, a clinical claim, or a safety decision. A systematic pass plus quantitative effect aggregation is a meta-analysis; the aggregation step needs statistical review beyond this workflow, so state that boundary rather than implying the numbers were pooled.

### 2. Write the protocol before collecting anything

Record, and show, before the first query: sources to search, date range, languages, publication types, inclusion criteria, exclusion criteria, and the exact search strings. Criteria written after the results are visible are criteria fitted to the results.

Source coverage: name at least one authoritative index for the domain, one route to preprints and grey literature — or an explicit statement that they are excluded — and one broad cross-publisher index. Which services fill those slots changes over time and varies by field, so choose them per question and record the choice in the protocol; a fixed list of database names ages badly and is not part of the method. *[authored: the source names a fixed minimum database set; the coverage rule generalizes it.]*

Decision point: if the requester cannot supply inclusion and exclusion criteria, produce a draft protocol and get it agreed before searching. Do not start collecting and infer the criteria later.

### 3. Search and log

Every search is logged as it runs, in a table that makes the pass re-runnable:

```markdown
| Source | Date searched | Query | Filters | Results | Export |
| --- | --- | --- | ---: | ---: | --- |
| <index name> | <YYYY-MM-DD> | `("CRISPR"[tiab] OR "Cas9"[tiab]) AND "sickle cell"[tiab]` | 2020:2026, English | <count> | ID list |
```

The angle brackets are placeholders, not sample results: a log row carries the counts an actual run returned and nothing else.

Keep raw identifiers, URLs, abstracts, and working notes in a store separate from the prose. Prose written over a mutable pile of tabs cannot be checked later.

### 4. Deduplicate on a fixed precedence

Match in this order, stopping at the first that resolves: DOI, then a stable repository identifier, then exact title, then normalized title plus first author plus year. Record how many duplicates were removed — the number is part of the audit trail, not bookkeeping.

### 5. Screen in stages, and record why each source left

Screen title, then abstract, then full text. Every exclusion records a reason from a closed list: wrong population, wrong intervention or method, wrong outcome, not primary research, duplicate, full text unavailable, outside the date range.

A source dropped without a recorded reason cannot be defended when someone asks why their paper is missing. If a needed reason is not on the list, amend the protocol, add it, and re-screen everything already excluded against the amended list rather than applying it only going forward. *[authored: the source fixes the list and says nothing about extending it.]*

### 6. Appraise each surviving study

Screening established relevance. This step establishes whether the study can carry weight. Check every included study against these dimensions:

| Dimension | What is checked |
| --- | --- |
| Methodology fit | Does the design answer the question the study itself poses, are the design choices justified, and is enough reported that another team could reproduce it? |
| Data adequacy | Are the data sources credible and appropriate, is the sample or corpus sufficient for the claim drawn from it, are inclusion, exclusion, and preprocessing decisions documented, and are missing data and bias risks addressed? |
| Analysis and baselines | Are the analytical methods appropriate to the data, are baselines and controls fair, are uncertainty, sensitivity, or robustness checks present where the claim needs them, and are alternative explanations considered? |
| Stated threats to validity | Are the limitations specific rather than generic, and does the study separate what it demonstrated from what it speculates? |
| Citation support | Open the study's strongest claim against the source it cites: does that source actually support it? Are primary sources used where they exist, and are reviews and preprints identified as such? |

Each dimension resolves to one of three outcomes, and there is no score:

- **Clear** — no concern worth carrying forward.
- **Flagged** — a specific weakness, named in one line. "Baseline was not tuned" is a flag; "analysis is weak" is not.
- **Disqualifying for this question** — the study cannot support the claim it was screened in for. Exclude it and record the reason exactly as a screening exclusion is recorded.

**No numeric scale, no aggregate score.** The appraisal dimensions here come from a rubric that scored nine dimensions from 1 to 5 and defined no rule for combining them into the overall figure its own template led with. An aggregate nobody can reconstruct is an aggregate nobody can act on, so this skill keeps the flags themselves and carries them forward instead. *[authored: the dimensions are sourced; the three-outcome resolution replacing the scale is this skill's own.]*

Flags travel: *[authored — the source rubric scored studies in isolation and the base workflow tiered claims with no link between the two]*

- An unflagged study may support a high-confidence claim once other work replicates it.
- A flagged study's findings enter the synthesis at medium or low confidence only, and the flag text travels with every claim that study supports.
- A disqualified study leaves the corpus with its reason recorded.

### 7. Extract into a structured table

```markdown
| Study | Design | Population or data | Method | Comparator | Outcome | Key finding | Appraisal flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

For technical papers, carry dataset, benchmark, metric, baseline, and reproducibility notes. The appraisal column is what keeps step 6 from evaporating between the appraisal and the write-up.

### 8. Synthesize by theme, tiered by confidence

Group evidence by theme, never paper by paper — a paper-by-paper walk is an annotated bibliography, not a synthesis. Produce these sections rather than choosing freely among "lenses": strongest evidence, conflicting evidence, methodological weaknesses (populated from the appraisal flags), population or dataset limits, and unanswered questions.

Tier every claim:

- **High** — replicated across independent sources, with no unresolved appraisal flag on the studies carrying it.
- **Medium** — plausible but limited by sample, method, recency, or a named flag.
- **Low** — single-source, early, speculative, or weakly measured.

Labeling each statement of the final write-up by how it was known — sourced, inferred, or recommended — and dating anything freshness-sensitive is a general reporting discipline and is not restated here. The tiers above grade the evidence behind a claim; they do not grade the prose that reports it.

### 9. Verify citations and labels before finalizing

Check that every identifier resolves — DOI, repository ID, or official URL — and that author names and publication year match the record. Never cite a paper for a claim it does not make. Mark preprints as preprints and keep reviews distinct from primary evidence throughout the write-up, not only in the reference list.

## Output contract

```markdown
# Literature Review: <topic>

Date: <date>            Review type: <scoping | systematic | meta-analysis>
Search window: <dates>  Sources: <list>

## Research question
## Search strategy and protocol
## Inclusion and exclusion criteria
## Evidence summary
## Appraisal summary          <- per study: clear / flagged (with the flag) / disqualified
## Thematic synthesis         <- strongest evidence, conflicts, methodological weaknesses, limits, open questions
## Gaps and limitations
## References
## Search log                 <- one row per search, plus the duplicate count and the exclusion tally by reason
```

## Examples

Illustrative wording; the counts are stand-ins for a real run's own numbers.

**Recording exclusions.**

- Weak: "Removed 31 papers that were not relevant."
- Right: "Excluded 31 at abstract stage: 12 wrong outcome, 9 not primary research, 6 outside date range, 4 full text unavailable."

The second can be audited and re-run; the first asks the reader to trust a judgment they cannot see.

**Carrying an appraisal flag into the synthesis.**

- Weak: "Three studies report the method outperforms the baseline (high confidence)."
- Right: "Three studies report the method outperforms the baseline. Two share a flagged weakness — the baseline was left untuned — so the claim carries medium confidence, and the untuned-baseline flag travels with it."

**Relevance is not quality.** A study on exactly the right population, with exactly the right outcome measure, whose comparator was chosen after the results were known, passes screening and is flagged at appraisal. Screening alone would have promoted it into the synthesis untouched.

## Common pitfalls

- Screening for relevance and calling the corpus appraised.
- Treating a search snippet or an abstract as evidence for a claim that only the full text could support.
- Mixing preprints, reviews, and primary studies without labeling which is which.
- Omitting negative or conflicting findings because they complicate the story.
- Claiming systematic rigor without a protocol written before collection began.
- Resting a broad claim on a single database, unless the scope is explicitly limited to that database.
- Treating citation count, venue, or author reputation as proof of quality.
- Letting the appraisal exist only in the reviewer's head, so the extraction table and the synthesis carry no trace of it.
