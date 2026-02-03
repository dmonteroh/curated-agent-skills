# Context Management Notes

Use this when managing long-lived project context and avoiding context drift.

## Principles

- Keep context artifacts minimal and current.
- Prefer short, explicit updates over large rewrites.
- Track key assumptions and open questions.

## Context Lifecycle

1. **Collect**: Gather product goals, stack constraints, and workflow rules.
2. **Prune**: Remove stale or superseded details.
3. **Version**: Note major context changes (date and reason).
4. **Validate**: Ensure core files are present and linked in the index.

## Retrieval Guidance

- Pull only the context needed for the current task.
- Summarize long sections into task-relevant bullets.
- Keep a short "brief" snapshot for fast rehydration.

## When Context Becomes Large

- Split into focused sections (product, tech-stack, workflow, architecture).
- Link to ADRs or specs rather than duplicating.
- Prefer references to canonical docs over copies.
