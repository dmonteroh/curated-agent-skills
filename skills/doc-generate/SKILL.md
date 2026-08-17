---
name: doc-generate
description: "Generate and maintain high-signal documentation from an existing codebase (API docs, architecture, runbooks, onboarding, reverse-specs). Use when a repo needs structured, maintainable docs grounded in code and configuration."
metadata:
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
- Auditing which docs a shipped or in-flight change still needs, and filling those gaps.

## Do not use this skill when

- The request is only for a one-off explanation of a single snippet.
- There is no code, spec, or source of truth to document.

## Inputs required

- Target repo path and doc output location (default: `docs/`).
- Target audiences and doc goals.
- Constraints (formats, existing doc conventions, compliance needs).
- Sources of truth beyond code (if any).

## Constraints and assumptions

- Uses local repo evidence only; no network assumptions.
- Does not install dependencies or modify package manifests.
- Writes documentation outputs only under the target repo path.

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

## Diataxis coverage pass over a diff

Applies when the trigger is a change rather than a whole repo: it turns "are the docs stale?" from a judgment call into a checkable table. Diataxis is Daniele Procida's documentation framework (`diataxis.fr`); the four quadrants below are its terms.

1) **Extract the surface.** Walk the diff against the base branch and list the new or changed public surface as a flat entity list: commands, flags, config options, API endpoints, exported modules.
2) **Score every entity against all four quadrants.** The quadrants are defined by reader intent, not by writing style:
   - reference — "what is the exact signature of Y?"
   - how-to — "how do I accomplish Y using X?"
   - tutorial — "walk me through X for the first time"
   - explanation — "why does X exist?"
3) **Classify gaps mechanically, not by feel.** Zero coverage on a required quadrant is a critical gap. Reference-only coverage is a common gap, and the most frequent real one: engineers in build mode default to writing reference, and nobody volunteers the explanation doc, so explanation rot accumulates fastest.
4) **Read the required quadrants off the entity type.** Requirements vary by type rather than applying uniformly — see the matrix below.
5) **Publish the gaps where a reviewer will see them.** Write the detected gaps into the pull request body as a distinctly labelled subsection, one line per entity, each tagged with the quadrant that would close it (for example: `FooProcessor — zero coverage. Diataxis quadrants: reference, explanation.`). A gap recorded only in the agent's own output is a gap that ships.
6) **Generate in dependency order: reference, then explanation, then how-to, tutorials last.** Reference fixes the vocabulary the other docs reuse, explanation justifies the design, how-tos build on both, and tutorials are the hardest to write well. This ordering is the originating source's stated design rationale, not a measured result.
7) **Never mix quadrants inside one file.** A tutorial gets no "Configuration" section; a reference doc gets no "What you'll build" framing. A file that seems to need both is two files.

**Entity type to required quadrants**

| Entity type | Tutorial | How-to | Reference | Explanation |
| --- | --- | --- | --- | --- |
| New feature a user interacts with | Yes | Yes | Yes | Maybe |
| CLI command or flag | Maybe | Yes | Yes | No |
| Internal module / architecture | No | No | Yes | Yes |
| Config option | No | Yes | Yes | No |
| Design pattern / philosophy | No | No | No | Yes |
| API endpoint | Maybe | Yes | Yes | No |
| Workflow (multi-step process) | Yes | Yes | No | Maybe |

"Maybe" is a third state, not a soft yes: produce that quadrant when the entity is user-facing or non-obvious, and do not count its absence as a gap.

**Worked coverage table**

| Entity | Entity type | Tutorial | How-to | Reference | Explanation |
| --- | --- | --- | --- | --- | --- |
| `--retry-budget` flag | CLI command or flag | not required | gap | existing | not required |
| `FooProcessor` | Internal module | not required | not required | gap | gap |
| Scheduled export | New feature a user interacts with | gap | existing | existing | not required |

Cells carry one of four values: `existing` (the quadrant is already covered and still accurate), `gap` (required by the entity type and absent), `not required` (the matrix does not ask for it), and `new` once this pass has written the doc that closes the gap. A `Maybe` cell in the matrix resolves to `existing` or `not required` for that entity — never to `gap`. `FooProcessor` above has no coverage at all: that is the critical case, and it is the row that must reach the PR body. A row reading `existing` under Reference and `gap` everywhere else is the common case.

Output: the coverage table, the gap list published to the PR body, and the docs generated to close the gaps.

Decision points:
- If there is no diff or base branch to scope against, use the repo-wide workflow above instead.
- If the scored quadrant disagrees with the author's judgment, the audit is a guide, not a constraint: override the tag by hand and record why in the plan.

Per-quadrant writing templates and the rules that govern each: `references/quadrant-templates.md`.

## Common pitfalls

- Drafting docs without evidence (prefer code/config/tests as truth).
- Letting the docs index drift (run index update after edits).
- Mixing observed behavior with assumptions (label assumptions explicitly).
- Overwriting existing docs without preserving structure or ownership.

## Scripts

Script paths below are relative to this skill's folder. Run each script from the target repo root, invoking it by its path inside the skill folder (for example `sh <skill-folder>/scripts/docscan.sh`); scripts write only into the target repo's docs/ tree.

**`scripts/doc.sh` (wrapper)**
- Usage: `doc.sh [scan|index|spec]` — dispatches to the scripts below.
- Requires: POSIX shell, standard core utilities.
- Verification: command prints an "OK" line and writes expected files.

**`scripts/docscan.sh`**
- Requires: POSIX shell, `find`, `wc`, `date`; optional `rg` for speed.
- Output: docs/_docgen/inventory.md plus an "OK" line.
- Verification: open the inventory file and confirm counts match repo signals.

**`scripts/update_docs_index.sh`**
- Requires: POSIX shell, `find`, `sort`, `awk`, `mktemp`.
- Output: updates index block inside docs/README.md.
- Verification: confirm the managed block lists all docs except `docs/_docgen/`.

**`scripts/spec_mine.sh`**
- Requires: POSIX shell.
- Output: docs/specs/reverse-spec.md (created only if missing).
- Verification: confirm the reverse-spec template exists and is populated with placeholders.

## References

- `references/README.md` for detailed templates and playbooks.
- `references/quadrant-templates.md` for the reference, explanation, how-to, and tutorial document templates used by the coverage pass, plus the cross-quadrant link sweep run before landing a generated set.

## Output contract

Report results using this format:

```
Summary:
- Goal and scope:
- Docs created/updated:
- Evidence sources used:
- Open questions/gaps:
- Scripts run (with outputs):
- Verification:
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
