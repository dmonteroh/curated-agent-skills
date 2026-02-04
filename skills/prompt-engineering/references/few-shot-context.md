# Few-Shot Context Budgeting

## Token budgeting

Allocate budget across system instructions, examples, user input, and output.

```
System: 10-20%
Examples: 30-50%
User input: 10-20%
Model output: 20-40%
```

## Dynamic truncation

Trim examples to fit the budget while preserving the most relevant cases.

```
selected = rank_by_relevance(examples, query)
while token_count(selected) > example_budget:
    selected = selected[:-1]
```

## Edge-case coverage

- Reserve one slot for a known failure case.
- If the user input is atypical, include the closest atypical example.

## Verification checks

- Final prompt fits the token budget.
- Examples leave room for the expected response length.
