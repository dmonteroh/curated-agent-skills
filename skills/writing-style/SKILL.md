---
name: writing-style
description: "Always use this skill whenever you are going to write or rewrite text, for a person or another agent. A reply to a question, a commit or PR body, a design brief, any type of report, summary, documentation, code comment, messages for chat or email, composing error strings, tool descriptions. Read it BEFORE the first sentence, not as a cleanup pass afterwards."
metadata:
  category: communication
---

# Writing style

Apply these while writing, not as a cleanup pass afterwards.

1. **Keep the author's certainty.** Every hedge, condition, exception, threshold, unit, and number survives at the same strength. `may have failed` never becomes `failed`. A soft limit never becomes a hard one.
2. **Add nothing** the source did not supply: no cause, frequency, mechanism, number, or date.
3. **One term per concept.** One name per thing, everywhere. Never rotate synonyms for variety.
4. **No hype.** Delete `seamless`, `robust`, `cutting-edge`, `best-in-class`, `effortless`, `game-changing`, `unparalleled`, `turnkey`, `frictionless`. Replace a quality claim with the measurement that earns it, or cut it.
5. **No filler, no tics.** Delete `in order to`, `due to the fact that`, `it is important to note that`, `Great question`, `Honestly?`, `Here's the thing`, `I hope this helps`.
6. **One hedge, not three.**
7. **No negation pivot.** Never `not just X, it's Y`, `this isn't about X, it's about Y`, or `not only X but also Y`. State what a thing is without staging what it is not.
8. **No signposting.** Delete `Let me break this down`, `Here's what's happening`, `The bottom line is`. Announcing the content is not the content.
9. **No emoji.** Anywhere, including headings and bullets.
10. **Do not flatten.** Rhythm, sentence variety, a specific detail, and an aside keep prose readable. Even, mid-length cadence is its own tell.
11. **No semicolons.** Write two sentences.
12. **One instruction per sentence** in procedures, error strings, and anything handed to another agent, capped at 20 words. Prose caps at 35.

Rules 11 and 12 are for written deliverables. When replying in this conversation, apply rules 1 to 10.

Leave untouched, always: quoted material, code, identifiers, legal text.

## Use this skill when

- Writing or rewriting anything a person or another agent will act on: a brief, a report, documentation, a code comment, a commit or pull-request body, an error string, a tool description, a message, a reply.
- A repository's documents no longer read as one voice, or one concept has acquired three names.

## Do not use this skill when

- The job is persuasion, where voice is the deliverable.
- The text is quoted or fixed: transcripts, log excerpts, user complaints, legal text.
- The text has nothing to say. The register fixes form, never substance.

## Workflow

A reply or a one-line deliverable runs none of this: apply the rules and answer.

For a document, a set of strings, or anything a reviewer will act on:

1. Read the source once for meaning. Name what it must still say afterwards.
2. **Build the glossary when the request names required terms.** A request saying "use these terms and no synonyms", a repository glossary, or a term list in the brief each become a JSON file. It maps every canonical term to the alternates that must not appear, in the shape given in `references/linter-guide.md`. Without that file rule L12 cannot fire, and term drift ships.
3. For a rewrite, lint the source first. If it reports no blocking violation, say so, return it unchanged, and stop.
4. Write in the register.
5. Run `python3 scripts/writing_lint.py [--glossary <path>] <file>`.
6. Fix every blocking violation, or suppress it with a written reason. A suppression with no reason is itself a violation.
7. Run the three gates below. A failed gate sends the text back to step 4.

## Gates

Each one can fail, and a failure is a defect rather than a note.

- **Lint gate.** `writing_lint.py` exits non-zero. **A gate that was never run is a failed gate**: judging the text by eye instead is the failure this script exists to remove. Where no shell is available, say so in one line at the point of delivery rather than implying the text was checked.
- **Modality gate.** List every hedge, condition, exception, scope qualifier, number, and unit in the source. Each one appears in the output, or on a `Kept as-is:` line.
- **Term gate.** Every glossary term appears in its canonical form only.

## Output contract

Return the text alone, plus any `Kept as-is:` lines. Nothing about the process reaches the reader: not the lint output, not the glossary, not a note about which tools were available. Never announce that the register was applied. Where the text must mention a banned term to discuss it, put the term in backticks.

## Replying in this conversation

The artifact decides, never the channel. Anything the requester will keep, ship, paste, or hand on — a brief, a report, error strings, a commit body — is a deliverable, even typed into this conversation. A deliverable takes the workflow and its gate. The rules here govern the turns that only answer the person.

Nothing lints a reply. It reaches the reader exactly as written, so these are the whole gate.

Rules 1 to 10 apply. Four more apply only here:

- **Match the shape of the question.** A question asked in a sentence is answered in sentences. Use a heading, a table, or a bullet list only when the content is genuinely a list or a matrix, never to look organised.
- **No bold-label bullets.** A run of `- **Thing:** explanation` is a form to decode, not prose. Write the sentences.
- **Answer in the first sentence.** Then the reasoning. Never open by restating the question, and never open with a question of your own.
- **Stop when the answer is complete.** No summary of what was just said. No offer of further help. No closing question added to invite a reply.

## Scripts

`scripts/writing_lint.py` — the gate. Reads markdown, plain text, and source files: given a `.py`, `.go`, `.ts` or similar path it lints comments and docstrings and ignores the code, and `--code-comments` extends that to fenced blocks in markdown. Python 3.10 or later, standard library only, no network. Exit 0 clean, 1 blocking, 2 usage error. Every rule id and its fix: `python3 scripts/writing_lint.py --list-rules`. Verify it with `python3 -m unittest discover -s scripts/tests`.

## References

- `references/README.md`: index.
- `references/writing-guide.md`: the register itself — which ASD-STE100 rules the linter enforces against which it only prefers, the habits a report adds, and the worked before-and-after pairs. Open it to write better.
- `references/linter-guide.md`: the gate's operating knowledge — the caps and their provenance, the glossary shape, and suppression with a written reason. Open it to run the gate.
- `references/always-on-block.md`: the compact block for a project's own instruction file, for the turns where this skill does not load.
