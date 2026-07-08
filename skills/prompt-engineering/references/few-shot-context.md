# Few-Shot Context Budgeting

## Priority order

When space is tight, keep content in this order — trim from the bottom:

1. Task instructions and constraints — never truncate.
2. One format-perfect example (the format anchor).
3. One edge case countering the most common known failure mode.
4. Additional diversity examples — first to cut.

## Budgeting rules

- Measure with the provider's tokenizer or usage metadata, not by estimating characters or fixed percentages.
- Leave headroom for the expected response length; a prompt that fits but leaves no room for output still fails.
- More examples are not better: on current instruction-following models, 1–3 high-signal examples usually saturate quality. Add a fourth only when an eval shows a measurable gain.

## Dynamic truncation

Trim examples by relevance rank while preserving the priority classes above:

```
selected = rank_by_relevance(examples, query)
while token_count(prompt(selected)) > budget:
    drop lowest-priority, least-relevant example
```

## Caching interaction

Per-request example selection makes every prompt a unique prefix and defeats prompt caching. For high-volume production prompts, prefer a fixed example set (cache-friendly) over dynamic retrieval, unless evals show retrieval-selected examples clearly win. See `prompt-caching-layout.md`.

## Verification checks

- Final prompt fits the budget with output headroom.
- Instructions and the format anchor survived truncation.
- If examples rotate per request, confirm the caching trade-off was deliberate.
