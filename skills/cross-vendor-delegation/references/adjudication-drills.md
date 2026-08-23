# Adjudication drills

Worked pairs for the closing recommendation line, plus the shapes the adjudication step emits. The rule is in `SKILL.md`; this file is the drill set.

## The format

```
Recommendation: <action> because <reason>
```

The reason has to do two things at once: name a specific finding, and compare it against a named alternative. The alternative is one of three kinds — another finding, fixing versus shipping, or fix order. A reason that names a finding but compares it to nothing is half the format; a reason that compares without naming anything is rhetoric.

## Failing reasons

These fail on shape, not on phrasing, and rewording them does not repair them:

- `Recommendation: Fix the issues because it's better.` — no finding, no comparison.
- `Recommendation: Address the feedback because the adversarial pass found things.` — reports that the delegation happened.
- `Recommendation: Follow the delegate's advice because it raised good points.` — defers the decision while appearing to make it.
- `Recommendation: Ship because nothing looked blocking.` — a verdict restated as a reason, and one the gate should have produced.
- `Recommendation: Fix the race condition because races are dangerous.` — names a finding, compares it to a general truth rather than to an alternative.

## Passing reasons, by outcome

**Fix first — compared against another finding.**

`Recommendation: Fix the injection at the user lookup before the traversal issue because its auth-bypass blast radius is larger and the parameterized-query fix is three lines against the traversal's session-handling rewrite.`

The comparison is explicit on two axes at once, severity and cost, and it produces an order rather than a list.

**Ship as-is — compared against fixing.**

`Recommendation: Ship as-is because all three findings are cosmetic and the gate passed; fixing them delays the release without changing observable behavior.`

Ship recommendations are the ones most often written as boilerplate. The reason has to name what was found and argue that acting on it costs more than it returns.

**Investigate before merging — compared against a second finding's timing.**

`Recommendation: Investigate the flagged write ordering before merging because its failure mode is silent corruption, which is far harder to detect after shipping than the harness gap also raised, which a follow-up can carry.`

Detectability-after-ship is a legitimate comparison axis and is frequently the decisive one.

**Adopt the delegate's proposal — compared against its own alternative.**

`Recommendation: Adopt the sharding proposal because it removes the head-of-line blocking in the current writer pool, while the caching alternative the delegate also floated leaves the single-writer hot path in place.`

**Reject the delegate's proposal — with an argued reason.**

`Recommendation: Reject the "switch datastores" proposal because the team's operational experience with the current one outweighs the simplicity gain at the projected scale, and the delegate's secondary proposal — read replicas — already answers the read-load concern that motivated the switch.`

A rejection is a first-class outcome and needs the same rigor as an adoption. Rejecting on grounds the delegate could not have known — operational context the payload never carried — is the strongest form, because it names exactly what the foreign view was missing rather than dismissing it.

## Disagreement notes

Where the caller's own reading differs from the delegate's, the note is a position with a reason, placed after the verbatim block:

- Weak: "There is some disagreement about the caching approach." Names no position and commits to nothing.
- Strong: "This report disagrees that the cache layer is redundant: the delegate did not receive the read-volume figures, and at the volumes measured the layer removes roughly the majority of primary reads. The delegate's point about invalidation complexity stands."

Conceding the part that survives is what keeps the note a position rather than a defense.

## Overlap buckets

```
Both found:            <findings present in the delegate's output and the caller's own pass>
Only the delegate:     <findings unique to the delegate>
Only this pass:        <findings unique to the caller>
Agreement: N of M unique findings overlap
```

Reporting rules:

- The ratio is computed over unique findings after de-duplicating differently-worded descriptions of the same defect. Two names for one defect inflate both the denominator and the disagreement.
- Overlap is the highest-confidence bucket; it is not the only actionable one. A finding only one side raised is the return on delegating.
- The ratio is reported, never gated on. No threshold over it is defensible without measurement, and the source carries none.
- Where no comparable pass of the caller's own exists, report the ratio as unavailable rather than running one afterwards to produce it. A pass run after reading the delegate's output is not independent and its overlap means nothing.
