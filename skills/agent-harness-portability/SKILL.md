---
name: agent-harness-portability
description: "Tests whether a skill or instruction corpus is harness-agnostic instead of merely asserting it: a per-target disposition pass over the axes on which agent harnesses differ, source-token leakage checks, and a defined repair for each failure. Use when authoring or auditing a portable skill, porting a corpus to another agent, or reviewing an untested portability claim."
metadata:
  category: ai
---
# Agent Harness Portability

Provides the pass that turns "runs on any agent" into a result: a per-axis disposition table across the declared targets, checks that can fail, and a defined repair for each failure. The claim is normally asserted once and never tested, and nothing errors when it is wrong — a wrong instruction is still readable, so the agent reads a tool it does not have or a path that does not exist, and improvises.

## Use this skill when

- A skill, instruction file, or prompt corpus claims to work across agents and nothing has ever checked that.
- Porting a corpus to a target it was not authored against, or adding a target to a corpus that already claims multi-agent support.
- Reviewing an instruction set that names tools, file paths, or capabilities — the three things that do not survive a change of agent.
- A corpus is read directly by several agents rather than compiled per agent, so every divergence has to be kept out at authoring time.
- Auditing a portability matrix that carries no target versions and no dates.

## Do not use this skill when

- The corpus targets exactly one agent and always will. Naming that agent's tools and paths is precision there, and generalizing them away costs the reader information.
- The question is one product's value — its install root, its frontmatter dialect, its description cap. This supplies the axis and the probe; the value is a lookup in that product's own documentation, and a fact with an expiry date.
- The failure is inside one agent at run time: a script that errors, an absent file, a permission denial. That is debugging, and portability is not implicated.
- The work is wording, examples, or reasoning controls aimed at a single model's behavior.
- The artifact carries no agent-directed prose — data, assets, generated output. There is nothing to leak and no vocabulary to rewrite.

## Required inputs

- Targets: every agent the corpus must run on, each with the product version being verified against and a pointer to where that product documents its own integration surface.
- The source agent: the one the corpus was actually authored against. Where none was declared, one is still implied by the tool names, paths, and file names already in the text — name it before checking anything.
- Distribution mode: **transformed per target** (a build emits one tree per target) or **read as authored** (one tree, every agent reads the same bytes). Transformed corpora repair by rewriting the output; read-as-authored corpora repair by never introducing the divergence, and have no later step that could catch one. *(The read-as-authored branch is authored, not sourced: the source material assumes a build step exists.)*
- The corpus, plus the list of items whose subject is an agent — those get excluded per target rather than rewritten.

## Axes of variation

Fourteen, recovered from one team's port of a single corpus to ten targets, plus at least one declared parameter whose meaning was not recoverable from that source — a floor, not a closed set. Probe question, verification method, and silent-failure signature per axis: `references/axis-probes.md`.

| # | Axis | What differs across targets |
| --- | --- | --- |
| 1 | Invocation name | The command that identifies the agent, which is not always the agent's name |
| 2 | User-scope root | Where user-level items are installed |
| 3 | Project-scope root | Where repository-level items are installed |
| 4 | Subdirectory prefix | The dot-directory the target's other files hang off |
| 5 | Root indirection | Whether roots are literal paths or resolved through an environment variable |
| 6 | Frontmatter dialect | Allowlist versus denylist, permitted keys, renames, injected keys, description cap and overflow behavior |
| 7 | Sidecar manifest | Whether the target wants an extra machine-readable index emitted alongside the corpus |
| 8 | Item exclusions | Which items are meaningless, recursive, or self-referential on this target |
| 9 | Path rewrites | Literal string replacements over body text, order-sensitive |
| 10 | Tool vocabulary | What the target's tools are called, and which have no equivalent at all |
| 11 | Capability sections | Which sections the target cannot perform, so they are deleted rather than reworded |
| 12 | Companion assets | Non-instruction files the corpus depends on and that must be installed with it |
| 13 | Materialization | How the tree is placed: copy, link, or generated output |
| 14 | Cross-agent boundary | Attribution, and the instruction handed to a foreign agent that shares the checkout |

## Workflow

1. Name the source agent, the targets, and the distribution mode. Record each target's version and integration-doc pointer. Output: a target list where every entry carries a version and a date.
2. Fill the disposition table: one row per axis, one column per target, exactly one of `verified`, `default — checked`, or `unknown` in every cell. Output: a table with no blank cell.
3. Build the leakage token list from the filled table — the source agent's path roots, its agent-instruction file name, every tool name in its vocabulary including the ones no rewrite table mentions, and the path roots of every other target the corpus names in prose. Output: an explicit token list, one entry per literal string that either got rewritten or did not.
4. Run one check per token, parameterized over the target list rather than over named targets, so a target added later cannot arrive unchecked. For a transformed corpus, each check greps the generated tree for the token — `grep -rn "<token>" <target-tree>` — and any hit is a failure. For a read-as-authored corpus the same list becomes a lint over the source, where any hit is an authoring defect, since no later step exists to catch it. Output: pass or fail per token, with the hits quoted.
5. Close each failure with a repair move below, then re-run step 4 against the repaired output. Output: repairs applied, one line each, naming the axis and the move.
6. Stop and report. While any cell reads `unknown`, the corpus is not described as agent-agnostic — name which targets are verified and which are not.

## Constraints

- **No blank cells.** Silence is a claim: an axis left unstated asserts that the target matches the default, with the same truth conditions as an axis stated out loud. The trap this pass exists to catch is a two-line target entry that reads "this target needs nothing" and means "nobody checked this target". *(Evidence from one registry read in 2026-08: half its targets declared no tool vocabulary at all and two declared nothing but a name, so each shipped the source agent's tool names verbatim while presenting as configured.)*
- **`unknown` blocks the claim, and the report names the claim it blocks.** "Verified for A and B, unverified for C" is a shippable result; "agent-agnostic" with an unknown cell is not.
- **One canonical phrasing for tool references** across the corpus, with the rewrite table's key set as the lint's allowlist. Any other phrasing is a defect, not a stylistic variant.
- **Any key a target's config injects must also appear in that target's own allowlist.** Injection and filtering are separate passes, and the allowlist is authoritative.
- **Every security-relevant key carries an explicit per-target disposition**: mapped to the target's equivalent control, enforced by a different mechanism, or an accepted and recorded loss. "Absent from the allowlist" must never be how that decision gets made.
- **No two targets resolve to the same name, subdirectory, or install root.** A collision overwrites one tree with the other silently, and is cheap to assert once.
- **Every target entry carries the version verified against and the date.** A portability matrix with no dates is indistinguishable from one that has rotted.

## Repair moves

Six ways to close a failing cell, plus one refusal:

1. **Rewrite the path** — literal replacement over body text, ordered longest-prefix-first. Shortest-first, a general entry consumes the prefix of a specific one and the special-cased sub-path silently lands in the wrong place.
2. **Rename the tool** — where the target has a clean one-to-one equivalent.
3. **Degrade the tool reference to prose** — name the action instead of the tool.
4. **Suppress the section** — delete it wholesale where the capability is structurally absent on the target. Rewording a section the target cannot perform produces a plausible instruction that cannot be followed.
5. **Exclude the item** — drop an item whose subject is the target agent itself, since self-delegation is a no-op or a regress.
6. **Re-express the frontmatter key** — translate a portable marker into the target's own vocabulary, or inject the target's equivalent key.
7. **Refuse** — fail the build rather than emit a silently degraded artifact. Not a repair: the correct outcome when no repair preserves meaning.

### Tool references: the ladder

1. **Exact rename**, where the target has a direct equivalent.
2. **Rename with collapse**, where two source tools map onto one target tool. Cost: any instruction whose meaning turns on the collapsed distinction — create versus modify — becomes ambiguous after the rewrite, and nothing detects it.
3. **Capability prose** — "run this command", "create this file", "dispatch a subagent". Correct on every target, including targets not yet on the list.
4. **Prose for an absent capability** — "search for", "find files matching". The only rung available when the target has no equivalent at all: name the intent.

Rung 3 is the default for a corpus that must not be re-audited per target, and the only rung available to a read-as-authored corpus. *(Inference: the source shows independently written vocabularies converging on rung 4's phrasings, but ranks no rung.)*

### Rewrite phrases, not tokens

A rewrite table keyed on a bare tool name corrupts every other use of that word — shell prose, code, file names — so its keys are sentence fragments instead. The consequence is load-bearing: **the corpus is portable only in the phrasings the table already knows.** "Use the X tool" is rewritten while "with the X tool" ships verbatim, so the rewrite covers less than it appears to, and the gap is invisible in the table. This is what makes one canonical phrasing an authoring contract rather than a style preference. *(Inference from the mechanism; the source states the keying, not its consequence.)*

## Decision points

- **Extend the rewrite list or replace it?** Extend when the derived defaults are right and the target merely needs more entries; replace only when the derivation itself is wrong for that target. Offer both as distinct operations and make requesting both an error rather than a merge — the merge semantics the caller assumed cannot be recovered from the call.
- **Rename the tool or write prose?** Rename on a clean one-to-one equivalent. Collapse only after confirming no instruction depends on the distinction being collapsed. Otherwise prose.
- **Suppress the section or let it degrade at run time?** Suppress when the capability is structurally impossible on the target. Let it degrade when the section already handles the capability's absence at run time — suppressing it there also removes it from targets where the capability is present but optional.
- **Which default for a capability group?** Follow prevalence: active-by-default with an opt-out when most targets have the capability, suppressed-by-default with an opt-in when most lack it. Backwards, and the common case becomes the one that must be remembered.
- **Cap overflow: fail, truncate, or warn?** Fail when the capped field is what the target uses to select the item at all — a truncated description degrades routing invisibly, and the item appears to simply never trigger. Truncate only where the field's tail is decorative. *(The ranking is authored; the source records only that one target chose to fail.)*
- **Allowlist or denylist frontmatter?** Denylist on the authoring side, where the key set is controlled and what to strip can be named outright. Allowlist for a foreign target, so a key added later cannot leak into a target that never agreed to it. The allowlist's cost is that every deliberately carried key must be added to every target's list, which is exactly how security markers get dropped.

## Common pitfalls

- Deriving the project-scope root from the user-scope root. They diverge in practice; resolve two paths per target, independently.
- Rewriting only the source agent's paths. A corpus documenting cross-agent usage carries other targets' paths in its prose, and those ship verbatim into the target's tree.
- A stale generated tree passing the checks by being old. Regenerate from current source before a check result counts.
- A foreign agent sharing the checkout, reading the other agent's instruction tree as ordinary repository content and following prompt templates never addressed to it. Attach a boundary instruction — and treat it as the weakest available control, since it is a request rather than a mechanism. It belongs alongside a real boundary (not installing both trees, or scoping the foreign agent's read root), never instead of one. *(The ranking is authored; the source offers only the prose instruction.)*
- Reporting an axis as handled because a rewrite exists for it, without checking the rewrite's coverage. A table with three of seven tool names, or one of three phrasings, presents as a solved axis.

## Examples

Tool reference, read-as-authored corpus:

- Wrong: "Use the `Shell` tool to run the suite, then use the `Search` tool to find the failing assertion", where those two names are the source agent's tool names. Two foreign tokens, one of them in a phrasing most rewrite tables never learned, in a corpus that has no rewrite step at all.
- Right: "Run the test suite, then search the output for the failing assertion." Rungs 3 and 4: correct on every target, including ones not yet on the list.

Disposition table (illustrative; the targets and values are placeholders, not claims about any product):

| Axis | Target A | Target B |
| --- | --- | --- |
| Project-scope root | verified — v3.2, 2026-08 | `default — checked` |
| Frontmatter dialect | verified — allowlist, two keys | `unknown` |
| Tool vocabulary | verified — prose only | `unknown` |
| Description cap | verified — capped, fail on overflow | `unknown` |

Target A ships as verified. Target B ships as unverified, and the corpus is described that way — the wrong version of this table is the one where Target B's column is empty and the corpus is announced as agent-agnostic.

## Output contract

Returns a portability report carrying:

- The target list, each entry with the version verified against and the date of that verification.
- The disposition table, no blank cells.
- Check results: the token list, and pass or fail per token with any hits quoted.
- Repairs applied, one line each: axis, move, and what changed.
- Residual `unknown` cells and the claim each one blocks.

## Provenance

- Sourced: the axis enumeration, the repair moves, the phrase-keyed rewrite mechanism, extend-versus-replace as mutually exclusive operations, the prevalence rule for capability-group defaults, and the verification half — leakage grep, checks parameterized over the target list, cross-target root uniqueness, freshness of generated trees. All of it comes from one team's multi-target port of a single corpus, read in 2026-08.
- Not carried: that team's per-target values — install paths, frontmatter dialects, tool vocabularies, and a stated description cap whose number the source neither derived nor dated. Those are one product's undated assertions about third-party agents; the axes transfer, the values do not.
- Authored or inferred, not sourced, and marked at each site: the read-as-authored distribution branch; the consequence drawn from phrase-keyed rewriting, that a corpus is portable only in the phrasings the table knows; the ranking of prose over rename as the default rung; fail-over-truncate as the default cap behavior; the ranking of a boundary instruction as the weakest available control; and the negative-control step for each check in `references/verification-harness.md`.

## References

- `references/README.md`
- `references/axis-probes.md`
- `references/verification-harness.md`
