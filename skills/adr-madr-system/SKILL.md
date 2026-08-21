---
name: adr-madr-system
description: "Create, review, and maintain Architecture Decision Records (MADR) as individual files plus an ADR index when documenting or superseding architectural decisions. Focuses on decision drivers, options, consequences, and supersedes semantics so accepted ADRs remain immutable."
metadata:
  category: architecture
---
# ADR MADR System

Defines explicit outputs for each step, reduces merge conflicts, and preserves decision history via **superseding** instead of rewriting accepted ADRs.

## Use this skill when

- Making a decision that affects architecture boundaries, persistence, auth/security posture, API style, reliability/SLOs, scaling, or major vendor/tool choices.
- Changing a previously accepted architectural decision (create a new ADR that supersedes the old one).
- Shelving a decision that is sound and reviewed but blocked by something outside the team's control (table it instead of rejecting it or leaving it proposed).
- Noticing mid-task that one of the decisions above has just been settled in passing, without anyone asking for a record (Step A).

## Do not use this skill when

- Capturing minor implementation notes, routine refactors, or small patches with no architectural impact.

## Defaults (override if the repo already has conventions)

- ADR directory: docs/adr/
- ADR index: docs/adr/README.md
- File naming: `ADR-XXXX-short-title.md` (XXXX is zero-padded)
- Status lifecycle: Proposed -> Accepted -> Rejected/Deprecated/Superseded; Tabled is a distinct, reversible status (Step F)

## Required inputs

- Decision topic and scope.
- Known constraints and decision drivers (with source artifacts if available).
- Existing ADR list or index location (or confirmation to use defaults).
- Stakeholders or approvers if required by repo conventions.

## Constraints and conventions

- Follow any existing ADR templates, numbering, or status policies in the repo.
- Keep ADR and index paths consistent within the same change.
- Prefer repo-local paths or already-provided URLs; do not assume network access.

## Workflow

### Step A: Decide if an ADR is required

Output: 3-5 bullets answering:
- What decision is being made?
- Why now (what triggered it)?
- What scope is affected?

Decision point:
- If the decision is cross-cutting or long-lived, proceed with an ADR.
- If it is a local implementation detail, stop and capture a brief note elsewhere.

**Explicit and implicit decision moments carry different obligations.** A decision reaches Step A in one of two ways, and conflating them is how decisions go unrecorded:

- *Explicit* — recording the decision was requested, or someone asked why a past choice was made. Proceed with the workflow as asked.
- *Implicit* — a decision in one of the categories under "Use this skill when" got settled as a by-product of other work: options were weighed, one was concluded on with a rationale stated in passing, and nobody asked for an ADR. This is the common shape and the one that gets lost.

Decision point for an implicit moment:
- Name the decision that appears to have been settled, the alternatives that were on the table, and propose recording it.
- Do **not** create the ADR file unprompted. An unrequested ADR spends reviewer attention and freezes a choice that may still have been exploratory.
- Do not stay silent either. An unsurfaced decision is one nobody records, which is the failure this skill exists to prevent.
- If confirmation does not come, stop and leave no partial file behind.

### Step B: Pull inputs from the spec

Output: a short list of constraints and decision drivers with **links or paths** to spec/track/task artifacts (repo-local preferred).
- Constraints: must/must-not/should, deadlines, platform limits, compliance.
- Drivers: ranked priorities (cost, latency, operability, DX, security, time-to-deliver).

Decision point:
- If no link to a source artifact is available, record the owner to confirm before acceptance.

### Step C: Consider options (minimum 2)

Output: 2-4 viable options with pros/cons evaluated against the drivers.
If there is only 1 realistic option, explicitly justify why.

### Step D: Record the decision

Output: a MADR document that includes:
- Title stated as the question and its answer, not a bare topic label, so the outcome is scannable without opening the body
- Decision and rationale tied to drivers
- Consequences (positive and negative), tagged to the review pass that surfaced a point when that source is known
- Risks and mitigations
- Follow-ups (implementation notes or tasks)

Use `references/templates.md` for templates.

### Step E: Apply governance (supersedes, don’t rewrite)

Output: supersedes section populated when replacing an accepted ADR, with the old ADR left intact.

Rule: **Do not edit accepted ADRs to change the rationale/decision.**
- If changing direction: create a new ADR and mark it as superseding the old one.
- The old ADR remains as historical context.

### Step F: Table a decision instead of leaving it vague, when it is blocked

Output: an ADR with status `Tabled` — sound and reviewed, but blocked by something outside the team's control. Distinct from `Rejected` (permanent, no path back) and from staying `Proposed` (nothing was settled yet). Tabling turns a blocked-but-sound decision into a resumable artifact instead of either a deleted investigation or a vague "someday" note.

Required in the ADR body:
- **The blocker, cited concretely.** Point at falsifiable, external, re-checkable evidence, not an internal assertion that "this turned out to be hard" — a documented capability/API gap quoted from its source, a tracked upstream issue (numbered, with its current state), and, where a workaround might exist, a specific check that it was verified and does not clear the bar.
- **The cost of tabling.** State explicitly what was and wasn't spent (code written or not, research time, artifacts produced). That cost is what justifies keeping the tabled artifact intact instead of deleting it.
- **The settled sub-decisions, preserved, not just the pitch.** Keep the decisions that took real review effort to reach, not only the summary, so a future resumer does not re-litigate settled ground from scratch.
- **The un-tabling trigger, tied to something external and independently checkable.** Name the specific event that clears the blocker — an issue closing, a changelog entry, a released capability — not an open-ended "revisit later".
- **An ordered un-tabling checklist**, run only when the trigger fires, in exactly this sequence:
  1. Re-confirm the blocking assumption's real current shape. Read whatever changed (an updated API doc, a shipped capability, a closed issue's resolution), capture a concrete example of the new reality, and record it.
  2. Re-check that the original premise still holds under that reality — does what made the decision worth pursuing still apply in full, or only a narrower slice of it? If narrower, the pitch needs revisiting before implementation, not just the plan.
  3. Re-run the review that originally vetted the decision, against the *revised* plan, not the frozen one. Most prior findings should carry forward; adjust only what depended on the blocked capability's exact shape.
  4. If a second, independent review also vetted the original decision, re-run that one too, the same way: concerns tied purely to the now-resolved blocker should disappear, while concerns independent of it still apply and still need addressing.
  5. Only then execute the original plan.

  This order is load-bearing: re-verifying the blocker before the premise before the review(s) before execution prevents resuming work on top of an assumption that quietly changed shape while shelved.
- **Tabling is distinct from rejection**, even within the same document: alternatives considered and permanently declined carry no re-trigger and are not resumable; a tabled main path is. File the two under different statuses.

Template and worked structure: `references/tabling.md`.

### Step G: Update the ADR index in the same change

Output: update docs/adr/README.md to include the new/updated ADR metadata and links.
Use `references/index-format.md` for the index table format and update rules.

### Step H: Self-check pitfalls

Output: a short checklist of “done” confirmations.
- Every section in the template is present (no missing headings).
- Decision drivers are ranked and referenced in the rationale.
- Consequences include at least one tradeoff.
- Supersedes section present when replacing an accepted ADR.
- If tabled: blocker cited concretely, cost of tabling recorded, and an ordered un-tabling checklist present.

## Output contract

- New or updated ADR file path(s)
- Updated ADR index path
- Link(s) between ADR(s) and spec/track/task artifacts
- If superseding: old ADR ID and new ADR ID
- Verification commands/results when scripts are used

Reporting format:
- ADRs: <list of ADR file paths>
- Index: <ADR index path>
- Links: <spec/track/task references>
- Supersedes: <old ADR ID -> new ADR ID or "none">
- Verification: <commands/results or "none">

## Quality gates

Before finalizing, check `references/quality-gates.md` and `references/README.md` for the latest guidance.

## SDD integration notes

When the ADR is accepted, update the relevant spec/track/task artifact to link to it (and ensure the ADR links back). See `references/sdd-integration.md`.

## Optional scripts

- `scripts/new_adr.sh` scaffolds a new MADR file and updates the ADR index block.
- `scripts/update_index.sh` rebuilds the ADR index block deterministically from ADR files, preserving hand-maintained Tags cells.
- `scripts/validate_adr.sh` validates that a single MADR file contains required sections (accepts MADR-canonical heading variants).
- `scripts/validate_repo.sh` validates all ADRs in a repo and checks index coverage.

Script requirements:
- POSIX shell, `awk`, `sed`, `grep` (or `rg`), `date`, and standard coreutils.
- No network access required.

Script usage (run from the target repo root):
- `ADR_DIR=docs/adr ADR_INDEX=docs/adr/README.md sh <skill-folder>/scripts/new_adr.sh "Use PostgreSQL"`
- `ADR_DIR=docs/adr ADR_INDEX=docs/adr/README.md sh <skill-folder>/scripts/update_index.sh`
- `sh <skill-folder>/scripts/validate_adr.sh docs/adr/ADR-0001-sample.md`
- `ADR_DIR=docs/adr ADR_INDEX=docs/adr/README.md sh <skill-folder>/scripts/validate_repo.sh`

Script verification:
- Ensure the command exits with status 0 before claiming success.
- Capture script output and include it in the final report when used.
- If a script fails, stop and report the error output instead of continuing.

## Common pitfalls

- Editing accepted ADRs instead of superseding them.
- Missing links back to the motivating spec/track/task.
- Skipping decision drivers and ending up with untraceable rationale.
- Forgetting to update the ADR index in the same change.
- Filing a blocked-but-sound decision as `Rejected` (loses the resumable path) or leaving it `Proposed` indefinitely (loses the fact it was already decided) instead of tabling it.
- Tabling a decision without a concrete, external, re-checkable blocker — "this turned out to be hard" is not a citation.

## Examples

Example output (reporting format):
- ADRs: docs/adr/ADR-0007-event-delivery.md
- Index: docs/adr/README.md
- Links: `docs/specs/eventing.md#L40`
- Supersedes: `none`
