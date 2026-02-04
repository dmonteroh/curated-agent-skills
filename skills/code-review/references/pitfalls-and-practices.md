# Pitfalls and Practices

## Recommended practices

- Keep reviews scoped to the diff and its impact.
- Prefer automation for formatting and linting checks.
- Verify behavior changes with tests or monitoring hooks.
- Keep PRs small when possible; request splitting when risk is high.
- Summarize key risks and required follow-ups.

## Common pitfalls

- Blocking on subjective style preferences.
- Missing input validation at trust boundaries.
- Ignoring rollback and migration safety.
- Skipping observability updates for new behavior.
- Approving without checking error paths.
