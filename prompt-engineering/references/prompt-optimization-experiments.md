# Prompt Optimization Experiments

## A/B testing pattern

Compare two prompt variants against the same test cases.

```
results_a = evaluate(prompt_a, test_suite)
results_b = evaluate(prompt_b, test_suite)
delta = compare(results_a, results_b)
```

## Metrics to track

- Accuracy or task success rate.
- Output validity (schema or formatting adherence).
- Latency and token counts.

## Decision rule

- Pick the variant with higher success and acceptable latency.
- If metrics are mixed, keep the simpler prompt and iterate.

## Sample size guidance

- Use at least 10-30 cases for quick checks.
- Add targeted edge cases for failure modes.
