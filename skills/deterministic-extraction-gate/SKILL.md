---
name: deterministic-extraction-gate
description: "Decides whether a model belongs in a text-extraction loop at all, then builds the seam: a deterministic parser that accounts for every region of its input, reason-code flags rather than a confidence score, escalation of flagged records only, and a labelled sample that measures the miss rate. Use when extracting fields from many similarly shaped records."
metadata:
  category: ai
---
# Regex versus a model for structured text

Provides the routing decision that comes before any extraction pipeline — should a model be in this loop at all — and, where the answer is "only for the hard minority", the seam that splits the work.

Writing a parser for consistently formatted text is not the interesting part; a competent agent does that unprompted. The interesting part is the **seam**: a programmatic flag set that routes a minority of records to a model, and an instrument that says how often the flag set is wrong. Left to itself, extraction work commits to all-code or all-model, and when it does build a hybrid it rarely measures the gate. A gate nobody measures is a gate that reports whatever its author assumed.

## Use this skill when

- The same fields must be pulled from many records that share a shape — line items, form entries, log lines, exported rows, repeated blocks in a document.
- The choice between writing a parser and calling a model per record is still open, and cost, latency, or run-to-run reproducibility matter.
- A model is already extracting every record and the run's cost or variance has become the problem.
- A parser is believed to be correct and nothing measures how often it is quietly wrong.

## Do not use this skill when

- **The input is free-form with no stateable record boundary.** Route the whole input to a model; prompt design owns the extraction prompt. There is no parser to gate.
- **The text is tool output on its way into an agent's context.** A stricter contract owns that path — set membership over whole lines rather than field extraction, tiered fail-open behavior, and a threat model that includes injection, which this one's does not.
- **The goal is to freeze an exploration that already succeeded into a replayable unit on disk.** Codification work owns that, and its entry condition assumes interpretation already *is* a pure function. This skill is the one that decides whether it can be.
- **The format is machine-specified and a conformant reader exists** — a serialization format, a schema-backed wire format, a declared dialect with a real reader. Use the reader; there is nothing to gate.
- **A handful of records, extracted once.** A model call is cheaper than a parser. No pipeline, no gate, no labelled sample.
- **The correctness requirement is total** — legal filings, financial postings, medical records. Neither branch qualifies, and a gate that routes a small percentage to a model is a false assurance dressed as a control. Route to a process with human adjudication.

## Workflow

1. **Sample and characterize.** Draw a random sample from the corpus. Write down the record boundary and the required fields. If no record boundary can be stated over that sample, stop — this is free-form, and the stand-down above applies.
2. **Write the deterministic parser** over the record grammar the sample showed — a regular expression, a real grammar, a dialect-aware reader, a structural walk; whatever the format earns. Regular expressions are one option among these, not the technique. **Interpretation must be a pure function of one input string** — same input, same output, no I/O — because an impure parser cannot be replayed against the labelled sample in step 5, and a gate that cannot be replayed cannot be measured.
3. **Account for coverage, not only for output.** Every region of the input is either consumed by a matched record or recorded as an unmatched region with its offsets. This is the step that is usually missing, and its absence is what blinds the gate: text the parser never matched produces no record, and a record is the only thing a per-item check can inspect. A parser that reports only what it found cannot report what it lost.
4. **Flag with reason codes, never with a score.** Each check emits a named reason — `missing_required_field`, `field_count_out_of_range`, `unmatched_region`, `value_failed_type_check`, `duplicate_identifier`, `field_crosses_record_boundary`. Any flag escalates. Do not compose penalties into a pseudo-continuous confidence unless the weights were fitted against labelled data; an unfitted weighted sum is a boolean wearing a decimal point, and it hides which check fired.
5. **Adjudicate on a labelled sample before shipping the escalation path.** Hand-label a sample and measure **two** rates: the **escalation rate** (flagged ÷ total) and the **miss rate** (records that were wrong *and* unflagged ÷ total). The miss rate is the number that says whether the gate works at all. A pipeline that reports only its escalation rate is reporting how much it spent, not how much it got right.
6. **Gate on those two rates.** Miss rate above what the consumer tolerates → the flag set is wrong: add a check that catches the observed misses, or escalate everything. Escalation rate above the cost budget → tighten the parser, never loosen the flags. Both tolerances belong to the consumer of the data; this procedure supplies neither and no default is offered.
7. **Escalate flagged records only**, each carrying its raw source region. Use the cheapest model that clears the labelled sample — established by running the sample, not by reputation. The model returns a correction or a no-change sentinel; it never sees and never rewrites an unflagged record.
8. **Never mutate parsed records.** Corrections produce new instances, so a before/after diff over a run stays auditable and a bad correction is attributable.
9. **Log both rates per run.** A change in the source format surfaces first as a rising escalation rate, well before it surfaces as bad data downstream. That early signal is most of the value of having a gate. An absent or stale miss rate is logged as absent, never as zero.

## Examples

**Coverage accounting versus a per-item scorer.** Three records, one malformed — the middle line carries a space where its second separator belongs, so the pattern never matches it at all.

```python
import re

RECORD = re.compile(r"^(?P<id>\d+)\|(?P<name>[^|]+)\|(?P<qty>\d+)$", re.M)

def parse(text):
    """Pure: same input, same output, no I/O. Returns records AND what was never matched."""
    records, unmatched, cursor = [], [], 0
    for m in RECORD.finditer(text):
        gap = text[cursor:m.start()]
        if gap.strip():
            unmatched.append((cursor, m.start(), gap.strip()))
        records.append(m.groupdict())
        cursor = m.end()
    if text[cursor:].strip():
        unmatched.append((cursor, len(text), text[cursor:].strip()))
    return records, unmatched

def reasons(records, unmatched):
    """Reason codes, never a score. Any code escalates that region or record."""
    out = [("unmatched_region", f"{s}:{e}") for s, e, _ in unmatched]
    out += [("missing_required_field", r["id"]) for r in records if not r["name"].strip()]
    return out

def blind_score(rec):            # the wrong instrument: it can only see what parsed
    return 1.0 if rec["name"].strip() else 0.5

SAMPLE = "101|widget|4\n102|gadget 7\n103|sprocket|2\n"
records, unmatched = parse(SAMPLE)
print(len(records), reasons(records, unmatched), [blind_score(r) for r in records])
# 2 [('unmatched_region', '12:26')] [1.0, 1.0]
```

The scorer gives every record it can see full marks, because both records it can see are fine. Record `102` was never parsed, so it was never scored, so it was never escalated — it left the pipeline as silence. Coverage accounting reports the gap at offsets 12 to 26 and escalates the raw text, which is the only route by which a model ever gets to look at it.

**A wrong version of the same gate.** Penalties of 0.3, 0.5 and 0.2 subtracted from 1.0, escalating below 0.95, is not a tunable confidence cutoff — every threshold between 0.8 and 1.0 produces identical behavior, because the score can only be 1.0 or at most 0.8. It is an any-flag-raised boolean with a decimal point painted on, and the decimal point makes it look calibrated.
