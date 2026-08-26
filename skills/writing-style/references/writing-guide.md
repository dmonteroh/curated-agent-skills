# Writing guide

Everything `SKILL.md` compresses. Four parts: the caps and their provenance, the glossary shape, which ASD-STE100 rules the linter enforces against which it only prefers, and worked before-and-after pairs.

## The caps

One register, one set of caps. The linter had four profiles once. A 97-run trace audit removed them: agents invented profile names in 15% of invocations, each a failed gate, and split two byte-identical options by coin flip.

| Cap | Hard (blocking) | Soft (advisory) |
| --- | --- | --- |
| Sentence, words | 35 (L01) | 25 (A01) |
| Paragraph, sentences | 8 (L10) | 6 |

The values are measured, not chosen by feel. Across eight documents this library treats as good writing, p90 sentence length ran 17-29 words and p95 ran 21-38. The soft cap sits at the p90 band and the hard cap above the p95, so accepted prose passes and an outlier fires.

### The tighter target the linter cannot hold

ASD-STE100 caps a procedure sentence at 20 words with one instruction in it, and that limit is rule 12 in `SKILL.md`, not a linter rule. The linter reads the text alone and cannot know that a sentence is an error string, a runbook step, or a message another agent will parse. The writer knows. Apply the 20-word, one-instruction form to anything read once, under pressure, or by a machine: error messages, log lines, tool descriptions, procedure steps, instructions handed to another agent. The linted caps govern everything else.

One question decides the tight form: **who acts on this, and can they ask a follow-up?** No back-channel and a real cost of misreading means the tight form.

### What a report adds

Reports and briefs share the caps. The habits are their own, and the linter cannot check them:

- **Lead with the outcome.** The first sentence answers what happened or what was found. Supporting detail comes after, for the reader who wants it.
- **Say what changed and what is next.** A report that ends without a next step makes the reader write back to ask.
- **Name the uncertainty where it exists.** A hedge in a report is content, and the modality gate protects it.

### The glossary

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

### Keeping this file honest

Three failure modes, all seen in the material this skill was built from:

1. **Another organisation's residue.** A house-style block imported wholesale carries decisions nobody here made. Delete what the repository has not chosen rather than inheriting it.
2. **A rule with no escape hatch.** An absolute such as "no sentence under three words" will produce worse text in a case its author did not consider. Every entry here can be overridden with a reason.
3. **An unearned number.** A cap that arrived by copying rather than measuring is a chosen default and says so. The linter's own caps carry their measurement in `scripts/writing_lint.py`.

## The rules behind the register

ASD-STE100 is a controlled natural language, first released in 1986 by the aerospace and defence industry. European airlines asked for it: their maintenance staff mostly read English as a second language, and a technician on a tarmac has no author to call. The Simplified Technical English Maintenance Group maintains it, and it has been free to obtain since Issue 6 in 2013.

The standard has two halves: writing rules that describe sentence shape, and a dictionary of approved words. **This skill carries the first half and cannot carry the second.**

### What the licence prevents

The dictionary holds roughly 900 approved words, each restricted to one meaning and one part of speech, plus roughly 1,200 words to avoid with suggested replacements. It is free to obtain and **not** free to redistribute: reproduction requires written authority from ASD, granted freely only to a listed set of organisations that this library does not belong to. The dictionary therefore stays out of this repository.

The consequence is specific rather than cosmetic. Every rule defined by "use an **approved** word" degrades from a checkable standard into a preference for the plainer word. Rule L13 in the linter exists to stop any output claiming otherwise. For documentation that must actually conform, obtain the standard and check word by word against the real dictionary.

### Structural rules — the linter decides these

Each one can be pointed at: a word, a punctuation mark, or a count.

| Rule | What it says | Linter |
| --- | --- | --- |
| Sentence length | Cap the sentence. Procedures are capped tighter than description | L01, A01. The tighter 20-word procedure cap is `SKILL.md` rule 12, prose only |
| One instruction per sentence | A procedure sentence carries one action | `SKILL.md` rule 12, prose only. As a linter rule it fired on 7.3% of accepted prose: deciding that a sentence is a procedure step takes knowledge the text alone does not carry |
| No semicolon | Rule 8.1 bans the mark outright, and permits every other standard mark. The em dash is not banned by the standard | L02, L03 by house style |
| Paragraph limit | One topic per paragraph, and a sentence cap | L10 |
| Lists for sequences | Three or more steps or conditions become a list rather than one sentence | not automated |
| No dropped words | Keep the subject, the verb, and the article, even where the sentence reads longer. Dropping them creates ambiguity rather than brevity | not automated |
| No phrasal verbs | Rule 9.3. A verb plus a preposition has meanings the parts do not predict, and both non-native readers and translation systems mishandle them | L04 |
| Active voice | Required for procedures. Permitted in description only where the actor is genuinely unknown or irrelevant | A02 |
| Simple tenses | Infinitive, imperative, simple present, simple past, simple future, and past participle as an adjective. No present perfect or other compound forms | A03 |
| Safety instructions | Open with the command or the condition, never bury it mid-sentence | not automated |

Two of these are advisory rather than blocking, for the same reason in both cases. The detection is a regular expression over surface forms, and English supplies counter-examples it cannot separate. A passive is right where the actor is unknown. A present perfect is right where "the job has completed" and "the job completed" are different statements. **Where the compound form carries information the simple form loses, keep it and suppress the rule with that reason.**

One rule from the standard is deliberately absent from the linter. Noun clusters are capped at three words by ASD-STE100, and deciding where a noun cluster starts needs part-of-speech tagging that a standard-library tool cannot do. An earlier build tried it and fired on ordinary prose such as "current Claude Code prompt". It was removed rather than shipped noisy. Check noun stacks by eye: four or more nouns in a row become a phrase with a preposition in it.

### Lexical rules — direction of travel only

| Rule | What to do | Why it is weaker here |
| --- | --- | --- |
| One word, one meaning | Pick one verb per action and reuse it every time. Never rotate "check", "verify", and "confirm" for the same act | Consistency inside one document is checkable, and rule L12 checks it against a supplied glossary. Which word is the *approved* one is not checkable without the dictionary |
| One part of speech per word | Prefer "apply oil to the valve" over "oil the valve" where both read equally well | Whether a word is approved as a noun only is a dictionary fact |
| Verb, not noun | Rule 3.7. "Analyze the log", not "perform an analysis of the log" | Preferring the verb form is safe anywhere. Knowing which verb is approved is not. Detected as A05 |
| Plainest available word | Choose the shorter, more common word over the formal or rare synonym | The base list of plain words is the dictionary |
| Domain terms | Keep the technical noun the text needs and define it once. The standard allows a project glossary beyond its base dictionary | The glossary allowance is real. The base dictionary it extends is absent |

### Why the register does not flatten prose

The standard was written for aircraft manuals, where flat is correct. This skill applies it to briefs, reports, and documentation, where flat is a different failure: even sentence length with no variation is one of the marks of generated text. Rule A06 exists for that reason and fires when a document's sentence-length spread falls below anything measured in accepted writing. The register removes ambiguity, filler, and unearned claims. It does not remove rhythm.

### Sources

- ASD-STE100 official site: `asd-ste100.org`, including its About page and its downloads request form.
- ASD Europe's Simplified Technical English page.
- The Wikipedia article "Simplified Technical English".
- TechScribe's ASD-STE100 summary.
- SKYbrary's Simplified Technical English entry.

Rule numbers cited above (3.7, 8.1, 9.3) come from those public descriptions of Issue 9, January 2025. Verify them against the standard itself before quoting them anywhere that matters. This file paraphrases rule categories and reproduces no part of the standard's text.

## Worked pairs

One per register, plus two cases that are not rewrites. Every "after" preserves each fact, number, condition, and hedge in its source. Where it does not, the pair says so.

### Instruction — an error message

**Before**

> An error may have occurred while processing your request due to a possible mismatch in the expected data format, which could be caused by an outdated client version.

What fires: L06 with three hedges stacked, A01 at 26 words, A02 on `be caused`. Rule 12 asks more of an error string than the linter does: 20 words, one instruction per sentence, because a person under pressure reads it once.

**After**

> The request may have failed. The data format did not match what the server expected. An outdated client can cause that mismatch, so check your client version.

Two calls worth stating rather than hiding. `may have` survives: the system suspects the failure and does not know it, and dropping the auxiliary would delete the uncertainty along with the tense. `could be caused by` became `can cause`, which keeps the possibility and drops one hedge, because three hedges in one sentence assert nothing.

**The wrong after**, and the reason this pair leads the file:

> The request failed. The data format did not match what the server expected. Check your client version, since an outdated client is the most common cause.

It reads better than the right one. It also asserts a failure the system only suspects, and invents a frequency claim that appears nowhere in the source. A rewrite that supplies a cause, a frequency, or a mechanism has stopped being a rewrite.

### Instruction — a message to another agent

**Before**

> Once the upstream job has completed successfully, assuming no errors were encountered during the process, the downstream consumer should proceed to consume the output artifact, though it is worth noting that in the event of a timeout the artifact may be partial.

What fires: L01 at 42 words, L07 on `it is worth noting that` and `in the event that`, A03 on `has completed`, A02 on `were encountered`.

**After**

> Wait for the upstream job to finish with no errors. Then read the output artifact. A timeout can produce a partial artifact, so check that the artifact is complete before you use it.

The final clause is **added content**, not a rewrite. The source warned about partial artifacts and never said what to do about them. Making the warning actionable is an improvement and it is called out here rather than passed off as compression. If the source's silence was deliberate, drop that clause.

### Documentation — a README paragraph

**Before**

> Our caching layer is designed to slot seamlessly into your existing stack with minimal friction and no vendor lock-in; it leverages semantic similarity to dramatically reduce the cache misses that traditionally plague LLM workloads.

What fires: L02 on the semicolon, L05 on `seamlessly`, A08 on `leverages`, A01 at 33 words.

**After**

> A normal cache matches requests by exact text, so a small change in wording causes a miss. This cache compares the meaning of a new prompt against the prompts it already holds. It runs beside your current stack and stores no data outside it.

The claims survive and the adjectives do not. `Seamlessly` and `minimal friction` claimed a quality. The rewrite shows the mechanism instead. Note that no sentence here is short: the register caps the outliers and leaves the rhythm alone.

### Report — a finding

**Before**

> It appears that there may be an issue with the way in which the signup funnel is currently being instrumented, as the property that identifies the plan the user selected has not been being sent on the final step of the funnel since around the middle of last month, which means that any breakdown by plan is likely to be undercounting.

What fires: L01 at 62 words, L06 with `may`, `appears to`, and `likely` in one sentence, A03 on `has not been being sent`.

**After**

> The signup funnel drops the plan property on its final step. The property stopped arriving on 12 May. Every breakdown by plan has undercounted since that date.

`Kept as-is:` nothing. The vague date became exact because the source data supplied it. Had it not, the right sentence is "the property stopped arriving in mid-May", not a date the writer chose.

### Correspondence — a stakeholder note

**Before**

> Hi team, just wanted to reach out and circle back on the incident from last night. Great question from Priya on the call. We're going to dive into the root cause and I'll loop you in once we have more clarity, but at the end of the day the important thing is that customers weren't impacted.

What fires: L04 on `reach out`, `circle back`, `dive into`, and `loop you in`, L07 on `at the end of the day`, L08 on `Great question`.

**After**

> Hi team, an update on last night's incident. Priya asked on the call how far it reached: no customer requests failed, and we have confirmed that against the gateway logs. We are still looking for the root cause and I will write again once we know it.

Contractions and first person are correct in correspondence. What went is the business idiom and the reassurance that carried no evidence. Note the addition of *how* the no-impact claim was checked, which the source asserted and did not support.

### Not a rewrite — the text already passes

**Input**

> The migration took a weekend, most of it waiting on backfills. It worked.

Nothing fires. One short emphatic sentence, one specific unglamorous detail, no hype and no hedging. Report that the text already holds the register and change nothing. Editing this produces flatter text, not better text.

### Not a rewrite — quoted material

**Input**

> The on-call engineer wrote: "honestly it was a total mess, we basically just guessed at the threshold and it seemed to work."

The quotation carries a verbal tic, a filler word, and two hedges. All of them stay. The linter skips blockquotes for exactly this reason, and a rewrite that "cleans up" a quotation has falsified a record.

### Breaking a rule on purpose

**Input**

> Delete the row only after the export finishes and the checksum matches, unless the run is a dry run, in which case delete nothing, report the intended deletion, and keep the export file for the audit trail.

At 37 words this fires L01. Every clause is load-bearing: two conditions, one exception, and three different actions inside the exception. Splitting it into four sentences separates the exception from the actions it governs, which is the ambiguity the cap exists to prevent.

The correct handling is a suppression carrying the reason, and a `Kept as-is:` line in the delivery:

```markdown
<!-- writing-lint: allow L01 the dry-run exception must stay attached to the action it governs -->
```

A cap that cannot be broken with a written reason is not a cap. It is a rule that produces worse text in the case its author did not consider.
