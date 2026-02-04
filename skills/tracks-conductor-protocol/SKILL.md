---
name: tracks-conductor-protocol
description: Run a unified protocol for intake, task briefs, tracks (spec/plan), and execution with deterministic indexing, promotion (intake -> task -> track), and validation scripts. Use when you need structured work management for SDD/CDD.
category: workflow
---

# Tracks Conductor Protocol

A single, unified work-management protocol for **intake -> planning -> execution** that fits **SDD** (spec-driven development) and **CDD** (context-driven development), and scales to **multiple agents**.

This skill is intentionally optimized for speed:
- One command to initialize work structure
- One command to create intake drafts / tasks / tracks
- Deterministic index blocks (low merge-conflict) similar to ADR indexes
- Validation to keep artifacts consistent and linkable

## Use this skill when

- You need to intake work, formalize it into task briefs, group it into tracks, plan it, and execute it.
- You want an indexing/registry system (like ADR indexes) that stays consistent across agents.
- You want to ensure specs/context are created and updated as required (SDD + CDD hygiene).

## Do not use this skill when

- The request is a single small code change with no need for tracking or planning artifacts.

## Trigger phrases

- "create a task brief"
- "start a track" / "open a track"
- "track this work"
- "promote intake"
- "set task status"
- "validate the work index"

## Default repo layout (override via env vars)

- Intake drafts: docs/project/to-do/ (TD-YYYYMMDD-*.md)
- Task briefs: docs/project/tasks/ (S##-T-YYYYMMDD-*.md)
- Task status: task frontmatter (`status:`) in each task brief (mirrored into `work_index.md`)
- Tracks registry: docs/project/tracks.md
- Tracks: docs/project/tracks/<track-slug>/{spec.md,plan.md,context.md}
- Work index (managed blocks): docs/project/work_index.md
- CDD context: docs/context/{product.md,tech-stack.md,workflow.md}

## Core principles
See `references/README.md` for core principles, traceability rules, and escalation guidance.

## Required inputs

- Target repo root (defaults to current working directory).
- Work titles (intake/task/track/future) and relevant IDs (task ID, track slug).
- Optional environment overrides for file locations.

## Workflow (unified)

### 0) Initialize (once per repo)

Run the init script to create directories, seed index blocks, and create CDD stubs:

```sh
scripts/tcd.sh init
```

- Output: directory structure + seeded index blocks + context stubs.

### 1) Intake (To-Do Draft)

Create a TD file that captures the problem, intent, and success signal:

```sh
scripts/tcd.sh intake "Title"
```

- Output: new TD file + updated `work_index.md` intake table.
- Template and quality bar: `references/templates.md`.

Decision point:
- If the intake is unclear or missing a success signal, revise the TD before promotion.

### 2) Promote intake -> task brief

When accepted, promote the TD to an executable task brief:

```sh
scripts/tcd.sh promote-intake path/to/TD-YYYYMMDD-*.md
```

- Output: new task brief + updated index tables.

Decision point:
- If the work is not actionable yet, keep it as intake and add required discovery notes.

### 3) Organize into a track (spec + plan)

Create a track to group related tasks and define a coherent spec and phased plan:

```sh
scripts/tcd.sh track "Track title"
```

- Output: track folder with `spec.md`, `plan.md`, `context.md` + updated tracks registry/index.
- Track templates: `references/templates.md`.

Decision point:
- If multiple tasks share dependencies or milestones, group them under a single track.

### 4) Execute using workflow patterns

Execution is performed per task (TDD/workflow checkpoints, verification, commit hygiene):
- Output: implementation updates plus task status transitions.
- Follow `references/execution-playbook.md` as the default execution protocol.

Decision point:
- If execution needs new context or spec updates, update the track files before coding.

### 5) Futures + ADR integration

- Output: new Future or ADR entry, plus index updates.
- If a requirement is deferred but architecture-sensitive: record it as a Future (see `references/futures.md`).
- If a decision is current and architectural: record it as an ADR using your repo's ADR format.

## Indexing + decision points
See `references/README.md` for managed index blocks, decision points, and common mistakes.

## Validation

Use:

```sh
scripts/tcd.sh validate
```

- Output: pass/fail report for required directories, index blocks, and templates.

To validate:
- required directories exist
- index blocks exist and cover all artifacts
- required sections exist in intake/tasks/tracks

## Common mistakes to avoid

- Skipping the intake template quality bar before promotion.
- Creating tracks without linking tasks in `tracks.md` and `work_index.md`.
- Letting task status drift from actual execution state.
- Editing managed index blocks by hand instead of using the scripts.

## Scripts

Entry point:

```sh
scripts/tcd.sh --help
```

Requirements:

- POSIX shell (`sh`)
- Common Unix utilities: `awk`, `sed`, `grep`, `date`

Verification:

```sh
scripts/tcd.sh validate
```

## Output contract

When this skill runs, report using this format:

- Actions: init/intake/promote/track/future/index/validate as used
- Files: created/updated paths
- Status: transitions applied or unchanged
- Follow-ups: missing inputs or next steps
- Validation: command + outcome

## Examples

Trigger test prompts:

- "Create an intake draft for implementing rate limits and add it to the index."
- "Promote this intake into a task and open a track for the billing overhaul."

Sample interaction:

User: "Start a track for migrating auth tokens and add a task brief."

Assistant output (summary format):

- Actions: `track`, `task`, `index`
- Files: `docs/project/tracks/auth-token-migration/spec.md`, `docs/project/tasks/S01-T-20240215-auth-token-migration.md`
- Status: task frontmatter updated to `Approved` and index refreshed
- Validation: `scripts/tcd.sh validate` (passed)

## References

- `references/README.md` for the full index of templates and playbooks

## Escalation rules
See `references/README.md` for escalation and cross-linking guidance.
