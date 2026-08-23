# Conversion, selection, and the holdout filter

Working code for the steps where the ordering is the point. Standard library only; no packages, no network, no I/O beyond what a caller supplies. Verify by running the shapes in the worked walkthrough at the end and checking each stated result.

The input record shape assumed throughout — whatever the grading side writes, it carries at least these fields:

```json
{"task_id": "t-042", "trace_id": "t-042-a3",
 "messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}],
 "verdict": "pass", "reward": 0.91, "grader": "exact_match"}
```

## The holdout filter

Run this on selected rows, before shaping. It raises rather than passing a row it cannot check, because a silently unchecked row is the exact failure it exists to prevent.

```python
def holdout_split(rows, holdout_ids, id_field="task_id"):
    """Partition candidate rows against the reserved evaluation identifiers.

    rows: dicts that still carry their source identifier.
    holdout_ids: the identifiers reserved for evaluation.
    Returns (kept, dropped). Raises if any row has lost its identifier —
    a row that cannot be checked must not pass silently, which is the
    whole failure this function exists to prevent.
    """
    missing = [i for i, row in enumerate(rows) if id_field not in row]
    if missing:
        raise ValueError(
            f"holdout_split: {len(missing)} row(s) carry no '{id_field}' "
            f"(first at index {missing[0]}) — run this before shaping strips it"
        )
    kept, dropped = [], []
    for row in rows:
        (dropped if row[id_field] in holdout_ids else kept).append(row)
    return kept, dropped
```

Log `dropped`; do not discard it. A large dropped count is a finding about the collection step — usually that it is resampling the evaluation set rather than real traffic — and it is invisible once the rows are gone.

## Top-fraction selection

```python
def keep_top_fraction(graded, fraction):
    """Keep the highest-scoring `fraction` of rows, never fewer than one.

    graded: (row, score) pairs. `fraction` is tuned against this batch's
    score distribution, not carried over from a previous batch.
    """
    if not 0 < fraction <= 1:
        raise ValueError(f"keep_top_fraction: fraction must be in (0, 1], got {fraction}")
    if not graded:
        return []
    ranked = sorted(graded, key=lambda pair: pair[1], reverse=True)
    keep_n = max(1, int(len(ranked) * fraction))
    return [row for row, _ in ranked[:keep_n]]
```

Fractions around a quarter, over roughly eight sampled candidates per prompt, appear across the sources as working values. They are chosen defaults, not measured optima. The durable part is the tuning rule: read this batch's score distribution and set the fraction against it, because a harder prompt set shifts the whole distribution down and a carried-over fraction then keeps rows an easier batch would have rejected.

## Pair selection, with the collapse check

```python
def select_pair(trajectories):
    """Pick (chosen, rejected, collapsed) from graded attempts at ONE task.

    Each trajectory is a dict carrying 'reward'. `chosen` is the highest
    scorer; `rejected` is the remaining candidate nearest the target point
    below the mean. `collapsed` is True when that target lands at or below
    the lowest score, so the selection degenerates to best-versus-worst —
    the construction the rule exists to avoid. Widen the candidate set
    rather than ignoring the flag.
    """
    if len(trajectories) < 2:
        raise ValueError("select_pair: need at least 2 trajectories to form a pair")
    rewards = [t["reward"] for t in trajectories]
    chosen = max(trajectories, key=lambda t: t["reward"])
    candidates = [t for t in trajectories if t is not chosen]
    mu = sum(rewards) / len(rewards)
    sigma = (sum((r - mu) ** 2 for r in rewards) / len(rewards)) ** 0.5
    target = mu - 2 * sigma          # the multiple is a chosen starting point
    rejected = min(candidates, key=lambda t: abs(t["reward"] - target))
    lowest = min(t["reward"] for t in candidates)
    return chosen, rejected, rejected["reward"] == lowest
```

**Why the flag exists.** Using the population standard deviation, no value in a set of *n* can sit further than `√(n−1)` standard deviations below the mean; the bound is reached only when one value sits alone against `n−1` identical others. Two standard deviations therefore needs `n ≥ 5` before it is even reachable, and reaching it requires that degenerate shape. In practice: fewer than five attempts per task and the target is *always* under the lowest score, so `rejected` is the minimum by arithmetic rather than by selection, and the rule has not bound at all. Even well above five, a set with no mid-range scores collapses the same way. Read the flag; when it is set, sample more attempts per task rather than shipping the pair. (authored — the sources present the two-candidate case as an incidental observation, not as a floor on candidate count.)

## Shaping — and why it runs last

```python
def to_sft_row(record):
    """Reduce a graded record to the training shape.

    Everything that is not the conversation is dropped here — the source
    identifier included, which is why holdout_split has to have run first.
    """
    return {"messages": record["messages"]}


def to_pair_row(chosen, rejected):
    """Build a preference triple from two attempts at the same task."""
    if chosen["task_id"] != rejected["task_id"]:
        raise ValueError(
            f"to_pair_row: cross-task pair ({chosen['task_id']} vs "
            f"{rejected['task_id']}) — a pair is two attempts at one task"
        )
    return {
        "prompt": chosen["messages"][0]["content"],
        "chosen": chosen["messages"][-1]["content"],
        "rejected": rejected["messages"][-1]["content"],
    }
```

`to_pair_row` raises on a cross-task pair rather than building one, because a triple assembled from two different tasks is well-formed data that teaches the wrong thing — it is not detectable downstream by shape.

The identifiers dropped here are not lost: they go to the card's provenance field, which is what makes the after-the-fact holdout check in the workflow possible.

## Human corrections

A corrected failure becomes a training row directly, with the corrected content replacing the failing response. It skips the score threshold — a person already validated it — and the original failing content never enters the set.

```json
{"task_id": "t-311", "verdict": "fail",
 "messages": [{"role": "user", "content": "Extract the invoice total as a JSON number."},
              {"role": "assistant", "content": "The total is around $4,200"}],
 "correction": {"content": "{\"total\": 4200.00}", "corrected_by": "reviewer-07"}}
```

becomes

```json
{"messages": [{"role": "user", "content": "Extract the invoice total as a JSON number."},
              {"role": "assistant", "content": "{\"total\": 4200.00}"}]}
```

It still passes through `holdout_split` first: a corrected row is as capable of being an evaluation item as any other.

## Worked walkthrough

Given three graded records with `task_id` values `t-1`, `t-2`, `t-3` and the reserved set `{"t-2"}`:

1. `holdout_split(rows, {"t-2"})` returns two kept (`t-1`, `t-3`) and one dropped (`t-2`).
2. `[to_sft_row(r) for r in kept]` returns two rows whose only key is `messages`.
3. Calling `holdout_split` on those shaped rows raises `ValueError` naming the missing field — which is the ordering constraint made mechanical rather than advisory.

For pair selection: a set of thirteen attempts scoring `0.95`, ten at `0.9`, one at `0.5` and one at `0.1` selects `0.95` as chosen and `0.5` as rejected, with `collapsed` false. The same call over any two, three, or four attempts returns `collapsed` true and the lowest-scoring candidate, every time.
