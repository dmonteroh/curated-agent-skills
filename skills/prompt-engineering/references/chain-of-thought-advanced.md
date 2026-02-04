# Chain-of-Thought Advanced Patterns

## Least-to-most prompting

Break the problem into subproblems, solve in sequence, then synthesize.

```
Decompose the problem into 2-4 subproblems.
Solve each subproblem in order.
Combine the results into a final answer.
```

## Tree-of-thought exploration

Generate multiple candidate reasoning paths, score them, and continue the best.

```
Generate three different solution paths.
Score each path 0-10 for correctness and completeness.
Continue with the highest-scoring path.
```

## Verification step

Add a second pass that checks the steps before finalizing.

```
Step 1: Solve the task with numbered steps.
Step 2: Verify each step for errors.
Step 3: Provide the corrected final answer only.
```

## Adaptive depth

Increase reasoning depth only if the initial attempt fails.

```
Attempt a 3-step solution.
If any step is uncertain, retry with 5 steps.
Return the final answer.
```

## Guardrails

- Keep reasoning sections short and structured.
- Avoid mixing multiple new instructions per iteration.
- Require the final answer to be explicit and separate.
