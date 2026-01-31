---
name: cdd-context
description: Create and maintain project context artifacts (CDD) as living documentation under docs/context/. Includes scripts to scaffold minimal context files, validate required sections, and maintain a deterministic context index. Works standalone; if other skills are available, use them for implementation details.
---

# CDD Context

Manage project context as first-class artifacts alongside code.

This skill is intentionally lightweight and drop-in: if a project has no existing context system, it can scaffold a minimal one; if it does, it validates and updates it without assuming any other skills exist.

## Use this skill when

- Starting work in a repo and you need stable context (what/why/how) before making changes.
- The team wants consistent, discoverable context artifacts for humans and agents.
- You need to update context after meaningful changes (product direction, stack, workflow).

## Do not use this skill when

- The request is a one-line change and context is already clear.

## Defaults (override if the repo already has conventions)

- Context directory: docs/context/
- Context index: docs/context/README.md
- Required core artifacts (minimal):
  - docs/context/product.md
  - docs/context/tech-stack.md
  - docs/context/workflow.md
- Optional (recommended) rehydration snapshot:
  - docs/context/brief.md

## Quick start

In the target repo:

```sh
./cdd-context/scripts/context.sh init
./cdd-context/scripts/context.sh index
./cdd-context/scripts/context.sh brief
./cdd-context/scripts/context.sh validate
```

## Workflow (single canonical process)

1) Verify context exists
- If docs/context/ is missing, create it.
- If core artifacts are missing, scaffold minimal stubs (don’t block).

2) Confirm context freshness
- Product context: what are we building and why?
- Tech stack: what is the stack and key constraints?
- Workflow: how do we work and what are the quality gates?

3) Update context only when needed
- Prefer small edits; avoid rewriting history without reason.
- When in doubt, add a short “Open questions” section rather than guessing.

4) Keep it discoverable
- Maintain a deterministic index in docs/context/README.md using a managed block.

## Compatibility space (optional)

If the repo also uses:
- task/track systems: link context artifacts from those docs
- ADRs: link context to ADR indexes and vice-versa

This skill does not require those systems.

## Resources

- `references/templates.md` (context file stubs + recommended headings)
- `scripts/context.sh` (wrapper)
