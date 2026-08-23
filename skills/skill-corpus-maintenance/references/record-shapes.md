# Record shapes

Three records carry a maintenance pass: the inventory the collector emits, the verdict record the item branch writes, and the candidate record the promotion branch writes. Field names below are a suggested default — what is load-bearing is that each field named as required is present, and that the record lives outside the corpus being audited.

Every value shown is illustrative. No count, timestamp, or line number here was measured.

## Inventory record

Emitted by `scripts/inventory.sh`, one document per corpus role.

```json
{
  "role": "capability",
  "entry": "SKILL.md",
  "generated_at": "2026-08-17T09:14:02Z",
  "roots": [
    { "path": "/corpus/shared", "found": true,  "count": 2 },
    { "path": "/corpus/project", "found": false, "count": 0 }
  ],
  "total": 2,
  "items": [
    {
      "root": "/corpus/shared",
      "path": "/corpus/shared/alpha/SKILL.md",
      "name": "alpha",
      "description": "…",
      "mtime": "2026-07-30T11:02:44Z",
      "lines": 164
    }
  ]
}
```

Required to be present, not merely emitted:

- **`roots[].found`.** A root that does not exist is a state, not a failure. The report says which roots were searched and which were absent; a pass over one of two intended roots that does not say so reads as a pass over the whole corpus.
- **`mtime`.** The incremental key. An item with no readable mtime is re-evaluated in full rather than carried forward.
- **`path`, not a name.** Two corpora can hold items with the same `name`; only the path is unique.

Run with `-H` to add `headings`, the item's level-2 headings, so a promotion proposal can name a target section rather than only a target file.

## Verdict record — the item branch

One entry per item, keyed by path.

```json
{
  "evaluated_at": "2026-08-17T09:41:18Z",
  "batches": { "total": 41, "evaluated": 41, "status": "completed" },
  "items": {
    "/corpus/shared/alpha/SKILL.md": {
      "verdict": "Merge",
      "target": "/corpus/shared/beta/SKILL.md",
      "reason": "…",
      "mtime": "2026-07-30T11:02:44Z",
      "batch": "authoring",
      "axes": { "sibling_overlap": "…", "standing_overlap": "…", "currency": "…" },
      "decision": "approved",
      "applied_at": "2026-08-17T10:05:00Z"
    }
  }
}
```

- **`status`** is `in_progress` while batches are still running and `completed` only once every item has a verdict. A record found at `in_progress` on the next run resumes at the first item without one; it is never treated as a finished pass.
- **`mtime`** is copied from the inventory entry the verdict was formed against — not from the file at write time, which may have moved during the pass.
- **`decision`** records what the human ruled: `approved`, `modified`, `skipped`, or `pending`. A verdict is a proposal; a decision is the only thing that authorizes a change.
- **`axes`** holds one short finding per axis actually evaluated. An axis with no signal available in this environment is recorded as `"no signal"` and omitted from the reasoning — never defaulted to a value that looks like a measurement.

## Candidate record — the promotion branch

One entry per candidate principle, keyed by a slug derived from the principle itself so the same principle re-identifies across runs.

```json
{
  "distilled_at": "2026-08-17T09:41:18Z",
  "standing_rule_coverage": "full",
  "candidates": {
    "bound-every-retry-loop": {
      "principle": "Give every retry or polling loop an explicit stop condition.",
      "evidence": [
        "alpha: §Workflow step 3",
        "delta: §Constraints",
        "epsilon: §Common pitfalls"
      ],
      "evidence_count": 3,
      "violation_risk": "A loop with no stop condition burns the run's whole budget on one unreachable state.",
      "verdict": "New Section",
      "target": "reliability §Loop bounds",
      "backlink": ["alpha", "delta", "epsilon"],
      "confidence": "medium",
      "draft": "…",
      "decision": "approved"
    }
  }
}
```

- **`standing_rule_coverage`** is `full` when the whole standing-rule text was in the analysis context, `partial` otherwise. A `partial` run's `Already Covered` verdicts are unsafe and the report says so. This field exists because the coverage question is invisible in the output otherwise: a candidate wrongly marked new looks exactly like a candidate correctly marked new.
- **`evidence_count`** is recorded because the promotion threshold is checked against combined evidence after the cross-batch merge, and a reader needs to see the count that cleared it.
- **`backlink`** names the items the principle came from, so the promoted text keeps a route back to the detail that stayed behind.
- **`revision`** is added for a `Revise` verdict only, carrying `reason`, `before`, and `after`. A revision proposal with no `before` cannot be reviewed.

## Keying and re-identification

- Items are keyed by path and compared by mtime. A path that disappeared is reported as removed rather than silently dropped from the record.
- Candidates are keyed by a slug of the principle, not by an index. An index-keyed candidate changes identity whenever a batch order changes, which breaks the one thing the record exists for: telling this run's candidates from the last run's.
- A carried-forward entry keeps its original reason text. It never becomes `"unchanged"` — a record of carried-forward entries with no reasons in it is a record with no decisions in it.
