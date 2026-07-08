# Prompt Optimization Workflow

## Baseline setup

Define a test suite and capture baseline metrics before changing the prompt.

```
baseline = evaluate(prompt, test_suite)
record(baseline)
```

## Iterative refinement loop

```
repeat:
  run tests
  analyze failures
  change one instruction
  re-test
until target metrics are met
```

## Grading methods

- **Structured outputs**: grade mechanically — schema validation, exact match, or unit-test-style assertions. Never eyeball what a validator can check.
- **Free-form outputs**: score against a short written rubric (3–5 criteria). At volume, use an LLM judge given that rubric — but spot-check its verdicts against human grades before trusting it, and re-check when the judge model changes.
- **Hold-out set**: keep a small set of cases that never steers edits; run it before shipping. Passing only the visible test set is how prompts overfit.

## Failure analysis checklist

- Which inputs fail most often?
- Is the output format wrong or incomplete?
- Are constraints being ignored?
- Are errors clustered around a single instruction?

## Changelog format

```
- Change: {what changed}
- Reason: {why}
- Expected impact: {effect}
```
