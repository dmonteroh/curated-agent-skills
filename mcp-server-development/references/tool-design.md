# MCP Tool Design (Workflow-First)

## Quick checklist

- Each tool exists because it completes a user-facing workflow step.
- Tool names reflect what humans ask for (not internal API resource names).
- Inputs are strict and self-documenting.
- Outputs are concise by default; “details” is opt-in.
- Tools do not require the agent to memorize hidden IDs (return IDs + human-readable labels).

## Design patterns that work well

1) “Find then act” helpers
- Provide a search tool that returns stable identifiers + key metadata.
- Provide an action tool that accepts those identifiers.

2) “Validate then commit”
- Expose a dry-run/validate mode where destructive operations are risky.
- Or split into `preview_*` and `apply_*` when the domain warrants it.

3) “List with filters”
- Avoid “list everything” defaults.
- Provide filters/sorts that match how users think (status, recency, owner).

## Anti-patterns

- One tool per upstream endpoint without consideration for agent workflows.
- Unbounded list tools (huge results, token blowups).
- Outputs that require additional calls to interpret (IDs with no labels).

