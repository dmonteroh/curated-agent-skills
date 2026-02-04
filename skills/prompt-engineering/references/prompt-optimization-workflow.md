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
