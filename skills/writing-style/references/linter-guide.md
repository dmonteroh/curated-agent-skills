# Linter guide

Operating knowledge for `scripts/writing_lint.py`: the caps and where they come from, the glossary file, and how to break a rule on purpose. Open this to run the gate. To write better, open `writing-guide.md`.

## The caps

One register, one set of caps. The linter had four profiles once. A 97-run trace audit removed them: agents invented profile names in 15% of invocations, each a failed gate, and split two byte-identical options by coin flip.

| Cap | Hard (blocking) | Soft (advisory) |
| --- | --- | --- |
| Sentence, words | 35 (L01) | 25 (A01) |
| Paragraph, sentences | 8 (L10) | 6 |

The values are measured, not chosen by feel. Across eight documents this library treats as good writing, p90 sentence length ran 17-29 words and p95 ran 21-38. The soft cap sits at the p90 band and the hard cap above the p95, so accepted prose passes and an outlier fires.

The tighter 20-word, one-instruction form for procedures and error strings is rule 12 in `SKILL.md`, prose only: the linter reads the text alone and cannot know a sentence is a procedure step.

## The glossary

One concept, one name. Pass it with `--glossary`, as JSON mapping the canonical term to the alternates that must not appear:

```json
{
  "worker": ["agent", "runner", "executor"],
  "run": ["execution", "invocation"],
  "customer": ["client", "user", "account holder"]
}
```

Rule L12 fires on any alternate and names the canonical term in its message. Two rules of thumb decide what belongs here:

- Add a concept once the same thing has been called two things in one repository. Not before.
- Never add a pair that is a real distinction. If `user` and `customer` mean different things in this system, they are two entries, not one entry with an alternate.

Without a glossary L12 cannot fire, and term drift falls to the term gate as a human check.

## Breaking a rule on purpose

**Input**

> Delete the row only after the export finishes and the checksum matches, unless the run is a dry run, in which case delete nothing, report the intended deletion, and keep the export file for the audit trail.

At 37 words this fires L01. Every clause is load-bearing: two conditions, one exception, and three different actions inside the exception. Splitting it into four sentences separates the exception from the actions it governs, which is the ambiguity the cap exists to prevent.

The correct handling is a suppression carrying the reason, and a `Kept as-is:` line in the delivery:

```markdown
<!-- writing-lint: allow L01 the dry-run exception must stay attached to the action it governs -->
```

In source files the same directive rides an ordinary comment: `# writing-lint: allow L05 the vendor's own wording, quoted`. A directive on its own line covers the next line. An inline directive covers its own line. `disable-file` covers the file. A directive with no reason is itself a violation.

A cap that cannot be broken with a written reason is not a cap. It is a rule that produces worse text in the case its author did not consider.
