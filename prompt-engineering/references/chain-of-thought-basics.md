# Chain-of-Thought Basics

## Purpose

Chain-of-thought prompting elicits structured reasoning for multi-step tasks. Use it when correctness depends on intermediate steps, not for simple lookups.

## When to use

- Multi-step math or logic problems.
- Tasks with explicit verification requirements.
- Outputs that benefit from step-by-step traceability.

## When to skip

- Simple factual questions or short summaries.
- Latency-sensitive responses where brevity is required.
- Tasks where exposing intermediate steps is not desired.

## Core patterns

### Zero-shot reasoning cue

```
Task: {task}

Think step by step, then provide the final answer.
```

### Few-shot reasoning cue

```
Q: {example_question_1}
A: Step 1 ... Step 2 ... Final: {example_answer_1}

Q: {example_question_2}
A: Step 1 ... Step 2 ... Final: {example_answer_2}

Q: {task}
A:
```

### Reason + answer split

```
Solve the task using numbered steps.
Return:
1) Reasoning steps
2) Final answer only
```

## Decision points

- If the model makes arithmetic mistakes, add explicit verification steps.
- If outputs are too long, require a fixed number of steps.
- If reasoning becomes inconsistent, introduce a short example.

## Common pitfalls

- Ambiguous step formatting (no numbering or labels).
- Mixing multiple changes at once during iteration.
- Adding examples that contradict required constraints.

## Minimal evaluation checks

- Steps follow the required format.
- Final answer matches the last step.
- No missing intermediate calculations.
