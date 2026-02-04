---
name: adr-madr-system
description: "Create, review, and maintain Architecture Decision Records (MADR) as individual files plus an ADR index. Focuses on decision drivers, options, consequences, and supersedes semantics so accepted ADRs remain immutable."
category: architecture
---

# ADR MADR System

Create high-quality ADRs (MADR style) as separate files, and keep a lightweight index for discoverability.

This skill defines explicit outputs for each step, reduces merge conflicts, and preserves decision history via **superseding** instead of rewriting accepted ADRs.

## Use this skill when

- Making a decision that affects architecture boundaries, persistence, auth/security posture, API style, reliability/SLOs, scaling, or major vendor/tool choices.
- Changing a previously accepted architectural decision (create a new ADR that supersedes the old one).

Trigger phrases:
- "We need to decide between X and Y."
- "Should we adopt <tech/vendor>?"
- "We’re changing the architecture for <system>."
- "Document the architecture decision for <topic>."

## Do not use this skill when

- Capturing minor implementation notes, routine refactors, or small patches with no architectural impact.

## Defaults (override if the repo already has conventions)

- ADR directory: docs/adr/
- ADR index: docs/adr/README.md
- File naming: `ADR-XXXX-short-title.md` (XXXX is zero-padded)
- Status lifecycle: Proposed -> Accepted -> Rejected/Deprecated/Superseded

## Workflow

### Step A: Decide if an ADR is required

Output: 3-5 bullets answering:
- What decision is being made?
- Why now (what triggered it)?
- What scope is affected?

Decision point:
- If the decision is cross-cutting or long-lived, proceed with an ADR.
- If it is a local implementation detail, stop and capture a brief note elsewhere.

### Step B: Pull inputs from the spec

Output: a short list of constraints and decision drivers with **links** to the spec/track/task artifacts.
- Constraints: must/must-not/should, deadlines, platform limits, compliance.
- Drivers: ranked priorities (cost, latency, operability, DX, security, time-to-deliver).

Decision point:
- If you cannot link to a source artifact, record the owner to confirm before acceptance.

### Step C: Consider options (minimum 2)

Output: 2-4 viable options with pros/cons evaluated against the drivers.
If there is only 1 realistic option, explicitly justify why.

### Step D: Record the decision

Output: a MADR document that includes:
- Decision and rationale tied to drivers
- Consequences (positive and negative)
- Risks and mitigations
- Follow-ups (implementation notes or tasks)

Use `references/templates.md` for templates.

### Step E: Apply governance (supersedes, don’t rewrite)

Rule: **Do not edit accepted ADRs to change the rationale/decision.**
- If changing direction: create a new ADR and mark it as superseding the old one.
- The old ADR remains as historical context.

### Step F: Update the ADR index in the same change

Output: update docs/adr/README.md to include the new/updated ADR metadata and links.
Use `references/index-format.md` for the index table format and update rules.

### Step G: Self-check pitfalls

Output: a short checklist of “done” confirmations.
- Every section in the template is present (no missing headings).
- Decision drivers are ranked and referenced in the rationale.
- Consequences include at least one tradeoff.
- Supersedes section present when replacing an accepted ADR.

## Output contract (always report)

- New or updated ADR file path(s)
- Updated ADR index path
- Link(s) between ADR(s) and spec/track/task artifacts
- If superseding: old ADR ID and new ADR ID

Reporting format:
- ADRs: <list of ADR file paths>
- Index: <ADR index path>
- Links: <spec/track/task references>
- Supersedes: <old ADR ID -> new ADR ID or "none">

## Quality gates

Before finalizing, check `references/quality-gates.md` and `references/README.md` for the latest guidance.

## SDD integration notes

When the ADR is accepted, update the relevant spec/track/task artifact to link to it (and ensure the ADR links back). See `references/sdd-integration.md`.

## Verification

- If you run any script from `scripts/`, report the command(s) and result(s).
- Do not claim completion without verification output when scripts are used.

## Optional scripts

- `scripts/new_adr.sh` scaffolds a new MADR file and updates the ADR index block.
- `scripts/update_index.sh` rebuilds the ADR index block deterministically from ADR files.
- `scripts/validate_adr.sh` validates that a single MADR file contains required sections.
- `scripts/validate_repo.sh` validates all ADRs in a repo and checks index coverage.

Script requirements:
- POSIX shell, `awk`, `sed`, `grep` (or `rg`), `date`, and standard coreutils.
- No network access required.

Script usage:
- `ADR_DIR=docs/adr ADR_INDEX=docs/adr/README.md ./adr-madr-system/scripts/new_adr.sh "Use PostgreSQL"`
- `ADR_DIR=docs/adr ADR_INDEX=docs/adr/README.md ./adr-madr-system/scripts/update_index.sh`
- `./adr-madr-system/scripts/validate_adr.sh docs/adr/ADR-0001-sample.md`
- `ADR_DIR=docs/adr ADR_INDEX=docs/adr/README.md ./adr-madr-system/scripts/validate_repo.sh`

Script verification:
- Capture script output and include it in the final report when used.

## Common pitfalls

- Editing accepted ADRs instead of superseding them.
- Missing links back to the motivating spec/track/task.
- Skipping decision drivers and ending up with untraceable rationale.
- Forgetting to update the ADR index in the same change.

## Examples

Trigger test prompts:
- "We need to decide between Kafka and SQS for event delivery."
- "Document the architecture decision for multi-tenant storage isolation."

Example output (reporting format):
- ADRs: docs/adr/ADR-0007-event-delivery.md
- Index: docs/adr/README.md
- Links: `docs/specs/eventing.md#L40`
- Supersedes: `none`
