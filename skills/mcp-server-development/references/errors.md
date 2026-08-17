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
  - `stop_condition` (when to stop retrying and escalate)
  - `details` (optional; include only when requested)
- A `hint` alone invites an unbounded retry loop: nothing in the response says when trying again has stopped being useful, so "try again with a different token" reads as valid on the hundredth attempt as on the first. Every error that invites a retry states its stop condition too, in one of three forms:
  - a code that is never transient, so retrying it cannot succeed — `INVALID_STATUS`: stop immediately and surface the valid enum;
  - an attempt or elapsed-time budget the caller enforces — `RATE_LIMITED`: honor the advertised window, stop after the caller's configured number of attempts, and cap the honored wait so a bogus retry-after header cannot stall the caller indefinitely;
  - a state that should have changed between attempts and did not — `JOB_PENDING`: keep polling only while the job's state or progress marker advances, and stop on unchanged consecutive polls.
- Any attempt count or wait duration inside a stop condition is a chosen default, not a measured limit: expose it as a value the caller may set, and document it as chosen rather than derived.

## Examples of good hints

- Missing permission: “Check your auth scope; try again with a different token.”
- Invalid filter: “Valid values: active|archived. Try filter=active.”
- Too many results: “Use query=... or limit=20; results are capped.”

## Closed code sets for pluggable backends

When the server wraps an optional or swappable backend provider, give that layer its own closed, enumerated `code` set instead of open-ended exception types, and designate exactly one code as the non-fatal "degrade and continue" signal callers are expected to catch — every other code is fatal to that call. Full contract: `provider-contracts.md`.

