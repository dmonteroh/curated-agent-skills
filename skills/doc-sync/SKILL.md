---
name: doc-sync
description: "Reconciles a repository's documentation against a change before it merges: audits every doc file against the branch diff, applies factual corrections without asking, escalates narrative and security edits, flags architecture-diagram drift without touching the diagram, and guards changelog entries and version bumps. Use when a branch is code-complete and its docs must match what shipped before review or merge."
metadata:
  category: docs
---
# Doc Sync

The posture is the inverse of writing documentation. Writing is a creative job that stops often to ask what to say; reconciliation is a mostly autonomous job over a narrow factual surface that refuses to touch anything else. Getting the split wrong in either direction is the failure this pass exists to prevent: an agent that asks about every corrected file path wastes the review, and an agent that rewrites an architecture doc's rationale because the diff "seemed to contradict it" has silently changed what the project claims about itself.

## Use this skill when

- A branch is code-complete and its documentation has to match what shipped before the pull request is reviewed or merged
- A change renamed, moved, split, or deleted public surface, and docs elsewhere in the repo still describe the old shape
- A changelog entry exists for this branch and needs to be checked and polished without being rewritten
- A version file was already bumped on this branch and nobody has checked whether it still covers everything the branch contains
- Architecture diagrams exist in the repo and the change touched the entities they name

## Do not use this skill when

- The job is to author documentation that does not exist yet. This pass reports a missing document as debt; it never generates one, and pointing it at an empty doc set produces a debt list, not docs.
- There is no change in flight. A periodic freshness audit has no diff to anchor "factually stale" on, so every finding becomes a judgment call — which is exactly the class of decision this pass declines to make alone.
- The changelog entry has to be written from scratch. This pass polishes and scores an entry that already exists, because that entry was derived from the actual diff and is the source of truth for what shipped.
- The whole point of the session is to rewrite a doc's narrative core — positioning, design philosophy, the security model. Those are stop-list items even mid-run; a session dedicated to them is not this pass.
- The change already merged and the ask is release communication (an announcement, an upgrade guide). That is authoring for an audience, not reconciliation against a diff.

## Autonomy split

Three lists govern every step below. They are what makes the pass repeatable across runs instead of renegotiated each time.

**Do not stop — apply these directly:**

- Factual corrections the diff plainly warrants
- Adding an entry to an existing table or list
- Paths, counts, version numbers, project-structure trees
- Stale cross-references between docs
- Minor changelog wording
- Marking a tracked TODO complete where the diff is clear evidence
- Cross-doc factual inconsistencies, such as one doc naming a different version than another

**Stop and ask for:**

- Narrative or philosophical text: positioning, design rationale, the "why" passages of an architecture doc
- Anything describing the security model
- Removing a section, or any removal beyond a single stale fact
- A rewrite large enough to change what a section says
- The version bump decision
- New TODO items to add
- Cross-doc contradictions that are narrative rather than factual

**Never do, and do not ask for permission to do:**

- Regenerate, replace, or reorder a changelog entry — polish wording only, and preserve every entry
- Bump the version without an explicit answer to the version question
- Overwrite the changelog with a whole-file write; every changelog change is an exact-match replacement of the specific wording being polished

**Where the escalation line falls.** A change escalates when it alters what a section *claims*, not when it touches many characters: correcting five stale facts scattered through a paragraph is autonomous, while rewriting one sentence so the section now means something different is not. The source's operational proxy is roughly ten changed lines within a single section — a chosen default with no derivation given for it; use it as a starting calibration for "large rewrite", never as a measured boundary.

**When no human is reachable** (*authored, not sourced* — the source assumes an interactive session and defines no degraded mode): apply the do-not-stop set, leave every stop-list item unapplied, and report each one as an unresolved decision carrying the evidence needed to settle it. Never promote a stop-list item to autonomous on the grounds that nobody is there to answer.

## Workflow

**1. Establish the comparison base.** Determine which branch this change targets, or the repository's default branch if no pull request exists yet. Abort if the working branch *is* the base branch: there is no diff, and the pass would otherwise report a clean bill of health it never checked.

**2. Gather what changed.** Take the change statistics, the commit list, and the changed-file list for the branch against that base.

```
git diff <base>...HEAD --stat
git log <base>..HEAD --oneline
git diff <base>...HEAD --name-only
```

Classify the changes into new features, changed behavior, removed functionality, and infrastructure. Removals need deliberate attention: nothing new appears in a doc to prompt the edit, so a deleted command keeps its README entry until someone goes looking for it.

**3. Enumerate the doc surface.** Discover documentation files by walking the repository, excluding vendored and dependency trees. Do not work from a fixed list of canonical filenames — a fixed list misses generated docs, per-package docs, and command-specific docs, which are exactly the ones nobody remembers to update.

**4. Audit each file against the diff**, using the questions below and applying the autonomy split to every finding.

| File | What to check against the diff | Posture |
| --- | --- | --- |
| README | Does it describe every feature and capability visible in the diff? Are install and setup steps still consistent? Are examples, demos, and troubleshooting steps still valid? | Autonomous on facts; the introduction and project positioning are stop-list. |
| ARCHITECTURE | Do component descriptions and diagrams match the current code? Are the design decisions and "why" passages still accurate? | Conservative: change only what the diff plainly contradicts. These docs describe slow-moving structure, so an apparent mismatch is more often the doc being right about intent than the doc being stale. |
| CONTRIBUTING | **New-contributor smoke test:** walk the setup instructions as a brand-new contributor. Are the listed commands accurate? Would each step actually succeed? Do the test-tier and workflow descriptions match the current infrastructure? | Fix commands and paths directly; escalate workflow narrative. Flag anything that would fail or confuse a first-timer even if it is not strictly wrong. |
| The repository's agent-instructions file, whatever it is named | Does the project-structure section match the real tree? Are the listed commands and scripts accurate? Do the build and test instructions match the package manifest? | Autonomous on facts. |
| Every other markdown file | Read it, establish its purpose and audience, then check whether anything in the diff contradicts what it says. | Follows the content: facts autonomous, narrative escalated. |

Read the full current text of a file before editing it — the file's own diff is not enough, because reconciliation is about what the file now claims, not about what this branch touched in it.

**5. Apply the autonomous set,** file by file, and emit a one-line summary per file naming *what specifically* changed. "Updated README" is not reviewable; see Examples.

**6. Detect architecture-diagram drift.** Extract the entity names — modules, services, data flows — from any ASCII diagram or diagram-source block in the docs, and cross-reference each against the diff. Flag every entity that was renamed, split, removed, or moved in the code. **This is advisory only: never auto-edit a diagram, in either ASCII or diagram source.** Updating one correctly requires judgment about layout and about which relationships still hold, and an edit that satisfies a rename while destroying the diagram's shape is worse than the stale name. Report the drift as debt and let a human redraw.

**7. Reconcile the changelog.** Skip if the branch did not touch it. Otherwise work under the never-clobber rules and the sell test below.

**8. Run the cross-doc consistency and discoverability pass.** Compare README's feature list against the agent-instructions file's description of the same surface; ARCHITECTURE's component list against CONTRIBUTING's project-structure description; and the changelog's latest version against the version file. Then check that every documentation file is reachable from README or from the agent-instructions file — a doc nothing links to is a doc nobody reads, so flag it. Fix clear factual contradictions; escalate narrative ones.

**9. Reconcile the tracked TODO list,** if one exists. Mark an item complete only on clear diff evidence, and be conservative — a related file changing is not the item being done. Where an item references files or components this branch substantially changed, ask whether to update, complete, or leave it. Finally, sweep the diff for new `TODO`, `FIXME`, `HACK`, and `XXX` comments and ask about each one that represents real deferred work rather than an inline note; adding items is a stop-list action.

**10. Settle the version question,** per the section below.

**11. Run an independent review pass,** per the section below.

**12. Publish.** Stage the documentation files by name and commit them as one change; never stage the working tree wholesale. Then emit the output contract, and write the debt block into the pull request description by replacing an existing block of the same name or appending one if none exists — read the current description first so a re-run updates rather than duplicates.

## Changelog: never clobber, then sell-test

**Never regenerate an entry.** The rule is incident-derived: the source records a real occurrence of an agent replacing existing changelog entries when it should have preserved them, and states this guardrail as the response. The mechanics that make it hold: read the whole file before touching it, change wording only by replacing an exact matched substring, never delete or reorder or replace an entry, and never write the file wholesale. If an entry looks wrong or incomplete, ask; do not silently fix it. The entry was written from the actual diff and is the record of what shipped, so a "cleaner" regenerated version is a different claim about the release.

**Sell test.** Score each entry the branch added or touched, one point per reader question it answers:

- **What changed?** It names the feature or the fix.
- **Why should the reader care?** It states the impact — what is now possible, or what pain is gone.
- **How is it used?** It gives a command, a flag, or a link to the document that shows it.

Three questions, so the scale runs 0–3 and nothing else contributes to it. **The pass mark — rewrite anything below two, treat three as the target — is a chosen default carried from the source with no derivation behind it.** The qualitative rule it encodes is the part to keep: an entry that only names what changed is a commit message with a bullet in front of it.

Rewrites stay inside the never-clobber rules: adjust the wording of the existing entry, and ask first if the rewrite would change what the entry claims shipped. Lead with what the reader can now do rather than with implementation detail. Move contributor-facing changes into their own subsection instead of leaving them in the user-facing list.

## Version absorption check

Skip silently if the repository has no version file.

If the version was **not** bumped on this branch, ask, recommending no bump for documentation-only changes: bump the patch level if docs ship alongside code changes, bump the minor level if this is a significant standalone release, or skip.

If the version **was** already bumped, do not treat that as done. Read the changelog entry for the current version and list what it describes, then compare that against the branch's full change set. If significant changes — new commands, new features, major refactors — are absent from that entry, ask whether they warrant their own version, an addition to the existing entry, or nothing for now.

This is the case an unprompted pass misses: a bump made for feature A silently absorbing feature B, so two changes ship under one version's notes and the second has no release notes at all.

## Independent review pass

Run a second pass with fresh context — a separate agent, or a second model where one is available — over the docs this pass touched plus any doc whose claims the diff affects. Do not hand it a fixed filename list, for the same reason step 3 does not use one.

Ask it for exactly four things:

- Doc claims that no longer match the code
- New public surface — commands, flags, config keys, endpoints — that shipped undocumented
- Stale examples, paths, counts, and version numbers
- Changelog entries that over- or under-sell what shipped

**Apply posture: informational, never auto-applied, and never discarded.** Present the findings, then ask once how to handle all of them — apply them all, skip them, or decide per finding — and make the approved edits directly. Zero findings is a reportable result and should be reported as one. If the answer is skip, the findings still go into the output, so a declined finding stays visible instead of evaporating.

## Constraints

- The heuristics are generic and depend on no particular project layout; a repository missing any canonical file simply skips that file's checks.
- Anything this pass writes is aimed at a competent reader who has not seen the code: concrete, specific, and free of internal shorthand.

## Examples

**Per-file change summaries.**

Wrong: `README.md: updated.`

Right: `README.md: added the --retry-budget flag to the options table; corrected the command count from 9 to 10.`

The second is auditable against the diff without reopening the file; the first is not.

**A changelog entry under the sell test.**

Scores 1 — names the change, gives no reason to care and no way to use it:

> Refactored the export pipeline to use a worker pool.

Scores 3 — what changed, why it matters, how to use it:

> Scheduled exports now run in parallel, so a long nightly export no longer blocks the next one. Turn it on with `--parallel-export`.

**Version absorption.**

Wrong: the version file already reads 2.4.0, so the version step reports "already bumped" and moves on. The branch also added an import command that no entry mentions, and it ships with no release notes at all.

Right: read the 2.4.0 entry, compare it against the branch's full change set, notice the import command is uncovered, and ask whether it deserves its own version or an addition to the existing entry.

## Output contract

- One line per file changed, naming what specifically changed in it
- A status line per canonical documentation file: updated (with what), current, wording polished, version not bumped, version already bumped, or absent
- A debt block in the pull request description covering undocumented new surface, drifted diagrams, and gaps this pass declined to fill — each with one line stating what is missing. Generating those documents is out of scope for this pass and belongs to a separate job.
- Every unresolved stop-list item, with the decision each one needs and the evidence for it
- When nothing needed changing: "All documentation is up to date", and no commit
