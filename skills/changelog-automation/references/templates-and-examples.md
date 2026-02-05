# Templates and Examples

## Changelog Entry Template (Keep a Changelog)

```markdown
## [Unreleased]

### Added
- ...

### Changed
- ...

### Fixed
- ...
```

Usage

- Use only sections that have entries.
- Keep entries user-facing and free of internal identifiers.

Verification

- Confirm every entry maps back to a commit or PR.

## Release Notes Template

```markdown
# Release {{version}}

## Highlights
- ...

## Added
- ...

## Changed
- ...

## Fixed
- ...

## Breaking Changes
- ...
```

Usage

- Put breaking changes in a dedicated section.
- Keep highlights limited to 3–5 items.

Verification

- Check that breaking changes match version bump rules.

## Commit Message Examples

```
feat(auth): add password reset flow
fix(api): handle empty payloads
perf(ui): reduce render time for dashboards
```

Usage

- Use scopes consistently to improve grouping.
- Use `!` or `BREAKING CHANGE:` in the footer for major bumps.

Verification

- Run the commit linter against sample commits.

## Checklist for Clean Release Notes

- Remove internal ticket IDs unless they are public.
- Replace sensitive data with neutral descriptions.
- Confirm the release version matches changelog headers.
