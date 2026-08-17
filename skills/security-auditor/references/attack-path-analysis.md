# Attack-path enumeration and choke-point ranking

Detail behind instruction step 5. `references/finding-triage.md` answers *is this finding real*; this file answers *which fix buys the most*.

The structure is an attack tree in Schneier's sense (1999): the attacker's goal is the root, internal nodes decompose it, leaves are atomic attacker actions. The tree itself is textbook and a model draws one on request. The part that changes a decision is the ranking rule below — mitigations ordered by the share of enumerated attack paths each one cuts, rather than by the severity of the threat each one names.

## Scope the tree before enumerating anything

- One attacker goal per tree. Enumeration takes the cross-product of child path sets at every AND node, so a whole-system model produces a path set that is expensive to compute and that nobody reads.
- If the enumerated set outgrows what a reader will read, the tree is too broad: split it by goal and enumerate each separately. Do not truncate the list to a display cutoff — truncation drops the long conjunctive paths first, and those are the ones a reviewer has not already thought of.
- Falsifiable check: the analysis states the total enumerated path count. A ranking reported without it cannot be checked, because every share below is a fraction of that number.

## Node semantics

| Node | Meaning |
| --- | --- |
| OR | Any one child achieves the parent goal. |
| AND | Every child is required to achieve the parent goal. |
| Leaf | An atomic attacker action — the unit that a control blocks. |

## Path enumeration

- An OR node contributes one path per child.
- An AND node contributes the cross-product of its children's path sets, because every branch must be executed.
- A path is therefore a *conjunction* of leaves the attacker must all complete — not a route through the diagram.
- The consequence that makes the counting worth doing: blocking any single leaf on a path closes that entire path.

## Choke-point counting

1. Count, for each leaf, how many enumerated paths contain it.
2. Rank leaves by that count. A high count is a choke point: one control there closes many routes at once.
3. Rank **every** leaf, including leaves with no mitigation recorded. Those are the highest-value gaps the analysis can produce.
4. Rank candidate mitigations by `paths closed / paths enumerated`, and report that share beside each recommendation rather than only the ordering.
5. Re-run the count with a proposed control marked as blocking, and report the residual open paths — how many remain and which they are.
6. A control sitting on a path that another control already closes cuts zero *additional* paths and ranks last. Buying it may still be right, but the grounds are elsewhere; state them. Never let a coverage count be read as justification for a second control on an already-closed path, and never treat "only one control on this path" as a finding on its own — the tracked boundary test in instruction step 2 decides whether a control is real, and this count only orders the real ones.

**Wrong, and observed in a working implementation of this technique:** rank only the leaves that already carry a recorded mitigation. The ranking then structurally cannot surface an unmitigated choke point — the single most valuable thing it could have told the reader — and reads as a clean report because the gap never appears in it.

**Right:** rank all leaves by path count first, then join the recorded mitigations in. A high-count leaf with nothing attached heads the gap list.

## Worked example

Goal: read customer records out of the production database.

- Root is **AND**: `[E] move the data out over the egress path` and `[G] obtain read access`.
- `[G]` is **OR** over three branches: `[A]` steal an operator session (**AND** of `a1` phish credentials, `a2` defeat the second factor); `[B]` exploit the reporting service (**AND** of `b1` reach the reporting host, `b2` exploit the report query endpoint); `c` use a leaked backup credential (a leaf directly under the OR).

Enumerated paths: `{E, a1, a2}`, `{E, b1, b2}`, `{E, c}` — 3 in total.

Leaf counts: `E` appears in 3; every other leaf appears in 1.

Ranking: an egress control on `E` closes 3 of 3 enumerated paths; hardening the second factor at `a2` closes 1 of 3. Severity ordering would likely have put credential phishing first. If no mitigation is recorded against `E`, that absence is the report's headline, and a ranking restricted to already-mitigated leaves would have omitted it entirely.

With `E` blocked, residual open paths within this tree: 0. State that as *zero within the enumerated tree* — it is a claim about the model's completeness, not about the system.

## Attacker-cost scoring, and one aggregation convention

Score paths on whatever attacker-cost axes the engagement cares about — effort, money, elapsed time, detection likelihood. Whichever are used, state the aggregation convention at the top of the analysis and hold it for every path.

Convention used here, reasoned rather than measured, and a **chosen default**:

| Axis | OR node | AND node |
| --- | --- | --- |
| Difficulty / skill | min — the attacker takes the easiest branch | max — the hardest required step gates the path |
| Cost | min | sum — every branch is paid for |
| Elapsed time | min | sum |
| Detection risk | min | max — the noisiest required step is the one that gets the attacker caught |

**Picking a convention matters more than which one is picked.** One implementation of this technique was found carrying three mutually inconsistent conventions across four functions in the same file — an AND node over children of difficulty 2 and 4 scored 4 under one and 6 under another — which makes any two path scores incomparable while still producing a confident-looking ordering.

- This skill prescribes no band count and no numeric scale. Whatever ordinal bands the engagement already uses, record them once and keep them fixed for the assessment; a source that supplies three-level bands in one place and five-level bands in another supplies neither.
- Ordinal bands are not magnitudes. Summing "difficulty 3" and "difficulty 4" assumes the gaps between bands are equal, which nothing establishes. Report scores as a comparative ordering — "path A is cheaper for the attacker than path B" — never as a quantity, and never as a number carried into a business case.
- The one figure here worth reporting as a number is `paths closed / paths enumerated`, because both terms are counted from the enumeration rather than assigned by judgment.

## What this composes with

Instruction step 2 produces the control-to-boundary map, which says which controls are real: a control gating nothing that crosses a boundary cuts no paths, whatever its count suggests. This file orders the real ones. Run the boundary test first; a choke-point ranking computed over controls that were never gating anything ranks fiction.

## Reporting

- Total enumerated paths, and the attacker goal the tree was scoped to.
- Top choke-point leaves with their path counts, unmitigated ones marked.
- Ranked mitigations, each with its `paths closed / paths enumerated` share.
- Residual open paths after the proposed control set, with the count and the paths themselves.
- The aggregation convention in force, stated explicitly.
