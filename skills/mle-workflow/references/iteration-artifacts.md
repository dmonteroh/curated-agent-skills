# Iteration artifacts

Two field templates. The first is written before model code; the second after each iteration. Both are deliberately short enough to sit in a change description and precise enough that another engineer can argue with the trade-offs rather than with the tone.

## The iteration compact

Written before touching model code, and revised when any line of it stops being true.

```text
Goal:
Who cares:
Decision owner:
User or system action the model changes:
Success metric:
Guardrail metrics:
Mistake budget:
Unacceptable mistakes:
Acceptable mistakes:
Assumptions:
Constraints:
Labels and data snapshot:
Baseline:
Candidate signals:
Threshold or configuration plan:
Evaluation slices:
Known risks:
Next experiment:
Rollback or fallback:
```

This is the model-work equivalent of a design note. It is what keeps a team from optimizing a metric nobody trusts, adding features that do not address the real error mode, or shipping complexity with no way back.

Two lines carry more weight than the rest. **Unacceptable mistakes** is what turns a metric into a gate — a mistake nobody will accept has to appear as a guardrail or a slice, not as a hope. **Rollback or fallback** written at this stage is a design constraint; written after the first incident it is a post-mortem action item.

## The observation ledger

Written after each iteration, beside the code, the change description, the experiment report, or the runbook.

```text
Iteration:
Change:
Why this mattered:
Metric movement:
Slice movement:
False positives:
False negatives:
Unexpected errors:
Decision:
Trade-off accepted:
Lesson captured:
Regression added:
Debt created:
Next iteration:
```

The ledger exists so model work accumulates. The test of an entry is whether it makes the *next* decision cheaper — a row recording only that a metric moved fails that test, and a row recording which mistake class moved and what was traded for it passes it.

**Regression added** is the line that most often stays empty and should not. An important mistake that was fixed but never pinned as a regression test, an evaluation slice, or a dashboard panel will return with the next refresh, and nothing will notice.
