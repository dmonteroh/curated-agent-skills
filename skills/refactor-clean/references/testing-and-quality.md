# Testing, Verification, and Quality

Use this reference to build safety nets and report quality outcomes.

## Safety Net Options

- Run existing unit and integration tests when available.
- Add characterization tests for critical paths when tests are missing.
- Use golden master snapshots for legacy behavior if appropriate.

## Reading Coverage Into a Tier

- Where the project has a coverage tool, take the number from it and record which tool produced it.
- Where it does not, the tier that gates the refactor is an estimate read off the test files. Record it as an estimate and say so in the report. An estimated percentage reported as a measurement turns a judgment call into a false fact, and the gate is only as good as its input.
- Read coverage per zone, not per target. Core, consumers, and edge usually differ, and the edge is normally where the gap is.

## Proving a Guard Is Safe to Remove

- An adversarial test feeds the malformed or hostile input the guard exists for.
- It counts only once it has been shown to fail without the guard: remove the guard, watch the test go red, restore the guard, watch it go green. A test that passes both ways proves nothing about the guard.
- Land it in the same change as the removal, never in a follow-up.

## What Not to Pin

- Do not add text assertions over prose files. A prompt, a rule file, a skill, or any other markdown has no behavioral seam, so a word-count or phrase assertion over it guards a diff rather than a behavior, and it fails on every legitimate edit.
- Cover only a machine-consumed value: a parsed field, a sentinel some runtime greps for, or a documented sample run through its real validator. Leave the rest of the prose to review.

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
