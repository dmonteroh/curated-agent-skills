---
name: doc-generate
description: Generate and maintain high-signal documentation from an existing codebase fast (API docs, architecture, runbooks, onboarding, reverse-specs). Includes repo scan + deterministic docs index scripts, and a spec-mining mode to reverse-engineer requirements from code. Works standalone; optionally link docs to ADRs and work artifacts for traceability.
category: docs
---

# doc-generate

Generate documentation from code with a bias toward **speed**, **accuracy**, and **maintainability**.

This skill replaces overlapping doc-generation skills and provides:
- A fast repo scan to build a documentation plan.
- A deterministic docs index block (to reduce multi-agent merge conflicts).
- A workflow that can link docs to **ADRs** (`adr-madr-system`) and **work artifacts** (tracks/specs/tasks), without requiring them.
- A “spec mining” mode to derive a reverse-spec (EARS-style requirements) from an existing codebase.
- A long-form “system manual” mode for deep technical documentation (optional; use when you truly need book-like depth).

## Use this skill when

- Generating API docs, architecture docs, onboarding guides, or runbooks from code.
- Standardizing documentation structure across a repo.
- Setting up doc automation (CI checks, link checks, doc freshness).
- Producing a long-form system manual (deep-dive) from an existing codebase for onboarding and long-term maintainability.

## Do not use this skill when

- The user only wants an ad-hoc explanation of a single code snippet (use `code-explain`).
- There is no code, spec, or source of truth to document.

## Quick start (fast path)

1) Run the repo scan (optional but recommended):
- `scripts/docscan.sh`

2) (Optional) Mine a reverse-spec from the codebase:
- `scripts/spec_mine.sh`

3) Produce a doc plan:
- audiences, doc set, file locations, ownership, and update triggers.

4) Generate docs incrementally:
- start with 1-2 top-value docs (often: docs/README.md, docs/architecture/overview.md, docs/runbooks/).

5) Add automation:
- index generation, link checks, and a lightweight “docs stale?” checklist.

## Workflow (best results, best speed)

### 1) Define the doc set (don’t boil the ocean)

Output: a short plan containing:
- Target audiences (developers, operators, end-users).
- Minimum doc set (recommended):
  - docs/README.md (docs entry point + index block)
  - docs/architecture/overview.md
  - docs/runbooks/ (ops workflows)
  - docs/onboarding/ (setup, local dev)
- “Living docs” sources: specs, ADRs, track/task artifacts, code.

### 2) Extract truth from the repo

- Prefer code/config as truth (not assumptions).
- If required info is missing, add a small “Missing Information” section and create follow-up work items.

### 3) Write docs as linkable artifacts

- Keep docs short and navigable; link out to deeper references.
- Add explicit links:
  - To ADRs (decisions) via `adr-madr-system`
  - To work specs/tracks/tasks (why + scope)

### 4) Indexing (multi-agent safe)

Use a managed block in docs/README.md:

<!-- DOC-INDEX:START -->
<!-- DOC-INDEX:END -->

Then run:
- `scripts/update_docs_index.sh`

### 4b) Spec mining (reverse-engineer requirements from code)

Use when the repo exists but the spec is missing/stale and you need a high-signal baseline quickly.

Output: a single reverse-spec doc (EARS-style) that captures:
- Primary actors + key user flows.
- Functional requirements (EARS “WHEN/IF… THEN…” format).
- Non-functional requirements (reliability, performance, security, privacy, ops).
- Constraints and invariants discovered in code/config/tests.
- Open questions and follow-up work items.

Run:
- `scripts/spec_mine.sh`

Then:
- Treat the reverse-spec as “derived truth” (grounded in code) and refine with stakeholders.
- If you later create a formal spec/track, link it to the reverse-spec (optional, not required).

### 5) Automation / CI hooks (recommended)

- Ensure docs index stays updated.
- Run link checks if your repo supports it.
- Enforce “no secrets in docs” scanning.

## Resources

- `resources/implementation-playbook.md` for patterns, templates, and automation ideas.
- `scripts/docscan.sh` to quickly inventory repo/doc needs.
- `scripts/update_docs_index.sh` to maintain a deterministic docs index block.
- `resources/spec-mining.md` for the spec-mining approach and EARS template.
- `scripts/spec_mine.sh` to scaffold a reverse-spec doc quickly and safely.
- `resources/system-manual-template.md` for the long-form deep-dive/manual structure (use sparingly; prefer smaller docs by default).
