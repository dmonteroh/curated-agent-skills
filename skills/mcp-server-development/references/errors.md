# Error Handling (Agent-Friendly)

## Goals

- Keep errors short by default.
- Provide next steps the agent can take.
- Preserve enough detail to debug without dumping entire payloads.

## Patterns

- Normalize upstream errors into a consistent error shape:
  - `code` (stable)
  - `message` (human/agent readable)
  - `hint` (what to do next)
  - `details` (optional; include only when requested)

## Examples of good hints

- Missing permission: “Check your auth scope; try again with a different token.”
- Invalid filter: “Valid values: active|archived. Try filter=active.”
- Too many results: “Use query=... or limit=20; results are capped.”

## Closed code sets for pluggable backends

When the server wraps an optional or swappable backend provider, give that layer its own closed, enumerated `code` set instead of open-ended exception types, and designate exactly one code as the non-fatal "degrade and continue" signal callers are expected to catch — every other code is fatal to that call. Full contract: `provider-contracts.md`.

