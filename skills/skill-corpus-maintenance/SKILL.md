---
name: skill-corpus-maintenance
description: "Grooming pass over an agent's own instruction corpus: one deterministic inventory feeds a keep/revise/retire verdict per item and the promotion of recurring principles into the standing rule text. Batched cross-reads, evidence-bearing reasons, approval before any mutation, and a dated record so the next run re-evaluates only what changed. Use for periodic maintenance, not author-time review."
metadata:
  category: ai
---

# Skill Corpus Maintenance

Provides a periodic grooming pass over the instruction corpus an agent carries: the capability items it selects among, and the standing rule text it loads every session. One deterministic inventory feeds two branches — a verdict on whether each item still earns its place, and the promotion of principles recurring across items into the standing rules.

The branches are one pass rather than two procedures because each is unsound without the other's evidence. An item cannot be called redundant without knowing what the standing rules already say, and a principle cannot be promoted without knowing which items carry it. They read the same inventory, batch the same way, and stop at the same approval gate.

The corpus is enumerated by a collector, never from recollection. A model asked what is installed answers from what it remembers loading — the subset that fired recently, which is precisely the wrong sample for a pass whose job includes finding what never fires.

Rules marked *[authored]* are this skill's own, filling a gap the source procedures left open.

## Use this skill when

- Periodic maintenance is due on a corpus that grew by accretion and has not been read as a whole since.
- Items were installed, imported, or inherited, and nothing has checked them against the ones already there.
- The same principle keeps reappearing item after item and looks like it belongs in the standing rule text instead.
- Items are suspected of overlapping each other, or of citing tool names, flags, or interfaces that have since moved on.
- No record exists of which items were ever judged, or why any of them is present.
- A previous pass was interrupted and left a partial verdict record to resume from.

## Do not use this skill when

- One freshly authored item needs review. That is a draft against a quality bar — one item, one author, no corpus — and it does not need an inventory, a batching plan, or a cache.
- The question is whether an item actually changes what the agent produces. Answering it takes a run with the item and a matched run without it, graded the same way. Reading the text cannot settle it, and a verdict formed by reading will be confident and unfounded.
- The question is what the standing surface costs to load, rather than whether its contents deserve to be there. Pricing always-loaded text, separating the cost of a description from the cost of the body behind it, and ranking components by tokens reclaimed is a different audit with a different unit and a different report. This pass never counts tokens and never ranks by them — it judges content on the merits, item by item, and a cheap item with nothing behind it still fails here.
- The corpus is documentation a human reads and nothing loads as instruction. Two documents covering the same ground is a style question; two instruction items covering the same ground is a selection failure, which is the defect this pass exists to find.
- The corpus is small enough to cross-read whole in one sitting. Batching, caching, and the cross-batch merge exist to make a corpus that does not fit tractable; below that size they cost more than they return.
- Nobody is available to rule on the proposals. Every mutation here is gated on a human decision by design, so without one the pass either stalls or applies an unreviewed verdict — and the second is the worse outcome.

## Required inputs

- **Every corpus root**, named explicitly — shared and project-local alike. A root that turns out not to exist is recorded as absent and the pass continues; a root nobody named is a silent omission that makes the report read as complete.
- **The full standing rule text**, or an explicit statement that no standing rule surface exists yet.
- **The previous verdict record**, if there is one, and its completion status.
- **A named decision-maker** who rules on proposals. Not a step; a precondition.

## Workflow

### 1. Collect the inventory

Run the collector over every root, for each corpus role — capability items and standing rules are separate inventories with separate entry conventions. Record which roots were found and which were absent, and carry that into the report.

Index **one entry file per item**, not every file beneath it. Support files under an item are not separately selectable, so counting them inflates the corpus, and keying on them makes an edit to a supporting note look like a changed item on the next run.

**An axis fed by a signal this environment does not emit is recorded as absent, never defaulted.** A collector that substitutes zero for a missing usage signal reports a corpus in which nothing is ever used, and every verdict it feeds is biased toward removal — an unmeasured axis presented as a measured zero. Where no usage telemetry exists, say so in the report and let no verdict rest on usage. *[authored: the source treats usage as an always-available axis, and its collector defaulted it to zero when the file behind it was missing.]*

*Output: one inventory record per corpus role, each naming its roots and their found/absent status.*

### 2. Split changed from unchanged

Compare each item's modification time against the previous record. Items that changed, and items with no entry, are evaluated. Items that did not change carry their previous verdict forward.

- **A carried-forward entry keeps its original reason in full.** It never becomes `unchanged`. A record whose carried-forward entries have lost their reasons is a record with no decisions in it, and the next pass has to re-derive everything the cache was supposed to preserve.
- **A record marked in progress is a resume point, not a result.** Resume at the first item with no verdict; never read a partial record as a completed pass.
- **No previous record means a full pass.** So does an unreadable modification time on an individual item.
- **The previous record is a comparison set, never the enumeration source.** Enumerate from the collector and join the record onto it. Reversed, the pass can only ever see items some earlier run already knew about, and everything added since is invisible to the pass that exists to find it.
- **No standing rule surface yet is not an error.** It is the ordinary state of a young corpus, and it routes every promotion candidate to the new-file verdict rather than aborting the run.

*Output: the evaluation set, and the carry-forward set with reasons intact.*

### 3. Batch by theme

Group items by what they are about, read from their descriptions — not alphabetically and not by directory. Overlap between two items is visible only when both land in the same batch, and alphabetical order scatters exactly the pairs the pass is looking for.

Size each batch so that the batch, the entire standing rule text, and the out-of-batch index all fit the analysis context with room left for the cross-read itself. **No batch size is established here**; whatever is chosen is a chosen budget, recorded with the run so the next pass can reproduce or revise it. Delegate each batch to its own analysis context.

*Output: the batch plan, with the size chosen and the reason for it.*

### 4. Cross-read each batch

Each batch receives three things: the full text of its own items, the full standing rule text, and a name-and-description index of every item outside the batch.

**Do not pre-filter the standing rules.** Coverage has to be judged including principles already stated in different words, which a keyword search cannot see — it finds the wording and misses the rule. Where the standing rule text genuinely does not fit alongside a batch, shrink the batch first; if it still does not fit, mark the run's coverage partial and say so in the report, because a candidate wrongly called new is indistinguishable in the output from one correctly called new.

Apply the same criteria to every item regardless of where it came from. No verdict branches on an item's origin, author, or age.

**Branch A — one verdict per item.** Judge on: overlap with sibling items; overlap with the standing rules; currency of the technical references it cites; and usage, only where a usage signal actually exists. An item whose references cannot be checked in this environment is recorded as unverified, not as current.

| Verdict | Meaning |
| --- | --- |
| Keep | Useful and current as written |
| Improve | Worth keeping; name the section, the change, and why |
| Update | A technical reference it depends on has moved; name the reference |
| Retire | Name the defect and name what covers the need instead |
| Merge | Substantial overlap; name the target item and the content to move into it |

**Branch B — candidate principles for promotion.** A candidate is proposed only if all three hold: it appears in **more than one item, with the count and the items recorded**; it is expressible as "do X" or "don't do Y" rather than "X matters"; and a one-sentence violation risk can be stated for it. The three together are what stop a promotion pass from filling the standing rules with abstractions nobody can violate.

| Verdict | Meaning |
| --- | --- |
| Append | Extend an existing section; name the file and section |
| Revise | Existing rule text is wrong or insufficient; carry reason, before, and after |
| New Section | Add a section to an existing rule file |
| New File | No rule file fits, or no standing rule surface exists yet |
| Already Covered | Present in the rules, including in different words; give the one-line reason |
| Too Specific | Appears in one item only; it stays in that item |

**What, not how.** A promoted principle carries the rule; the commands, code, and worked examples stay in the item, and the promoted text carries a backlink to the items it came from so the detail remains findable. Without that split the standing rules become a second copy of the corpus, loaded on every session.

*Output: per batch, a verdict for every item and a candidate list, each entry carrying its own evidence.*

### 5. Merge across batches

Deduplicate candidates that state the same principle in different words, then **re-check the evidence threshold on combined evidence**. A principle appearing once in each of four batches clears the bar in total while failing it in every batch individually — per-batch analysis cannot see this by construction, so it is the merge step or nothing.

Resolve cross-batch verdicts too: a `Merge` pointing at an item in another batch is only valid if that target exists and is not itself retired. Where two items each name the other, the merge direction is a decision for the report, not for whichever batch happened to run last.

*Output: one merged proposal set, with per-candidate evidence counts as combined.*

### 6. Present, then apply only what was approved

Nothing in the corpus is modified before its proposal is ruled on, item by item. Bulk approval of a whole verdict class is not a decision on the items inside it.

A `Retire`, `Merge`, or delete proposal is presented with three things or it is not ready: the specific defect found, what covers the same need afterwards, and the impact of removal — anything that references the item, and any workflow that depends on it. Record each ruling as approved, modified, skipped, or pending, against the item it applies to.

*Output: a decision recorded against every proposal, and applied changes limited to the approved ones.*

### 7. Persist the record

Write the dated record outside the corpus being audited — an audit that writes state into the tree it is auditing changes what the next run inventories, and breaks outright when the corpus is read-only or reinstalled. Key items by path and candidates by a slug of the principle, so both re-identify on the next run. Shapes and required fields: `references/record-shapes.md`.

*Output: one dated record carrying verdicts, decisions, and the modification times they were formed against.*

## Reason quality

A verdict is only as good as its reason, and the reason has to stand alone months later, without the batch it was written in. Every reason names the specific evidence: what was found, where, and what happens instead.

Retire — wrong: `Superseded.`
Retire — right: `Its three procedures are stated verbatim in the deployment item, which also covers the rollback case this one omits. Nothing here is unique.`

Merge — wrong: `Overlaps with the review item.`
Merge — right: `Thin: one procedure, already step 4 of the review item. Move the one-line note about draft PRs into that step and drop the rest.`

Improve — wrong: `Too long.`
Improve — right: `Its framework-comparison section restates the architecture item's table with no additions; deleting it removes the duplication and the maintenance hazard.`

Keep, carried forward — wrong: `Unchanged.`
Keep, carried forward — right: `Modification time moved, content identical. Unique coverage of the data-migration path; no sibling overlap found in the previous pass and none in this one.`

## Decision points

1. **Full pass or incremental?** No previous record, or a record whose status is in progress → full pass, or resume, respectively. A completed record with readable modification times → evaluate the changed set only.
2. **Is this candidate a rule or an item detail?** More than one item, statable as do/don't, with a nameable violation risk → candidate. Any one of the three missing → it stays in its item.
3. **Merge or retire?** Unique content that something else should carry → merge, and name what moves. No unique content → retire, and name what covers the need.
4. **Is the coverage check trustworthy?** Whole standing rule text in the analysis context → yes. Anything less → the run is partial, `Already Covered` verdicts are provisional, and the report says so.
5. **Apply or hold?** Approved by the named decision-maker → apply. Anything else, including silence → hold. *[authored: the source requires approval but never says what an unanswered proposal defaults to.]*

## Output contract

Returns a maintenance report carrying:

- The roots searched, each marked found or absent, and the item count per root.
- The mode — full or incremental — with the count evaluated and the count carried forward.
- The batch plan: the batch size chosen, labelled as a chosen budget, and the theme of each batch.
- Whether the standing rule text was passed whole, and, if not, that coverage is partial.
- One verdict per item, each with a self-contained reason, plus the axes evaluated and any axis recorded as having no signal.
- The candidate principles after the cross-batch merge, each with its combined evidence, its item count, its violation risk, its verdict, and its target.
- The proposals requiring a ruling, with defect, replacement, and impact stated for every removal.
- The decision recorded against each proposal, and the subset actually applied.
- The record's location and its date.

## Scripts

`scripts/inventory.sh` collects the deterministic inventory both branches read.

- Usage:
  - `scripts/inventory.sh <corpus-root> [<corpus-root> ...]` — capability items, one entry file per item.
  - `scripts/inventory.sh -e '*.md' -H -r standing-rule <rules-root>` — a flat corpus where every file is an item, with its level-2 headings indexed so a proposal can name a target section.
  - `-r <role>` labels the inventory; `-h` prints usage.
- Required: `bash`, `jq`, `find`, `awk`, `sort`, `wc`, and either GNU or BSD `stat`/`date`.
- Behavior worth knowing before relying on it: a root that does not exist is reported as `found: false` with zero items and exit 0, never as an error; frontmatter reading is a single-line reader, not a YAML parser, so multi-line and nested values report empty rather than wrong.
- Verification:
  - `scripts/inventory.sh <root> | jq '.roots, .total'` — every named root appears, with its count.
  - `find <root> -name SKILL.md -type f | wc -l` — must equal `.total` for a default run.
  - `scripts/inventory.sh <root> | jq '[.items[] | select(.mtime == "")] | length'` — must be `0`, or the incremental key is unusable and the next run must be a full pass.

## Provenance

- **Sourced:** the deterministic-collection-then-judgment split; the phase order; both verdict vocabularies; the three-part promotion filter; the no-pre-filtering rule and its justification; the cross-batch merge on combined evidence; the reason-quality contract and its contrast pairs; the what-not-how split with backlinks; the resume-on-partial-record rule; blind evaluation regardless of origin; and approval before any removal.
- **Chosen, not measured:** the batch size, which the source stated as a constant and which is carried here only as a budget to record. No number in this procedure is a measurement.
- **Not carried:** the source's mode durations, its item-per-batch constant, its line-count trigger for compacting the standing rules, and its "more than one item" threshold as a fixed number — the rule survives at any threshold above one, so the count is recorded rather than fixed. Its worked end-to-end example is also not carried: it routed the same candidate to three different targets and its saved record disagreed with the run it claimed to record.
- **Authored, marked at each site:** recording an axis with no available signal as absent rather than defaulting it; the hold-on-silence default for unanswered proposals.
- **Repaired rather than reproduced:** indexing one entry file per item instead of every file beneath it; treating an absent standing rule surface as the new-file case instead of a fatal error; and keeping the persisted record outside the audited corpus.

## References

- `references/record-shapes.md` — the inventory, verdict, and candidate record shapes, their required fields, and the keying rules that make a run re-identifiable.
