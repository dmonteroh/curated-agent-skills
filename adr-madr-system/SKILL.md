---
name: adr-madr-system
description: "Create, review, and maintain Architecture Decision Records (MADR) as individual files plus an ADR index. Optimized for spec-driven development and multi-agent workflows: enforces decision drivers, considered options, consequences, and \"supersedes\" semantics instead of editing accepted ADRs. Works standalone; if other skills exist, use them for domain/tech guidance, but keep ADRs as the decision source of truth."
category: architecture
---

# ADR MADR System

Create high-quality ADRs (MADR style) as separate files, and keep a lightweight index for discoverability.

This skill is designed for **spec-driven development (SDD)** and **multi-agent** work: it defines explicit outputs for each step, reduces merge conflicts, and preserves decision history via **superseding** instead of rewriting accepted ADRs.

## Use this skill when

- Making a decision that affects architecture boundaries, persistence, auth/security posture, API style, reliability/SLOs, scaling, or major vendor/tool choices.
- Changing a previously accepted architectural decision (create a new ADR that supersedes the old one).

## Do not use this skill when

- Capturing minor implementation notes, routine refactors, or small patches with no architectural impact.

## Defaults (override if the repo already has conventions)

- ADR directory: docs/adr/
- ADR index: docs/adr/README.md
- File naming: `ADR-XXXX-short-title.md` (XXXX is zero-padded)
- Status lifecycle: Proposed -> Accepted -> Rejected/Deprecated/Superseded

## Workflow (SDD + multi-agent)

### Step A: Decide if an ADR is required

Output: 3-5 bullets answering:
- What decision is being made?
- Why now (what triggered it)?
- What scope is affected?

If this is an architectural decision with cross-cutting impact, write an ADR.

### Step B: Pull inputs from the spec

Output: a short list of constraints and decision drivers with **links** to the spec/track/task artifacts.
- Constraints: must/must-not/should, deadlines, platform limits, compliance.
- Drivers: ranked priorities (cost, latency, operability, DX, security, time-to-deliver).

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

## Quality gates

Before finalizing, check `references/quality-gates.md`.

## SDD integration notes

When the ADR is accepted, update the relevant spec/track/task artifact to link to it (and ensure the ADR links back). See `references/sdd-integration.md`.

## Optional scripts

- `scripts/new_adr.sh` scaffolds a new MADR file and updates the ADR index block.
- `scripts/update_index.sh` rebuilds the ADR index block deterministically from ADR files.
- `scripts/validate_adr.sh` validates that a single MADR file contains required sections.
- `scripts/validate_repo.sh` validates all ADRs in a repo and checks index coverage.
