# Few-Shot Example Construction

## Format consistency

Keep identical fields and ordering across all examples.

```
Input: {input}
Output: {output}
```

## Input-output alignment

Examples must demonstrate the exact task required, not a paraphrased variant.

```
Good:
Input: "Sentiment: The movie was boring."
Output: "Negative"

Avoid:
Input: "The movie was boring."
Output: "This expresses negative sentiment."
```

## Complexity balance

Include one simple, one typical, and one edge case when possible.

## Ordering

- Start with the simplest example.
- Place the most similar example closest to the user input.

## Anti-patterns

- Inconsistent labels or formatting between examples.
- Examples that conflict with constraints or policies.
- Too many examples that crowd out the user input.
