---
name: doc-generate
description: Generate and maintain high-signal documentation from an existing codebase (API docs, architecture, runbooks, onboarding, reverse-specs). Use when a repo needs structured, maintainable docs grounded in code and configuration.
category: docs
---

# doc-generate

Provides a repeatable workflow to generate and maintain documentation that is grounded in code, configuration, and tests.

Core capabilities:
- Repo inventory for fast discovery.
- Deterministic docs index generation.
- Documentation planning and incremental delivery.
- Optional reverse-spec mining (EARS-style requirements) when formal specs are missing.
- Optional long-form system manual template for deep technical docs.

## Use this skill when

- Generating API docs, architecture docs, onboarding guides, or runbooks from code.
- Standardizing documentation structure across a repo.
- Setting up doc automation (indexing, link checks, doc freshness).
- Producing a long-form system manual from an existing codebase when needed.

## Do not use this skill when

- The request is only for a one-off explanation of a single snippet.
- There is no code, spec, or source of truth to document.

## Trigger phrases

- "Generate docs from this repo"
- "Create architecture or onboarding docs"
- "Reverse-engineer a spec from the code"
- "Set up a docs index and doc automation"

## Inputs required

- Target repo path and doc output location (default: `docs/`).
- Target audiences and doc goals.
- Constraints (formats, existing doc conventions, compliance needs).
- Sources of truth beyond code (if any).

## Quick start (fast path)

1) Run the repo scan (optional but recommended).
   Output: docs/_docgen/inventory.md.
2) Draft a doc plan (audiences, doc set, file locations, ownership, update triggers).
   Output: short plan + proposed file list.
3) Generate the first 1–2 docs (typically docs/README.md and architecture overview).
   Output: initial docs with links to evidence.
4) Add or update the managed docs index block and rebuild it.
   Output: deterministic index table in docs/README.md.
5) (Optional) Run reverse-spec mining when requirements are missing.
   Output: docs/specs/reverse-spec.md.

## Workflow (best results, best speed)

### 1) Scope the doc set

Output: a concise plan covering:
- Target audiences.
- Minimum doc set (recommended):
  - docs/README.md (entry point + index block)
  - docs/architecture/overview.md
  - `docs/runbooks/`
  - `docs/onboarding/`
- Sources of truth (code, config, tests, existing docs).

Decision points:
- If only one doc is required, skip index automation.
- If an existing docs structure exists, reuse its folders.

### 2) Inventory the repo

Output: repo signals list and a short summary.

Decision points:
- If `rg` is unavailable, rely on `find` (script handles this).
- If no `docs/` directory exists, propose creating one.

### 3) Draft the doc plan and skeletons

Output: doc list + short outline per doc.

Decision points:
- If any doc exceeds a screenful, split into subpages.
- If information is missing, add a "Missing information" section and log follow-ups.

### 4) Write docs grounded in evidence

Output: draft docs with evidence links to code/config/tests.

Decision points:
- If behavior is inferred, label it as an assumption.
- If evidence is unclear, add an open question instead of guessing.

### 5) Maintain the docs index

Output: deterministic index block in docs/README.md.

Decision points:
- If the index block is missing, add it once and rerun the index script.

### 6) Reverse-spec mining (optional)

Output: docs/specs/reverse-spec.md with EARS-style requirements.

Decision points:
- If requirements already exist and are current, skip spec mining.

### 7) Automation hooks (optional)

Output: checklist for doc freshness, link checks, and index updates.

Decision points:
- If CI tooling is unavailable, provide manual run steps instead.

## Common pitfalls

- Drafting docs without evidence (prefer code/config/tests as truth).
- Letting the docs index drift (run index update after edits).
- Mixing observed behavior with assumptions (label assumptions explicitly).
- Overwriting existing docs without preserving structure or ownership.

## Scripts

**`scripts/doc.sh` (wrapper)**
- Usage: `./scripts/doc.sh [scan|index|spec]`
- Requires: POSIX shell, standard core utilities.
- Verification: command prints an "OK" line and writes expected files.

**`scripts/docscan.sh`**
- Usage: `./scripts/docscan.sh`
- Requires: POSIX shell, `find`, `wc`, `date`; optional `rg` for speed.
- Output: docs/_docgen/inventory.md plus an "OK" line.
- Verification: open the inventory file and confirm counts match repo signals.

**`scripts/update_docs_index.sh`**
- Usage: `./scripts/update_docs_index.sh`
- Requires: POSIX shell, `find`, `sort`, `awk`, `mktemp`.
- Output: updates index block inside docs/README.md.
- Verification: confirm the managed block lists all docs except `docs/_docgen/`.

**`scripts/spec_mine.sh`**
- Usage: `./scripts/spec_mine.sh`
- Requires: POSIX shell.
- Output: docs/specs/reverse-spec.md (created only if missing).
- Verification: confirm the reverse-spec template exists and is populated with placeholders.

## References

- `references/README.md` for detailed templates and playbooks.

## Output contract

Report results using this format:

```
Summary:
- Goal and scope:
- Docs created/updated:
- Evidence sources used:
- Open questions/gaps:
- Scripts run (with outputs):
- Follow-up recommendations:
```

## Examples

**Input**: "Generate architecture and onboarding docs for this repo."

**Output (summary)**:
```
Summary:
- Goal and scope: Architecture + onboarding docs in docs/.
- Docs created/updated: docs/README.md, docs/architecture/overview.md, docs/onboarding/setup.md.
- Evidence sources used: src/, config/, README.md.
- Open questions/gaps: Missing deployment workflow.
- Scripts run (with outputs): docscan.sh (docs/_docgen/inventory.md).
- Follow-up recommendations: Add runbook for incident response.
```

## Trigger test

- "Create a reverse-spec from this codebase."
- "Set up a docs index and generate a docs/README.md entrypoint."
