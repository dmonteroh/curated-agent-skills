---
name: tracks-conductor-protocol
description: Unified protocol + tooling for spec-driven and context-driven development across intake, task briefs, tracks (spec/plan), and execution. Designed for multi-agent workflows with deterministic indexing, promotion (intake -> task -> track), and validation scripts. Works standalone; if tech/framework skills are available, use them for implementation details.
category: workflow
---

# Tracks Conductor Protocol

A single, unified work-management protocol for **intake -> planning -> execution** that fits **SDD** (spec-driven development) and **CDD** (context-driven development), and scales to **multiple agents**.

This skill is intentionally optimized for speed:
- One command to initialize work structure
- One command to create intake drafts / tasks / tracks
- Deterministic index blocks (low merge-conflict) similar to `adr-madr-system`
- Validation to keep artifacts consistent and linkable

## Use this skill when

- You need to intake work, formalize it into task briefs, group it into tracks, plan it, and execute it.
- You want an indexing/registry system (like ADR indexes) that stays consistent across agents.
- You want to ensure specs/context are created and updated as required (SDD + CDD hygiene).

## Do not use this skill when

- The request is a single small code change with no need for tracking or planning artifacts.

## Default repo layout (override via env vars)

- Intake drafts: docs/project/to-do/ (TD-YYYYMMDD-*.md)
- Task briefs: docs/project/tasks/ (S##-T-YYYYMMDD-*.md)
- Task status: docs/project/task_status.md
- Tracks registry: docs/project/tracks.md
- Tracks: docs/project/tracks/<track-slug>/{spec.md,plan.md,context.md}
- Work index (managed blocks): docs/project/work_index.md
- CDD context: docs/context/{product.md,tech-stack.md,workflow.md}

## Core principles (multi-agent compatible)

- **Separate artifacts per work unit**: reduce merge conflicts (no monolithic ledgers).
- **Managed index blocks**: scripts rebuild tables deterministically.
- **Promotion, not mutation**:
  - Intake drafts are problem-focused.
  - Task briefs are executable and acceptance-driven.
  - Tracks organize multiple tasks under a single spec/plan.
- **Traceability is non-negotiable**:
  - Intake <-> Task <-> Track <-> (optional) ADRs and Futures all link to each other.
- **Context precedes code**:
  - If context is missing, create/update CDD artifacts.
  - If decisions are material, create/update ADRs using `adr-madr-system`.

## Workflow (unified)

### 0) Initialize (once per repo)

Run the init script to create directories, seed index blocks, and create CDD stubs:

```sh
scripts/tcd.sh init
```

### 1) Intake (To-Do Draft)

Create a TD file that captures the problem, intent, and success signal:

```sh
scripts/tcd.sh intake "Title"
```

- Template and quality bar: `references/templates.md`

### 2) Promote intake -> task brief

When accepted, promote the TD to an executable task brief:

```sh
scripts/tcd.sh promote-intake path/to/TD-YYYYMMDD-*.md
```

- Update status sources of truth (`task_status.md`, index).

### 3) Organize into a track (spec + plan)

Create a track to group related tasks and define a coherent spec and phased plan:

```sh
scripts/tcd.sh track "Track title"
```

- Track templates: `references/templates.md`

### 4) Execute using workflow patterns

Execution is performed per task (TDD/workflow checkpoints, verification, commit hygiene):
- Follow `references/execution-playbook.md` as the default execution protocol.

### 5) Futures + ADR integration

- If a requirement is deferred but architecture-sensitive: record it as a Future (see `references/futures.md`).
- If a decision is current and architectural: record it as an ADR via `adr-madr-system`.

## Indexing system (like adr-madr-system)

docs/project/work_index.md contains managed blocks:
- Intake table
- Tasks table
- Tracks table
- Futures table (file-per-entry by default; compatible with a ledger if present)

Scripts rebuild only these blocks, keeping other content untouched.

## Validation

Use:

```sh
scripts/tcd.sh validate
```

To validate:
- required directories exist
- index blocks exist and cover all artifacts
- required sections exist in intake/tasks/tracks

## References

- `references/templates.md` for templates (intake/task/track/context)
- `references/index-format.md` for managed-block formats and columns
- `references/status-model.md` for lifecycle states and promotion rules
- `references/cdd-sdd-interop.md` for when to create/update context/spec
- `references/futures.md` for unified Futures handling (file-per-entry + ledger compatibility)
- `references/execution-playbook.md` for execution, verification, and commit hygiene

## Escalation rules (create more spec/context as required)

- If an intake draft cannot be evaluated without project context, create/update docs/context/* first.
- If a track spec is missing requirements or non-goals, expand it before implementation.
- If implementation depends on a cross-cutting architectural decision, create an ADR via `adr-madr-system`.
- If a requirement is explicitly deferred but architecture-sensitive, create a Future entry and add a clear trigger.
