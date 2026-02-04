# Concept Explanation Blocks

Use these blocks when a key concept needs a short, reusable explanation.

## Decorators

**Definition**: A decorator wraps a function to add behavior without changing the original body.

**How to explain**

- What it wraps and why.
- The input/output that remains unchanged.
- The extra behavior it adds (timing, logging, access checks).

**Mini example**

```python
@timer
def slow_function():
    do_work()
```

**In this code**: Call out the specific function being wrapped and the side effect.

## Generators

**Definition**: A generator yields values lazily, producing one item at a time.

**How to explain**

- What data sequence it emits.
- Why laziness matters (memory, streaming, backpressure).
- Where iteration happens in the call path.

**Mini example**

```python
def count_up_to(n):
    i = 0
    while i < n:
        yield i
        i += 1
```

**In this code**: Note where the generator is consumed and the stop condition.

## Recursion

**Definition**: A function calls itself until it reaches a base case.

**How to explain**

- The base case and termination condition.
- The shrinking input and progression toward the base case.
- The return value as the call stack unwinds.
