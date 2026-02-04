---
name: cdd-context
description: Create and maintain CDD project context docs (product, tech stack, workflow) with optional scaffolding, indexing, validation, and a brief snapshot under docs/context.
category: ai
---

# CDD Context

Manage project context as first-class artifacts alongside code. This skill is standalone and does not depend on other skills.

## Use this skill when

- Starting work in a repo and you need stable context (what/why/how) before making changes.
- The team wants consistent, discoverable context artifacts for humans and agents.
- You need to update context after meaningful changes (product direction, stack, workflow).

## Do not use this skill when

- The request is a one-line change and context is already clear.
- The user explicitly forbids documentation or file edits.

## Activation cues (trigger phrases)

- "set up context docs" / "docs/context is missing"
- "update product context" / "update tech stack context" / "update workflow context"
- "create a context brief" / "rehydration snapshot"

## Inputs required

- Repo root (current working directory)
- Existing context conventions (directory or filenames), if any
- Whether automation scripts are allowed
- Whether to create/update the brief snapshot
- Any reporting format preferences

## Defaults (override if the repo already has conventions)

- Context directory: docs/context/
- Context index: docs/context/README.md
- Required core artifacts (minimal):
  - docs/context/product.md
  - docs/context/tech-stack.md
  - docs/context/workflow.md
- Optional (recommended) rehydration snapshot:
  - docs/context/brief.md

## Workflow (single canonical process)

1) Discover existing context
- Locate any existing context directory and files (prefer repo conventions).
- Output: chosen context directory and list of existing context files.
- Decision: If an existing system is present, do not scaffold unless requested.

2) Scaffold missing core files (optional)
- If allowed, scaffold minimal stubs for missing core files.
- Output: list of created files (or note that no files were created).
- Decision: If file writes are not allowed, only report missing artifacts.

3) Validate structure
- Confirm required files and headings exist.
- Output: validation results or missing headings/files.

4) Update context content
- Edit only relevant sections; avoid rewriting unrelated history.
- Add an “Open questions” section when information is uncertain.
- Output: updated file paths and a short change summary.

5) Maintain the index
- Update the managed index block in the context README.
- Output: confirmation that the index block is up to date.

6) Create/update brief snapshot (optional)
- If requested, generate/update `brief.md` as a rehydration snapshot.
- Output: confirmation that `brief.md` was created or updated.

## Scripts (optional automation)

Use these only if the user allows file writes and scripts:

```sh
./cdd-context/scripts/context.sh init
./cdd-context/scripts/context.sh index
./cdd-context/scripts/context.sh brief
./cdd-context/scripts/context.sh validate
```

Environment overrides:
- `CONTEXT_DIR` (default `docs/context`)
- `CONTEXT_INDEX` (default `docs/context/README.md`)
- `CONTEXT_BRIEF_FILE` (default `docs/context/brief.md`)

Verification step:
- Run `./cdd-context/scripts/context.sh validate` after scaffolding or edits.

Required tools:
- POSIX shell with standard Unix utilities (`mkdir`, `cat`, `grep`, `awk`, `sort`, `mktemp`, `date`).

## Common pitfalls

- Overwriting existing context instead of honoring repo conventions.
- Missing the index markers in `docs/context/README.md`.
- Treating `brief.md` as the source of truth (it is a snapshot).
- Leaving stale “Open questions” unanswered after decisions are made.

## Examples

**Example 1: scaffold context**

Input:
"Set up context docs in this repo and index them."

Output (report summary):
- Created `docs/context/product.md`, `docs/context/tech-stack.md`, `docs/context/workflow.md`
- Updated `docs/context/README.md` index block
- Validation: passed

**Example 2: update tech stack context**

Input:
"We migrated to PostgreSQL; update the tech stack context and refresh the index."

Output (report summary):
- Updated `docs/context/tech-stack.md` with new datastore details
- Updated `docs/context/README.md` index block
- Validation: passed

## Output contract

When you run this skill, report in the following format:
- Summary (1–3 bullets)
- Files created/updated
- Validation results (or note if not run)
- Open questions

## Trigger test

The following prompts should activate this skill:
- "Create docs/context with product, tech stack, and workflow context."
- "Update the workflow context and refresh the context index."

## References

- `references/README.md` (index)
