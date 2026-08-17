---
name: cdd-context
description: "Create and maintain CDD project context docs (product, tech stack, workflow, optional product guidelines) when setting up or updating docs/context, with optional scaffolding, brownfield extraction from an existing codebase, indexing, validation, and a brief snapshot."
metadata:
  category: ai
---
# CDD Context

Provides guidance for managing project context as first-class artifacts alongside code. This skill is standalone and does not depend on other skills.

## Use this skill when

- Starting work in a repo and stable context (what/why/how) is needed before making changes.
- A team wants consistent, discoverable context artifacts for humans and agents.
- Context needs updates after meaningful changes (product direction, stack, workflow).
- Onboarding onto an existing codebase whose stack and workflow are undocumented.
- User-facing wording needs a canonical home — voice, terminology, or error-message format that humans and agents should follow consistently.

## Do not use this skill when

- The request is a one-line change and context is already clear.
- The user explicitly forbids documentation or file edits.
- The repository already has documentation and instruction surfaces that work, and the request is to *govern* them — give each existing file a maintenance role, put every fact under exactly one owner, and keep the set from drifting as the project ages. Scaffolding this prescribed context set on top of a working structure produces a second, competing documentation system; that request is answered by assigning roles to what is already there, not by creating docs/context beside it.

## Inputs required

- Repo root (current working directory)
- Existing context conventions (directory or filenames), if any
- Whether automation scripts are allowed
- Whether to create/update the brief snapshot
- Any reporting format preferences

## Constraints

- Honor repository context conventions over defaults.
- Avoid network calls or time-sensitive assumptions.
- Do not add dependencies or require other skills.

## Defaults (override if the repo already has conventions)

- Context directory: docs/context/
- Context index: docs/context/README.md
- Required core artifacts (minimal):
  - docs/context/product.md
  - docs/context/tech-stack.md
  - docs/context/workflow.md
- Optional (recommended) rehydration snapshot:
  - docs/context/brief.md
- Optional, add only when the repo produces user-facing text:
  - docs/context/product-guidelines.md — brand voice and tone, a terminology glossary with preferred and avoided terms, the error-message format, and user-facing copy standards. The three core files own what is built, with what, and how the team works; none of them owns how the product *sounds*, so without this file an agent writing an error string or UI label has no canonical place to check. Keep it optional: a fourth required file that nobody maintains is another stale artifact, not more context.

## Workflow (single canonical process)

1) Discover existing context
- Locate any existing context directory and files (prefer repo conventions).
- Output: chosen context directory and list of existing context files.
- Decision: If an existing system is present, do not scaffold unless requested.

2) Scaffold missing core files (optional)
- If allowed, scaffold minimal stubs for missing core files.
- Output: list of created files (or note that no files were created).
- Decision: If file writes are not allowed, only report missing artifacts.
- Decision: Scaffold `product-guidelines.md` only when the user asks for it or the repo emits user-facing text (UI copy, CLI output, error strings, API messages); it is optional, not a fourth core file.

3) Pre-populate from the existing codebase (brownfield)
- For an existing codebase, do not hand back empty stubs: read the repository's own signals and fill the drafts with what is demonstrably there.
- Extract from dependency manifests and lockfiles (languages, frameworks, pinned versions), CI and build configuration (test, lint and type-check commands; quality gates; deploy targets), container and infrastructure files and env templates (data stores, runtime targets), and existing prose (README, CONTRIBUTING, ADRs) for conventions the team already wrote down.
- Extraction fills `tech-stack.md` and `workflow.md` only. Product intent — goals, users, non-goals, success metrics — is not in the code: a manifest shows what is installed, never why. Leave those for the user to supply, or record them under “Open questions”.
- Every extracted entry is a draft to be corrected, not a verified record. Mark each one unconfirmed until the user reviews it, and cite the file it came from so the reviewer can check it in one step rather than re-deriving it.
- Output: pre-populated drafts with each entry marked unconfirmed and sourced, plus a review request naming what could not be extracted.
- Decision: If the repo is new (no code yet), skip this step and leave the stubs from step 2 as-is.

4) Validate structure
- Confirm required files and headings exist.
- Output: validation results or missing headings/files.
- Decision: If fixes are needed and file writes are allowed, add minimal headings; otherwise report gaps.

5) Update context content
- Edit only relevant sections; avoid rewriting unrelated history.
- Add an “Open questions” section when information is uncertain.
- Output: updated file paths and a short change summary.

6) Maintain the index
- Update the managed index block in the context README.
- Output: confirmation that the index block is up to date.
- Decision: If index markers are missing and file writes are allowed, add them; otherwise report and skip updates.

7) Create/update brief snapshot (optional)
- If requested, generate/update `brief.md` as a rehydration snapshot.
- Output: confirmation that `brief.md` was created or updated.
- Decision: If not requested or file writes are disallowed, report that the snapshot was skipped.

## Scripts (optional automation)

Use these only if the user allows file writes and scripts:

```sh
./cdd-context/scripts/context.sh init
./cdd-context/scripts/context.sh index
./cdd-context/scripts/context.sh brief
./cdd-context/scripts/context.sh validate
```

`init` scaffolds the three core files and the index block only. The optional `product-guidelines.md` is created by hand from `references/templates.md`; `index` then picks it up automatically, because it indexes every `*.md` in the context directory, and `validate` still passes, because it requires only the core files.

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
- Summary: Scaffolded core context artifacts and index.
- Files created/updated: `docs/context/product.md`, `docs/context/tech-stack.md`, `docs/context/workflow.md`, `docs/context/README.md`
- Validation results: passed
- Open questions: none

**Example 2: update tech stack context**

Input:
"We migrated to PostgreSQL; update the tech stack context and refresh the index."

Output (report summary):
- Summary: Updated tech stack context and refreshed index.
- Files created/updated: `docs/context/tech-stack.md`, `docs/context/README.md`
- Validation results: passed
- Open questions: none

**Example 3: onboard an existing codebase (brownfield)**

Input:
"This repo has no context docs. Set them up."

Output (report summary):
- Summary: Scaffolded core artifacts, then pre-populated the stack and workflow drafts from repository signals.
- Files created/updated: `docs/context/product.md` (stub), `docs/context/tech-stack.md` (draft), `docs/context/workflow.md` (draft), `docs/context/README.md`
- Extracted, unconfirmed — please correct: Python 3.12 + FastAPI (`pyproject.toml`); PostgreSQL (`compose.yaml`); tests via `pytest -q` and lint via `ruff check` (`.github/workflows/ci.yml`); PRs require one approval (`CONTRIBUTING.md`).
- Not extractable, needs you: product one-liner, users, non-goals, success metrics — recorded under “Open questions” in `product.md`.
- Validation results: passed

## Output contract

When running this skill, report in the following format:
- Summary (1–3 bullets)
- Files created/updated
- Extracted-and-unconfirmed entries, each with the file it came from, when brownfield extraction ran
- Validation results (or note if not run)
- Open questions

## References

- `references/README.md` (index)
