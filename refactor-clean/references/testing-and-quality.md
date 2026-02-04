# Testing, Verification, and Quality

Use this reference to build safety nets and report quality outcomes.

## Safety Net Options

- Run existing unit and integration tests when available.
- Add characterization tests for critical paths when tests are missing.
- Use golden master snapshots for legacy behavior if appropriate.

## Verification Tiers

- **Tier 1:** focused unit tests for refactored functions.
- **Tier 2:** integration or end-to-end tests for affected flows.
- **Tier 3:** targeted manual checks for high-risk paths.

## Migration Guidance

- If breaking changes are required, provide a step-by-step migration note.
- Offer temporary adapters or deprecations when feasible.

## Quality Checklist

- Complexity reduced in the targeted area.
- Duplicate logic consolidated or eliminated.
- Names and structure match domain intent.
- Error handling remains intact.
- Tests cover the refactored seams.
