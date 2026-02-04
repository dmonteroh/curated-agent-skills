# Few-Shot Example Selection

## Goal

Select examples that teach the model the exact format, edge cases, and decision logic needed for the task.

## Selection strategies

### Semantic similarity

Use embeddings or similarity scoring to pick examples closest to the input.

```
examples = [
  {"input": "...", "output": "..."},
  {"input": "...", "output": "..."}
]

scores = [similarity(embed(example.input), embed(query)) for example in examples]
top_k = select_top_k(examples, scores, k=3)
```

### Diversity sampling

Select examples that span distinct patterns and edge cases.

```
clusters = cluster_examples(examples, k=3)
diverse = [closest_to_center(cluster) for cluster in clusters]
```

### Difficulty ladder

Order examples from simple to complex to scaffold learning.

```
examples_sorted = sort_by_difficulty(examples)
selected = take_spread(examples_sorted, k=3)
```

### Error-guided selection

Include examples that explicitly counter known failure modes.

```
selected = pick_examples_matching(error_patterns, examples)
```

## Decision points

- If outputs are inconsistent, add a high-signal edge case.
- If the model overfits to one pattern, add a diverse example.
- If the task is format-sensitive, prioritize format-perfect examples.
