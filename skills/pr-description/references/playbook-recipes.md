# Manual Verification Playbook Recipes

One recipe per change-type classification. Every playbook opens with the common preamble, then follows the matching recipe step by step. Every step must obey the step-level rules in `SKILL.md`.

## Common preamble (every playbook)

- Environment and prerequisites — where to run, restored database, seeded data, running services, build instructions if non-default.
- Tools — named explicitly when used (for example a named API client collection such as a Bruno or Postman collection in the repo, the browser DevTools network pane, a specific psql session).
- Authentication note when role or token affects the result. Name the role and any relevant claims.
- Independence note when more than one section follows: state whether sections can run in any order or have a required order.

## Feature recipe

1. Setup — data and state required: user role, fixtures, seeded entities, identifiers to capture.
2. Happy path — numbered concrete actions. Each step has an explicit *Expected result* or *Confirm* line.
3. Error and edge paths — invalid input, permission boundaries, empty, null, or malformed state.
4. Idempotency or repeat behavior when relevant — re-run the action, restart the service, replay the request.

## Bugfix recipe

1. Reproduce the broken state on the old build, or describe the trigger condition precisely enough to recreate it.
2. Switch to the new build and re-run the same steps.
3. Confirm the outcome that reproduced as broken on the prior build matches the expected behavior on this build, with an explicit assertion.
4. Regression checks on adjacent flows that share code paths or data.

## Migration / data-shape change recipe

1. Baseline capture — count or snapshot the rows, keys, or files the migration touches, before it runs.
2. Trigger the change — start the backend with the new migration, hard-refresh the app, run the backfill script, or whatever applies.
3. Assert post-state — counts match expectations, transformed data is correct, new columns or keys are populated.
4. Spot-check preservation — non-target rows or keys are unchanged.
5. Re-run or restart idempotency — running the migration again does not duplicate or corrupt data.

## Pure refactor / docs / no observable change

- A single line: `Manual verification not applicable — <one-line reason>.`
- Optionally a follow-up line: `Confirm build, lint, and tests pass on this branch.`
- Do not invent steps to fill space.

## Mixed

- Preamble names environment, dataset, and tools used by any sub-section.
- Sub-sections labelled `A.`, `B.`, `C.`, one per concern. Each sub-section uses its own recipe above.
- State an independence note explicitly: either "Sections may be run in any order" or "Run A before B because <reason>".
