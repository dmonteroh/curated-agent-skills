---
name: prose-de-slopping
description: "Edits AI-generated prose into text that reads as human-written, using a catalogue of named tells with concrete replacements plus a guard that stops the pass from flattening legitimate writing. Use when a draft, doc, README, release note, or article reads as machine-written and has to ship."
metadata:
  category: docs
---

Provides a three-part pass: a scan against the catalogue of 35 named tells in `references/ai-tell-patterns.md`, a rewrite of every hit the guard does not protect, and three gates that can fail. The scan list below indexes the catalogue.

Half the procedure is the catalogue. The other half is the guard that decides which hits are legitimate and must survive untouched, because a pass that fires on every dash and every three-item list produces flat, voiceless text, which is its own tell.

## Use this skill when

- A draft, README, pull-request body, release note, or article reads as machine-written and has to ship as human prose.
- Text is being reviewed for AI tells before publication, whether or not anything will be rewritten.
- A writing sample by the intended author is available and the text has to be brought into that voice.
- A document mixes generated and hand-written sections and the seam between them is visible.

## Do not use this skill when

- The text carries scattered tells and no cluster. Editing it anyway strips the author's habits and leaves the prose flatter rather than more human. Report the finding instead.
- The job is to produce new prose. This pass edits what exists and contributes no content of its own.
- The job is to derive a reusable voice profile from an author's body of published work — choosing which pieces count as source material, reconciling the ones that disagree with each other, and emitting a named profile for later work to load. That is a separate derivation job that runs upstream of this one. This pass reads at most one supplied sample to calibrate a single edit, and emits no profile of its own.
- The goal is to defeat an AI-detection tool. The pass targets how prose reads, and claims nothing about what any detector reports of the result. *(Authored: the source material makes no claim about detection either.)*
- The wording is fixed: quotations, transcripts, legal filings, published records, or any passage that has to be reproduced verbatim.

## Required inputs

- The text itself, or the path to the file holding it.
- The register and audience, if they are not obvious from the text: encyclopedic, technical reference, changelog, essay, marketing.
- Optional, and decisive when present: a writing sample by the same author, and the document's style guide.

## Workflow

1. **Calibrate to the author.** With a sample in hand, read it before the target text and note sentence lengths, vocabulary, paragraph openings, punctuation habits, recurring phrases, and transitions. Match those habits rather than only deleting tells: do not upgrade casual words, and do not regularize a deliberate quirk. A sample outranks every style rule in this skill, the dash gate included. If the author uses em dashes, keep them at roughly the sample's frequency. Without a sample, take the register from the text.
2. **Scan and triage.** Walk the scan list below, marking every hit with its pattern number. Run each hit past the guard before touching it, and drop from scope anything the guard protects or the document's own style guide requires. Only a cluster of surviving hits justifies a rewrite.
3. **Draft the rewrite.** Every claim in the original survives, but depth need not be uniform: compress the dull stretches, dwell where a person would, and merge or split paragraphs freely. Where preserving the information and mirroring the original structure pull apart, the information wins. Add nothing factual that is not in the source.
4. **Audit the draft in writing.** Answer two questions briefly and keep the answers: *What still marks this text as machine-written?* and *Does the rewrite state any fact, name, number, date, quotation, or citation absent from the source?* A fabrication is a defect even when it reads better than the vague original.
5. **Produce the final rewrite and run the gates.** Revise against the audit answers, then run all three gates below. A gate that fails sends the text back to step 3.

## Gates

- **Dash gate.** Search the final text for `—`, `–`, and a spaced double hyphen used as either. Any hit means the draft is not done. The one exception is a supplied writing sample that uses dashes, which overrides the gate per step 1.
- **Fabrication gate.** Every proper noun, number, date, quotation, and citation in the rewrite appears in the source or in material the requester supplied. One that appears nowhere is removed, not softened.
- **Claim gate.** List any claim in the source that no sentence of the rewrite carries. Each one is restored or reported; a claim lost to compression is a defect, not a stylistic choice.

The dash gate is an editorial default for this pass, not a claim that dashes indicate machine authorship. The guard below rates a dash on its own as near-worthless evidence, and both hold at once: the gate governs what this pass emits, the guard governs what it is safe to conclude about text it reads. *(Authored reconciliation. The source states the dash rule as an absolute and separately lists dashes among its weak indicators, without connecting the two.)*

## Decision points

- If the document is version-scoped by nature, including changelogs, release notes, and migration guides, pattern 30 does not apply: narrating change is what those documents are for.
- If the register is encyclopedic, technical, legal, or reference, plain and neutral prose is the correct human voice. Add no opinion, humor, or first person there. In essays, opinion, and personal writing the reverse holds: bloodless neutrality reads as generated, so let the author keep stance, uncertainty, mixed feelings, asides, and uneven rhythm. Never manufacture that voice by adding a factual claim.
- If a rewrite would be stronger with a specific detail the source lacks, ask for the detail or write the plain version without it. Trading a vague claim for a specific one is allowed only when the specific comes from the source or the requester.
- If the material is fiction, the fabrication gate does not apply, since invented detail is the work; the catalogue still does. *(Authored: the source states this exception for its no-invention rule only.)*
- If a pattern's legitimacy depends on house style, which covers heading case, boldface, emoji, quotation marks, and hyphenation, follow the document's own convention and leave conforming text alone. *(Authored: the source states these four rules absolutely.)*
- If a tell sits inside a quotation, a title, a proper name, or an example where the phrase is being discussed rather than used, leave it. This holds even in a text that is being rewritten around it.

## Scan list

Full entries, with words to watch and a before-and-after rewrite for each, are in `references/ai-tell-patterns.md`.

**Content**

1. Significance inflation: an ordinary fact promoted into a turning point.
2. Notability and coverage padding: outlet lists and follower counts instead of what was said.
3. Participle pseudo-analysis: an `-ing` tail bolted on to simulate depth.
4. Promotional language: brochure adjectives in neutral description.
5. Vague attribution: experts, observers, and industry reports with no name.
6. Formulaic challenges and future sections: a generic difficulty raised and immediately walked back.

**Language and grammar**

7. Overused AI vocabulary: the abstract, co-occurring register of *pivotal*, *tapestry*, *underscore*.
8. Copula avoidance: *serves as* and *features* standing in for *is* and *has*.
9. Negative parallelism and tailing negation: *not just X, it's Y*, and clipped *no guesswork* fragments.
10. Rule of three: a forced triple whose third member is empty.
11. Elegant variation: one referent renamed on every mention.
12. False ranges: *from X to Y* across items that share no scale.
13. Passive voice and subjectless fragments: the actor hidden or dropped.

**Style**

14. Em and en dashes: see the dash gate.
15. Boldface overuse: emphasis applied mechanically in running prose.
16. Inline-header vertical lists: a bold label whose sentence only restates it.
17. Title case in headings, against the document's own convention.
18. Emojis as decoration on headings and bullets.
19. Curly quotation marks, against the surrounding convention.

**Communication artifacts**

20. Chat correspondence pasted as content: *I hope this helps*, *let me know*.
21. Cutoff disclaimers and speculative gap-filling: writing about a missing source, then inventing filler to cover it.
22. Sycophantic tone: *Great question*, *You're absolutely right*.

**Filler, hedging, and rhetorical padding**

23. Filler phrases: *in order to*, *due to the fact that*, *at this point in time*.
24. Excessive hedging: three qualifiers stacked on one claim.
25. Generic positive conclusions: an upbeat send-off in place of a last fact.
26. Uniform hyphenation of compound pairs, including in predicate position.
27. Persuasive authority tropes: *the real question is*, *at its core*.
28. Signposting: announcing the content instead of stating it.
29. Fragmented headers: a one-line paragraph restating the heading above it.
30. Diff-anchored writing: describing a change rather than the thing.
31. Manufactured punchlines and staccato drama: a run of fragments engineered for momentum.
32. Aphorism formulas: *X is the currency of Y*, *X becomes a trap*.
33. Conversational rhetorical openers: *Honestly?*, *Here's the thing*, as standalone hooks.
34. Fake vulnerability arcs: a staged struggle that resolves into the lesson the piece was always going to make.
35. Engagement-farming closing questions: a question bolted on after the argument ends, to invite replies rather than to ask anything.

## False-positive guard

Applies to every hit before it is edited. Each item below is something competent human writing does. On its own, none of them is evidence of anything, and cutting them on sight is how a de-slopping pass damages good prose.

1. **Perfect grammar and consistent style.** Plenty of writers are professionals or have been edited. Polish is not authorship evidence.
2. **Mixed casual and formal register.** Typical of technical writers, young writers, and neurodivergent prose habits.
3. **Bland or robotic prose.** Machine text has specific tells; dryness without them is dry writing.
4. **Formal or academic vocabulary.** Pattern 7 names particular overused words. Do not flatten *ostensibly* or *constituent* for sounding brainy.
5. **A letter-style opening or sign-off.** Salutations predate chat assistants by centuries.
6. **Common transition words in isolation.** *Additionally*, *moreover*, and *consequently* count only when piled up. One *however* is nothing.
7. **Curly quotation marks alone.** Most word processors and publishing systems curl them by default.
8. **Dashes alone.** Editors and journalists use them heavily. They count only beside formulaic, sales-toned rhythm.
9. **One short emphatic sentence.** Clipped sentences land points. Flag the run, not the sentence.
10. **"Honestly" or "look" mid-sentence.** Ordinary in casual writing; only the standalone theatrical opener is pattern 33.
11. **Unsourced claims.** Most writing anywhere is unsourced. Missing citations prove nothing about authorship.
12. **Correct, complex formatting.** Templates and visual editors produce clean output with no model involved.
13. **Secondhand text.** A watched phrase inside a quotation, a title, a proper name, or an example under discussion is being mentioned, not used.

The evidence is the cluster, never the item. One dash means nothing; a dash plus a forced triple plus *vibrant tapestry* plus a Conclusion section that concludes nothing is a confession.

## Signs the text is already human

Each of these argues for leaving a passage alone, and over-editing destroys exactly what makes it read as a person.

- **Specific, unusual, hard-to-fabricate detail.** A real address, an odd quote, "the lawyer who used to work upstairs from my dentist". Models round specifics off; people hoard them.
- **Mixed feelings and unresolved tension.** "I think this is mostly right and it still bothers me, and I cannot say why." Generated takes come out clean.
- **Dated, era-bound references.** Slang, memes, and in-jokes that pin to one year and one subculture.
- **First-person editorial choices the writer can defend.** An explicable cut or word choice is a strong signal.
- **Variety in sentence length.** Real writing alternates short and long; generated writing settles into an even mid-length cadence.
- **Genuine asides, parentheticals, and self-corrections.** "(I keep wanting to write *almost* here, but it really was certain.)"
- **Text that predates widely available chat assistants.** The first mass-market one launched at the end of November 2022. A time-sensitive fact, and it settles authorship only, never quality.

## Examples

**A hit that gets edited.** Patterns 3, 4, and 7 cluster in one sentence.

- Before: "At the heart of the platform, the new gateway boasts a vibrant plugin ecosystem, showcasing the team's commitment to extensibility."
- After: "The new gateway supports third-party plugins."

**A hit that gets left alone.** Guard items 8 and 9 protect it.

- Text: "The migration took a weekend — most of it waiting on backfills. It worked."
- Action: no edit. One dash and one short sentence, in prose with a specific, unglamorous detail and no other tells, is a person writing. Editing it out yields text that reads more generated, not less.

## Output contract

Three delivery modes. All three run the full loop and all three gates; they differ only in what leaves the pass.

- **Text supplied in the request.** Deliver the draft rewrite, the two audit answers, the final rewrite, and a short list of what changed and which hits the guard protected.
- **A file to edit in place.** Run the loop internally and write only the final rewrite into the file, leaving code blocks, frontmatter, data, and link targets untouched. Report a summary rather than pasting the rewritten text back.
- **Embedded in a larger job**, such as a pull-request body, a commit message, or one section of a document. Run the loop internally and emit only the final text. No draft, no audit answers, no summary.

## Common pitfalls

- Rewriting to the shape of the original instead of to its claims, which keeps the paragraph count and loses the point.
- Replacing a vague sentence with a specific one by supplying the specifics, which is the highest-frequency failure of this pass and the reason the fabrication gate exists.
- Editing a protected hit because it appears in the catalogue, without checking whether the guard or the document's style guide covers it.
- Scrubbing every tell and adding no voice, in text whose register calls for one.
- Treating the scan list as the deliverable and reporting pattern numbers instead of rewritten prose.

## References

- `references/ai-tell-patterns.md`: all 35 patterns with words to watch, a before-and-after rewrite each, and the register notes for the patterns that are legitimate in some documents.

## Provenance

The taxonomy is adapted from Wikipedia's advice page "Signs of AI writing", maintained under WikiProject AI Cleanup (`en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing`, verified against the live page 2026-08-17), and reached this file through an MIT-licensed community adaptation of that page. Examples here are written for this file rather than reproduced. Patterns 34 and 35 do not come from that page: they restate two entries from a long-form drafting ban-list in this library's intake material, in this file's own words.

No efficacy figure is carried, because the source states none: nothing here quantifies how much of a text this pass changes, and nothing claims a particular result from any detection tool. Rules marked *(Authored)* are this skill's, not the source's.
