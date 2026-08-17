# Bounded Variant Search

Use this reference during the optimize phase, when "make it faster" has to become a search over concrete variants. It bounds the search before it starts, keeps each delta attributable, names the conditions that end it, and gates what becomes the new default.

## Declare the budget before the first variant

A pass with no declared end runs until someone stops paying attention, and its result is whatever happened to be measured last. Write these down before changing any code:

- the operation under optimization, named precisely enough to re-run from the note alone;
- the correctness gate that must stay green — the tests, invariants, or output comparison that decide whether a variant is admissible at all;
- the metric being optimized, chosen explicitly: wall time, p95 latency, rows/sec, cost per run, peak memory, error rate, freshness age;
- the current baseline for that metric, with the environment it was measured in;
- the search budget: maximum number of variants, maximum wall-clock or agent time, maximum spend, and maximum data impact — what the search is allowed to write, migrate, or delete.

The budget's values are **chosen per pass**, not derived. There is no correct default number of variants or minutes; set them against what the win is worth and record the choice next to the baseline so a reader can see the search was bounded on purpose.

When the requested target is unrealistic ("make it 20x faster"), keep the ambition and bound the loop anyway. An unreachable target is a reason to declare the budget, not a reason to skip it.

## One hypothesis per variant

Each variant tests exactly one idea and runs against the same input shape as the baseline. Two changes in one variant produce a delta that cannot be assigned to either.

Wrong — `batch-and-parallel`: batches writes and raises worker count in one variant, comes back faster, cause unknown. It is now impossible to learn that batching carried the whole win while the extra workers were quietly costing error rate.

Right — `batch-500` measured alone; then `parallel-8` layered on top of the accepted batching variant and measured against it.

## Keep a ledger

Persist every run, including the rejected ones. A rejected variant is the evidence that stops the same idea being retried three rounds later.

```text
Variant     | Hypothesis        | Command                    | Metric | Correct? | Notes
baseline    | current path      | <job command>              | 120s   | yes      | stable over 3 runs
batch-500   | fewer round trips | <job command> --batch 500  | 42s    | yes      | accepted
parallel-8  | more workers      | <job command> --workers 8  | 31s    | no       | upstream rate limit, rejected
```

The rows above are illustrative shape, not targets. What matters is that every column is filled for every run: a ledger row without its exact command cannot be reproduced, and a row without a correctness verdict cannot be promoted.

## Compare against the best accepted variant, not the previous run

Run-to-run comparison lets a search walk downhill: each step looks like an improvement on the step before it while the whole sequence drifts below a winner found three rounds ago. Measure every candidate against the current best *accepted* variant — the one that passed the correctness gate — and let the ledger be what makes that comparison possible.

Where the work is recursive or a hyperparameter sweep, keep a holdout as well: a set of inputs, or a replay of recorded traffic, that never steers variant selection and is run against the winner before promotion. A variant tuned on the same workload that selected it will report a delta it does not have on traffic it has not seen; the holdout is what catches that.

## Stopping conditions

Stop the search — do not merely slow it down — when any of these fires:

- the improvement over the best accepted variant is within run-to-run noise, where noise is measured by repeating the baseline against itself rather than assumed;
- correctness fails, and the failure is in the approach rather than in one variant's implementation;
- the declared budget is spent in variants, time, money, or data impact;
- the search has started changing more variables than it can explain — deltas are no longer attributable to named hypotheses.

The last condition is the one usually missing. It stops a search that has become *unattributable*, not merely one that has become unprofitable. A search producing unexplained wins is producing results nobody can defend in review or reproduce after the next dependency bump.

## Promotion gate

A variant does not become the new default until all of these hold:

- correctness tests pass on the variant as it will ship, not on a near-relative of it;
- the delta is repeated across runs, or explained by a mechanism someone can state;
- rollback is obvious — a flag, a revert, or a documented config change;
- the change is encoded somewhere durable: source control, a script, a test, or a runbook, never only in the session transcript that found it;
- the summary carries the exact commands and measurements that produced the delta;
- no metric outside the optimized one regressed unnoticed — check freshness age, error rate, and saturation before promoting a latency win.

Then re-run the baseline and the winner together, in the same environment and the same session, and confirm the delta survives. A delta assembled from two sessions includes whatever else changed on the machine between them.

## Reporting honesty

Report the outcome as the **best measured safe variant**, never as "optimal" or "the global optimum", unless the search space was genuinely exhausted — and a bounded search by construction did not exhaust it. Carry two more facts into the report: the budget actually spent, and which stopping condition fired. They are what tell the reader whether the search ended because it converged or because it ran out of room, and whether more budget is worth spending later.
