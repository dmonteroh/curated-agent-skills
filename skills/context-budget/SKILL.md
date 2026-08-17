---
name: context-budget
description: "Audits what an agent's standing instruction surface costs before any work starts: prices every always-loaded component, separates always-cost descriptions from on-demand bodies, classifies each as always, sometimes, or rarely needed, and ranks removals by tokens reclaimed. Use when context fills too fast, after adding capabilities, or before expanding a configuration."
metadata:
  category: ai
---

# Context Budget

Provides an audit of the context an agent occupies before the user types anything — the configuration and instruction text injected into every session, the descriptions by which capabilities are selected, and the schemas of every tool registered with the model. That surface is paid on every request for the life of the configuration, it grows by accretion because each addition is individually small, and nothing in a normal session reports it.

The audit exists because the intuitive measure is the wrong one. Ranking components by file size ranks the part that is *not* always paid.

## Use this skill when

- Context fills faster than the work explains, or output quality degrades as sessions run long.
- Capabilities, instruction files, or tool integrations were added over time and nobody has priced the accumulated result.
- Deciding whether a new instruction belongs in the always-loaded surface or behind an on-demand load.
- Planning an expansion — more tool integrations, another instruction file — and the question is whether there is room.
- Inheriting a configuration authored by someone else, where what is loaded and why is not documented.
- A harness reports a large baseline occupancy before the first user message and the composition of that baseline is unknown.

## Do not use this skill when

- The pressure comes from the conversation rather than the configuration: large file reads, verbose tool output, a long transcript. The standing surface is a constant, and removing all of it does not rescue a session that read a 40,000-token log. Measure the baseline first; a small baseline means the problem is elsewhere and this audit will report almost nothing.
- The session in front of you is already degraded. Changes to the standing surface take effect when a session starts, not mid-run. Salvage the current session by other means, then audit.
- The question is money rather than occupancy. Occupied tokens and billed tokens diverge once caching, model tiering, or batching enter, and a spend audit ranks the same components differently.
- The component under question is load-bearing for correctness or safety. This audit reports what a thing costs, never whether it is worth its cost — a safety instruction that costs 400 tokens is a price, not a finding.
- The regression followed a model change or a prompt change, not a configuration change. Nothing in the standing surface moved, so nothing here explains it.
- The surface is one short instruction file with no registered tools and no selectable capabilities. There is nothing to rank, and the audit costs more than it can return.
- The question is whether each capability still deserves its place on the merits — one duplicating another, references that have gone stale, a principle recurring across enough of them to belong in the standing instruction text instead. That is a periodic content grooming pass over the corpus, judged item by item against its siblings and ending in keep, revise, or retire verdicts a human rules on. This audit is the other half of that question and stops where it begins: it prices what a component occupies and reports the price, so a cheap component with nothing to say still passes here.

## Required inputs

The audit is defined over roles, not over locations. Map each role to wherever the harness in use keeps it, and record the mapping in the report so a re-audit covers the same ground:

| Role | What occupies context |
| --- | --- |
| Standing instruction text | Every instruction or configuration file the harness injects into each session, including the whole chain of them when several are concatenated |
| Capability descriptions | The name-and-description pairs the harness lists so the model can choose among its capabilities — whatever it calls them |
| Tool schemas | Name, description, and full parameter schema for every tool registered with the model, from every connected server or extension |
| On-demand bodies | The content behind a description, loaded only once something selects it |

Also required:

- **The context window of the model actually in use**, recorded alongside the model name. The window is a parameter of the audit, not a constant of the world; every percentage in the report is unreadable without it, and a report carried across a model change is wrong rather than stale.
- **Confirmation of which roles this harness truly loads always.** Harnesses differ: some register every tool schema up front and some attach them lazily, some inject instruction files once per session and some per turn. *(Authored, not sourced: the source material assumes a single harness whose loading behavior it never states. Verify before pricing, and record an unverified role as unknown rather than assuming it is always-loaded.)*

## Always-cost versus on-demand-cost

Every component has two prices, and they are paid by different events.

**Always-cost** is what the model reads whether or not the component is ever used: the description that makes it selectable, its frontmatter, its tool schema. Any harness that chooses capabilities by reading their descriptions must have all the descriptions present in order to choose, so an unused capability is not free — it is priced at its description on every single request.

**On-demand-cost** is the body behind that description, paid only when something selects it.

The consequence inverts the obvious ranking: a 600-line body behind a 20-word description is cheap, and a 60-word description on a capability selected twice a year is expensive. **Count and report the two separately for every component.** A single "tokens" column collapses the distinction and produces a cut list that trims the price nobody was paying.

The reverse move — taking something out of the always-loaded surface and putting it behind a description — is a real trade, not a pure saving. *Untested assertion, carried without measurement:* an instruction in the always-loaded surface is read every turn, while one behind a description is read only when the selector picks it, so the move exchanges certainty of application for tokens. Do not move anything whose application must be unconditional. No figure for selection reliability appears here on purpose: the source material's comparisons of one loading mode against another were unattributed, and no measurement is available to replace them.

## Workflow

1. **Inventory.** Establish the baseline first: measure the occupied context of an empty session, before any user message. Prefer a number the harness reports about itself over an estimate, and say which one was used. Then build one row per component carrying its role, its always-cost, and its on-demand-cost in separate columns. Deduplicate as you go — a component reachable by two routes is one cost, and a component the harness never actually loads is zero. *Output: a baseline number with its counting method named, and an inventory table where every row carries two costs.*

2. **Classify.** Sort every component into exactly one bucket. The operative test is referencing: **a component earns standing residency only if something already in the always-loaded surface points at it.**

   | Bucket | Test | Disposition |
   | --- | --- | --- |
   | Always needed | Referenced from the standing instruction text, backs a routine entry point, or matches the work this configuration exists for | Keep. Audit its always-cost for bloat, not its existence |
   | Sometimes needed | Genuinely used, but only inside one domain, phase, or project type, and nothing in the standing surface points at it | Move behind an on-demand load; keep the description and shrink it to what routing needs |
   | Rarely needed | Nothing references it, its content overlaps another component, or no current work matches it | Remove |

   *Output: every inventoried component in exactly one bucket, with the test that put it there.*

3. **Detect.** Work the named patterns over the classified inventory, and attach the tokens at stake to each hit:
   - **Bloated selection text** — a description or frontmatter block written to teach rather than to route. Routing needs enough to be chosen correctly; the body does the teaching, and every extra word is paid on every request.
   - **The dominant term left untouched** — registered tool schemas usually outweigh everything else, because each carries a full parameter schema and there are often many. A large tool set can cost more than all the instruction text combined.
   - **Wrapper tools** — a tool integration whose capability the agent already has by other means pays schema tokens on every request for something it can already do. Before cutting, check what the wrapper adds beyond the raw capability: authentication, structure, or a safety boundary counts; convenience does not.
   - **Duplicated always-cost** — the same rule stated in two places that both load always. One statement is a rule; two are a rule plus a maintenance hazard.
   - **Unsummed chains** — several instruction files each individually reasonable, concatenated into a total nobody has ever measured. A per-file limit that is never summed is not a limit.
   - **Standing text that is really a body** — long explanation, worked examples, or reference material sitting in the always-loaded surface.

   *Output: an issue list, each entry naming the component, the pattern, and the tokens at stake.*

4. **Rank and report.** Order the detections by the ranking rules below, attach an estimated delta to each, and emit the report per the output contract. *Output: the report, with every removal carrying a number and every unmeasured role named as unmeasured.*

## Estimating token cost

Exact counts beat estimates: run the text through the tokenizer of the model actually in use, once, and record what it returns. Where an exact count is unavailable, these seeds apply:

- Prose: words × 1.3
- Code, JSON, schemas, tables, and paths: characters ÷ 4
- A registered tool: ~500 tokens, standing in for its name, description, and parameter schema together

**All three are chosen constants with no derivation behind them.** They are inherited from the source material, which asserts them and never shows how they were obtained. Treat them as starting points, not measurements, and calibrate once: take a real sample of the surface being audited, count it exactly, divide by what the seed predicted, and use that ratio from then on. Schema-dense tool definitions and prose-dense instruction files can sit far apart, and the per-tool figure especially varies with how many parameters a tool declares.

State the method in the report, and use the same method for every re-audit. *(Authored, not sourced.)* The value of this audit is that two runs are comparable; a baseline counted exactly and a follow-up counted by estimate measures the change of method, not the change of configuration.

## Ranking removals

Rank by tokens reclaimed per unit of capability lost — never by tokens alone. In order:

1. **Always-cost with nothing behind it** — a description or schema for a capability nothing selects and nobody wants. Free to remove.
2. **Duplicated always-cost** — delete every statement but one. Free, and it removes a contradiction risk as well.
3. **Wrapper tools whose capability survives their removal.** Cheap, and usually the largest single number on the list because schemas dominate.
4. **Always-cost convertible to on-demand-cost** — move the body behind a description and shrink the description to routing minimum. Subject to the unconditional-application caveat above.
5. **Genuine capability, actually used.** A trade, not a saving. Report it as a trade, name what is lost, and let the owner decide.

Work the dominant role first. Trimming adjectives out of instruction text while a large tool set sits unexamined spends effort on the smaller term. *(The ordering of this ladder is authored; the source states the biggest-lever principle and the wrapper criterion but ranks nothing.)*

## Pre-expansion check

The same model runs forward. Price the proposed addition with the estimator already calibrated, add it to the measured baseline, and report the projected baseline and its projected share of the window.

Report a prerequisite rather than a verdict: name which existing components would have to be cut to absorb the addition, and what that would cost in capability. **No tolerable share is specified here, because none is derivable** — long autonomous runs need far more headroom than short interactive turns, and the same percentage is comfortable in one and fatal in the other. Choose a share for the workload at hand, write it down as a chosen default, and hold re-audits to the same one.

## Output contract

Returns a context budget report carrying:

- The model and its context window, and the counting method used — exact, or estimated with the calibration ratio stated.
- The role-to-location mapping used for this audit, so the next run covers the same surface.
- The measured baseline: total standing cost, absolute and as a share of the window.
- A per-role breakdown, with component counts and with always-cost and on-demand-cost in separate columns.
- The classification: every component in exactly one bucket.
- The issue list, each entry with its component, pattern, and tokens at stake.
- The ranked removals, each with an estimated token delta and, where capability is lost, what is lost.
- The total reclaimable, absolute and as a share of current standing cost.
- Every role that was not measured, named as not measured. A report that silently omits a role reads as a complete audit.

## Common pitfalls

- Ranking components by body size and calling the result a context audit. Body size is on-demand-cost; the always-cost sits in the descriptions and schemas.
- Reporting one "tokens" number per component, which hides the distinction the whole audit turns on.
- Counting a component twice because two routes reach it, or counting one the harness never loads.
- Shrinking a description past the point where it still routes. A capability that stops being selected costs nothing and delivers nothing, and the failure is silent — it looks like a capability that simply never triggers. *(Authored.)*
- Removing a component because nothing references it, when the real defect is that nothing routes to it. Unreferenced and useless are different findings with different fixes: add the reference, or remove the component.
- Quoting percentages without stating the window they are a share of, so the report stops being true the moment the model changes.
- Re-auditing with a different estimator than the baseline used, and reading the difference as progress.
- Treating the baseline as the whole story when most of a session's context goes to tool output and file reads.

## Examples

**Ranking by the wrong price.**

Wrong: "The planning capability is the largest file in the configuration at 600 lines — cut it first."

Right: the 600 lines are on-demand-cost, paid only when planning is selected. Its always-cost is a 60-word description, and *that* is the number the audit reports for it. The ranked first cut is instead the tool integration registering twelve schemas that are present on every request, none of which the current work uses.

**Report shape.** *Numbers below are invented for illustration, not measurements — the tool-schema figure is simply the ~500-token seed multiplied by the component count, which is what an uncalibrated estimate looks like.*

| Role | Components | Always-cost | On-demand-cost |
| --- | --- | --- | --- |
| Standing instruction text | 2 | ~1,200 | — |
| Capability descriptions | 28 | ~6,200 | ~74,000 |
| Tool schemas | 87 | ~43,500 | — |

Ranked: remove three wrapper integrations (~27,000); delete the duplicated review rule stated in both instruction files (~400); shorten nine descriptions to routing minimum (~1,900).

**Pre-expansion check.** "Is there room for four more tool integrations?" — estimated at the ~500-token seed against a measured baseline, the projection is roughly +10,000 tokens of always-cost. The answer returned is the projected baseline, its share of the named window, and the prerequisite: which existing integrations would offset it, and what capability that would cost.

## Provenance

- **Sourced:** the four-phase ordering, the three-bucket classifier and its referencing test, the always-cost versus on-demand-cost distinction, tool schemas as the dominant term, the wrapper-tool removal criterion, the report's composition, and the forward-looking pre-expansion mode.
- **Chosen defaults, no derivation:** `words × 1.3`, `characters ÷ 4`, and ~500 tokens per registered tool. The source asserts all three without showing a derivation, and they are carried here only as calibration seeds.
- **Not carried:** the source's fixed context-window figure (a parameter, not a constant); its worked audit numbers, which are shaped like measurements but were illustrative; and any threshold for "too many" components or a tolerable share of the window, none of which was derived anywhere in the source.
- **Authored, not sourced, and marked at each site:** verifying per-role loading behavior instead of assuming it; the same-estimator rule for re-audits; the ordering of the removal ladder; the unreferenced-versus-useless distinction; and the too-short-to-route pitfall.
- **Deliberately unquantified:** the reliability cost of moving an instruction out of the always-loaded surface. The claim is stated as an assertion because the only measurement-shaped figures available for it were unattributed.
