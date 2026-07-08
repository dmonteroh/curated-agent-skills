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
- When outputs vary run to run, execute each case 3-5 times and compare pass rates, not single runs — one lucky pass is not a result.

## Experiment axes beyond prompt text

- On reasoning models, sweep the reasoning effort/thinking setting as its own experiment — it often moves quality, latency, and cost more than any prompt edit.
- Treat model version as a variable: record it with every result, and re-baseline when it changes.
