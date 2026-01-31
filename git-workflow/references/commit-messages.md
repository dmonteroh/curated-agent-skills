# Commit Messages (Clean PRs)

Goal: commits should be reviewable, searchable, and easy to revert.

## Default style

- Subject line: imperative, <= 72 chars
- Body: why + constraints + caveats (optional but recommended for non-trivial changes)
- Reference issues/ADRs/specs if they exist (optional)

Example:

```text
fix(auth): reject expired refresh tokens

The verifier started accepting expired refresh tokens when the TTL parser
was refactored. This adds a strict expiry check and a regression test.
```

## Squash vs keep commits

Keep multiple commits when they each add value:
- isolated refactor
- behavior change + tests
- docs/update scripts

Squash when commits are noise:
- "wip"
- "fix typo"
- "address review comments" (fold into the relevant commit)

## What to avoid

- “update” / “fix” with no context
- mixing unrelated changes in one commit
- committing generated files unless your repo intentionally tracks them

