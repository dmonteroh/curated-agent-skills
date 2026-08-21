---
name: competitive-benchmark
description: "Runs a competitive positioning benchmark as one pipeline: elicits the client's positioning brief, scopes and tiers a candidate set, scores every survivor on fixed dimensions with evidence per score, then assembles a decision-grade report. Emits no composite score and never averages the poles of the client's strategic tension. Use when a named organization needs a defensible read of the rivals contesting its position."
metadata:
  category: research
---

# Competitive benchmark

Provides an ordered procedure that turns one organization's positioning into a defensible benchmark of the rivals contesting it. Each stage produces a named artifact that is the next stage's only input: a positioning brief, then a tiered candidate set, then a profiled set, then one uniform score card per competitor, then a report that resolves three decisions. A set scoped without the client's own positioning makes the client look either unbeatable or doomed, which is why the brief comes first and is not optional.

## Use this skill when

- A named organization needs to know who contests its position, how it compares, and where its defensible ground is.
- A competitive landscape has to be scoped, scored, and written up as one auditable deliverable rather than three disconnected exercises.
- A positioning decision — where to invest, what to concede, which rival is the real fight — is waiting on evidence rather than on opinion.
- The output has to survive being questioned: every score traceable to a source, every recommendation traceable to the client's own stated emphasis.

## Do not use this skill when

- **The competitor set and its scores already exist and only a document is wanted.** Assembling scores whose evidence trail this procedure did not produce lends them a defensibility they have not earned; the appendix that makes the report auditable cannot be written after the fact.
- **The question is fit rather than positioning** — evaluating a technology, vendor, or platform against a requirement set for a buying decision. That is an evaluation against requirements, and nothing below applies to it.
- **The subject is one product rated on its own merits** rather than against a set. A single-product review answers "is this good"; this procedure answers "who else is here, and where is the room."
- **There is no organization whose positioning defines the frame.** Without a brief this is generic market scanning, and the thing that makes the scoring defensible does not exist. Elicit the brief or decline — never invent one.

## Required inputs

Six fields, established before any candidate is looked at. This brief is the pipeline's first input and every later stage reads from it.

1. **Identity** — what kind of organization this is and how it presents itself.
2. **Offer** — what it actually sells.
3. **Target buyer** — who it sells to.
4. **Differentiator** — the positioning argument it believes defends it.
5. **Strategic tension** — the two named poles whose intersection marks the position it wants, plus which quadrant of that 2×2 is the target. This is the axis pair the benchmark resolves around.
6. **Emphasis mix** — the deliberate proportional balance across its strategic emphases, whatever proportions it gives. Every later recommendation is checked against this and flagged if it would shift it.

**Elicitation is bounded to one pass.** Ask for all six together, in one round, rather than interviewing. Fields 1 through 4 may be drafted from the organization's own public material and put back for confirmation — a draft the client corrects is faster and more accurate than a blank question. Fields 5 and 6 cannot be drafted: they are statements of intent, and inventing them means benchmarking against a position nobody chose.

**The stop.** If the strategic tension cannot be obtained, stop and say so. The tension dimension, the headline map, the profiled-set selection, and the white-space claim are all undefined without it, and a benchmark run without it is a competitor list with numbers on it.

*Authored, not sourced:* the one-pass bound, the draftable-versus-non-draftable split, and the stop are this skill's own rules. The source refused to proceed without a brief but delegated eliciting one elsewhere, which left the procedure unable to start on its own.

## Constraints

Three invariants hold across every stage. Each of them is a thing an agent will otherwise do unprompted, because each of them looks like rigour.

- **No composite score, anywhere.** Not as a weighted average during scoring, not as a total column in the matrix at render time. Dimension scores are read as a profile. An average hides the asymmetry between competitors, and that asymmetry is the entire finding.
- **The two poles of the strategic tension are scored and reported separately, never averaged.** The client's question is precisely whether a rival achieves both at once; averaging them destroys the only evidence that answers it.
- **No dimension carries a weight.** A weight is consumable only by a composite, and the composite is forbidden — so any weight vector here would be decoration that reads as measurement. An earlier version of this method shipped one that no step ever read; it is deliberately absent, and re-adding it would put a number back with no operation behind it.

## Workflow

### Stage 1 — Scope the candidate set along both poles of every axis

Do not sort candidates into market-specific buckets; place them along generic axes, so the landscape cannot skew toward one archetype. Deliberately populate **both poles of every axis before pruning anything** — this is the instruction that stops the set from becoming a list of the client's own mirror images.

| Axis | Poles |
|---|---|
| Positioning stance | identity-led (competes on point of view) · capability-led (competes on craft, throughput, outcomes) |
| Specialization | specialist in one discipline or vertical · generalist across a broad menu |
| Size band | the client's own band · the bands directly above and below it |
| Engagement format | productized, named packages · bespoke or custom engagement |
| Distinctiveness posture | conventional and safe · contrarian and opinionated |
| Credibility model | outcome-led (metrics, named customers) · reputation-led (showcase, awards, visibility) |
| Operator brand strength | interchangeable · ownable, recognized identity |
| Market reach | local or regional · global |

Then resolve the set into three tiers, which carry through to the report:

- **Direct** — near the client on positioning, specialization, size band, and market *at once*. All four, not any of them. This is the realistic head-to-head.
- **Adjacent** — partial overlap, one capability or a different buyer size, pressuring at the edges.
- **Aspirational** — not competed with today, but setting the bar the client is aiming at.
- Substitutes — in-house teams, generalist contractors, tooling that removes the need — are noted as a threat vector, not profiled as competitors unless materially relevant.

**Verify every attribute against at least two independent sources before treating it as fact.** Self-reported copy is a claim, never an attribute. Two sources is this skill's chosen floor rather than a measured one; the rule that matters is that a single self-reported source never establishes anything, and the verification note travels with the attribute all the way to the appendix.

Output: a tiered candidate set, each entry carrying its axis positions, its tier, and its source links.

### Stage 2 — Select the profiled set by role, not by threshold

Score each scoped candidate on four pre-filter axes — offer overlap, distinctiveness, commercial credibility, and capability proximity — using the 1-to-5 anchors defined in Stage 3, so the same words mean the same thing at both stages. Then select by the role a candidate plays in the argument:

The profiled set must contain one candidate in each of these four roles, where one exists in the scoped set:

- **Target-position exemplar** — high on both poles of the client's tension. Proves the target position is achievable.
- **One-pole cautionary case** — high on one pole, low on the other. The failure mode to learn from.
- **Competent-but-forgettable archetype** — high credibility, low distinctiveness. The mass the client defines itself against.
- **Direct threat** — the Direct-tier candidate sitting closest to the client on the tension map.

Beyond those four, admit a candidate **only if it adds a role or an axis position no admitted candidate already holds.** A candidate that duplicates an admitted candidate's role and axis position is dropped however well it scored: a second example of the same thing adds length, not evidence.

If no candidate fills the target-position exemplar role, record that as a finding — do not promote the nearest miss into it. An empty target quadrant is the answer to the report's central question, not a gap in the set.

*Authored, not sourced:* this whole selection rule. The source kept any candidate scoring high on *either* distinctiveness *or* credibility, defined neither "high" nor a threshold, and dropped only the low/low quadrant — a filter permissive enough that its own worked example admitted every candidate it ran, inside a skill whose stated anti-pattern was listing every similar company. The role rule excludes by construction instead.

The profiled set is bounded by the roles it must cover and the positions it must not duplicate, not by a target count. Where a count is fixed for scheduling reasons, it is a chosen budget recorded before scoping begins, never a quality bar.

### Stage 3 — Score every profiled competitor on the same dimensions

Fix the dimension list before looking at the first competitor, so the same evidence earns the same number for everyone.

1. **Positioning clarity and distinctiveness** — sharp, ownable, legible at a glance, or generic?
2. **Verbal identity** — an ownable register, or interchangeable category-speak?
3. **Surface craft** — the quality and ownership of the public surface, read as proof of capability.
4. **Offer definition and packaging** — legible and named, or vague and bespoke-only?
5. **Evidence and credibility** — named customers, quantified outcomes, case depth. Proof beyond assertion.
6. **Commercial maturity** — signals they can win and hold the buyer the client targets: process, references, scale, contracting posture.
7. **Owned point of view** — writing, talks, research, frameworks. Depth over volume.
8. **Pricing and engagement legibility** — is how you buy, and roughly what it costs, discoverable?
9. **The client's strategic tension** — the two poles from the brief, scored independently and reported as two values.

This dimension set is this skill's chosen default for a positioning benchmark, not a fixed standard. Substitute or drop what does not apply to the market — a developer-tools market might replace surface craft with documentation depth — but settle the final list before scoring anyone.

**Anchors, 1 to 5**, applied to dimensions 1 through 8 and to each tension pole separately. Adapt the wording per dimension; hold the meaning of each level constant. These five bands are a chosen default, not a measured scale:

| Level | Meaning |
|---|---|
| 1 | Absent or generic. Indistinguishable from a template; an active liability. |
| 2 | Below par. Some intent, but inconsistent or derivative; would not survive a side-by-side. |
| 3 | Competent, table stakes. Solid and professional; ownable by nobody. |
| 4 | Strong and distinctive. Clearly above peers; a strength a buyer would notice and cite. |
| 5 | Category-defining. Best in class, hard to imitate; sets the bar others react to. |

Read the tension poles' own 1/3/5 anchors from the brief rather than reusing the generic wording — the poles are the client's named axes, and their levels mean whatever the client said they mean.

**Collect evidence cheapest signal first**, substituting the source types native to the market. The ordering is the rule; no specific platform is:

1. The competitor's own public surface — positioning, voice, offer packaging, pricing posture, named customers, stated point of view.
2. Their case material — evidence depth and quantified outcomes. Separate *asserted* ("we delivered X") from *proven* (named, measured, verifiable).
3. Third-party review or directory sources native to the market — corroborate customers, deal size, engagement model.
4. Professional-network and team sources — size, model, founder narrative, publishing cadence.
5. Craft or portfolio showcases native to the market — the register of the work itself.
6. Owned content channels — writing, talks, newsletters — for depth of point of view.

**The evidence gate.** Every score carries a one-line justification and the source that earned it. A score that cannot point at a source is not assertable — go and get the evidence, or leave the cell empty and say it is empty. This is what the appendix later renders, and it is what makes the report survive being questioned.

**Bias controls**, applied before the card is final:

- **Asserted versus proven.** Downgrade credibility and evidence scores for self-reported claims with no corroboration.
- **Affinity bias.** Reviewers over-score competitors whose style they share and under-score rivals' commercial strength. Score craft and credibility independently; a dull surface may be winning the larger customers.
- **Recency and visibility bias.** Award-winning, showpiece work dazzles and may have no commercial depth behind it. Corroborate before it moves a credibility score.
- **Survivorship.** The visible, well-marketed players are not the market. Go looking for the strong-but-quiet operators the visible set omits.
- **Calibrate across the set, not in isolation.** Before finalizing, re-read every score side by side: a 4 must mean the same thing for every competitor. Adjust the outliers, and record that the pass happened.

Output: one card per profiled competitor, in this shape.

```text
## <Competitor name>
- Profile / tier: <positioning stance · specialization · size band> / <Direct | Adjacent | Aspirational>
- Role in the set: <target-position exemplar | one-pole cautionary | forgettable archetype | direct threat | adds axis position X>
- One-liner: <how they position themselves, in their words>
- Model / reach / engagement: <size band> · <region> · <pricing and engagement model>
- Notable customers / evidence: <named, each tagged proven or asserted>

Dimension scores (1-5), one row per dimension: score | one-line justification | source

Tension plot
- <Pole 1 from the brief>: <1-5> - <why>
- <Pole 2 from the brief>: <1-5> - <why>
- Quadrant: <high/high | high-1/low-2 | low-1/high-2 | low/low>

Read for the client
- Strength to learn from / weakness that exposes white-space / threat posed
```

### Stage 4 — Assemble the report

Do not begin until every profile card is complete. Partial data breaks the heatmap and makes the white-space claim unsupportable, and a white-space claim argued from a partial set is the single failure this whole pipeline exists to avoid.

Eight sections, in this order:

1. **Executive summary** — decision-first, no methodology. Where the client is strong, where it is exposed, who occupies its target position, and the moves. Written so a reader who stops here still knows what to do.
2. **Landscape and category framing** — a multi-axis map, at minimum a 2×2, with the client's tension plot as the headline artifact. Place every profiled competitor and the client.
3. **Competitor tiers** — one short paragraph per tier: who is in it and why it matters. This sets expectations before the detail.
4. **Benchmarking matrix** — competitors × dimensions, rows grouped by tier. The tension dimension appears as **two separate sub-columns**, never one. Include the client's own honest self-assessment as a row. Use a heatmap so patterns are scannable. Call out the columns where the client leads and where it trails.
5. **Deep dives** — the four roles from Stage 2, in narrative form, chosen for instruction rather than ranking. Each one: what they do, what the client should learn, what the client should avoid.
6. **White-space and threats** — argued from the maps and the matrix, never asserted. Confirm whether the target quadrant is genuinely open; that confirmation is the report's central empirical claim. State the client's own risks alongside rivals', including the risk its own chosen position carries.
7. **Strategic recommendations** — prioritized and sequenced by impact against effort. **Check every recommendation against the emphasis mix from the brief and flag any that would shift it**, in the form "this shifts the emphasis from X toward Y; confirm intent." A recommendation that quietly re-weights the client's own strategy is a decision made on their behalf.
8. **Sources and methodology appendix** — the dimension list, the anchors, the scoped set with tiers, per-competitor source links, and the asserted-versus-proven notes. This is what makes the report auditable.

The report has to resolve three questions, and a draft that leaves any of them open is not finished: **who do we compete with** (name the Direct tier specifically), **how do we compete** (the differentiator in one sentence, grounded in the columns the client owns), and **where is that defensible** (which dimensions and which quadrant rivals cannot easily copy, versus which are table stakes).

Close on questions that force a decision rather than admiration of the analysis: is the target quadrant genuinely open or is a rival already moving in; which Direct competitor is the sharpest threat over the client's own planning horizon and what is the counter; does the emphasis mix still hold given the landscape; which trailing dimension is worth closing and which to deliberately concede.

## Output contract

The consumer receives:

- The positioning brief as established, with any field marked drafted-and-confirmed rather than client-stated.
- The tiered candidate set with axis positions and source links, and the profiled set with the role that admitted each entry plus any role nothing could fill.
- One profile card per profiled competitor, every score carrying its justification and source.
- The eight-section report, with the three decision questions answered and the trigger questions appended.

## Examples

**Weak — the composite reappears at render time:**

| Competitor | Positioning | Evidence | Memorability | Hireability | Total |
|---|---|---|---|---|---|
| Studio A | 5 | 3 | 5 | 2 | 3.75 — rank 2 |

The total is the only column a reader will look at, and it says Studio A is mid-tier. The two columns that matter say something else entirely: Studio A is the most memorable player in the set and the least hireable, which is the cautionary case the client most needs to see. Averaging deleted it.

**Strong — poles separate, quadrant named, evidence attached:**

| Competitor | Positioning | Evidence | Memorability | Hireability | Quadrant |
|---|---|---|---|---|---|
| Studio A | 5 | 3 | 5 | 2 | high memorability / low hireability |

> Studio A — one-pole cautionary case. Memorability 5: the manifesto page is quoted back by third parties in two of the reviewed sources. Hireability 2: no named customer, no stated engagement model, no pricing posture anywhere on the public surface. The client's target quadrant is high on both; Studio A shows what happens when only one pole is served, and no profiled competitor holds both — which is the report's headline finding, not a gap in the set.
