# AI-tell pattern catalogue

Thirty-five named patterns, each with what to watch for and a concrete replacement. Grouped into five families; numbering is stable so the main file's scan list and this catalogue stay in step.

Two rules govern every entry.

- **The After column is illustrative, not a template.** In a real edit the replacement text comes from the source document. Never import a detail from an example here, and never invent one to make a rewritten sentence land better.
- **Run every hit past the false-positive guard in `SKILL.md` before editing it.** Several patterns below are legitimate in some registers; those carry a *Register* note. Where a note says the rule depends on the document's own style, confirm that style before changing anything.

## Content

### 1. Significance inflation

**Watch:** stands as, serves as, is a testament to, played a pivotal/crucial/key role, marked a turning point, underscores the importance of, reflects a broader, part of a broader movement, evolving landscape, left an indelible mark, deeply rooted.

Ordinary facts get promoted into milestones, and arbitrary details get attached to a sweeping trend the source never claimed.

- **Before:** The library's 2019 rewrite marked a pivotal moment in the project's evolution, reflecting a broader industry shift toward type safety.
- **After:** The library was rewritten in 2019.

*Register:* a sourced causal claim is not this pattern. The tell is the unsourced upgrade, where the significance is asserted rather than attributed.

### 2. Notability and coverage padding

**Watch:** has been featured in, independent coverage, national/regional media outlets, written by a leading expert, maintains an active social media presence.

Coverage gets listed instead of used: four outlet names and a follower count in place of one thing somebody actually said.

- **Before:** Her research on grid failures has been covered by The Guardian, Wired, El Pais, and Nikkei, and she maintains an active presence across several platforms.
- **After:** Wired covered her study of grid failures.

Keep the one citation the source gives real context for and drop the rest of the list. Do not invent the context to make the trimmed sentence read better.

### 3. Participle pseudo-analysis

**Watch:** trailing clauses opening with highlighting, underscoring, emphasizing, ensuring, reflecting, symbolizing, contributing to, fostering, cultivating, showcasing, encompassing.

A present-participle tail is bolted onto a finished sentence to simulate depth. It almost always restates the sentence or asserts an unsupported consequence.

- **Before:** The API returns paginated results, ensuring predictable memory use and reflecting the team's commitment to reliability.
- **After:** The API returns paginated results, so a client never loads a whole collection at once.

### 4. Promotional language

**Watch:** boasts, vibrant, rich (figurative), profound, nestled, in the heart of, renowned, breathtaking, stunning, must-visit, groundbreaking (figurative), commitment to, natural beauty, enhancing its.

Neutral description slides into brochure copy, most reliably on places, institutions, and anything framed as heritage or culture.

- **Before:** Nestled in the heart of the old town, the museum boasts a rich collection and a breathtaking glass atrium.
- **After:** The museum is in the old town and has a glass atrium.

### 5. Vague attribution and weasel words

**Watch:** industry reports suggest, observers have noted, experts argue, some critics say, it is widely regarded, several sources.

An opinion is attributed to an authority with no name, which makes an unsupported claim look sourced.

- **Before:** Industry reports suggest observability budgets are under pressure, and experts argue consolidation is inevitable.
- **After:** Cut the sentence. If a real source exists, name it and state what it actually found.

Never invent a source to make a sentence sound attributed. An unsupported claim gets cut, not decorated.

### 6. Formulaic challenges and future sections

**Watch:** faces several challenges, Despite these challenges, Challenges and Legacy, Future Outlook, continues to thrive.

A section appears because the template calls for one, then concedes a generic difficulty and immediately walks it back.

- **Before:** Despite its rapid growth, the team faces challenges typical of scaling organizations, including communication overhead and technical debt. Despite these challenges, the team continues to thrive.
- **After:** Communication overhead and technical debt have grown with the team.

The specifics worth having here, when the overhead started or what was done about it, come from the source or the requester, never from the rewrite.

## Language and grammar

### 7. Overused AI vocabulary

**Watch:** additionally, align with, crucial, delve, emphasize, enduring, enhance, foster, garner, highlight (verb), interplay, intricate, key (adjective), landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, valuable, vibrant.

These words appear far more often in post-2023 text than before it, and they cluster: finding one usually means finding three in the same paragraph.

- **Before:** Additionally, the framework enhances developer experience by fostering a vibrant plugin ecosystem, showcasing the enduring value of open standards.
- **After:** The framework also has a plugin ecosystem.

*Register:* each of these is an ordinary word in its literal sense, and a crucial bolt or a woven tapestry is not a tell. The pattern is the abstract or figurative use, in a cluster.

### 8. Copula avoidance

**Watch:** serves as, stands as, represents, marks, features, boasts, offers, in place of plain *is* or *has*.

Simple statements of identity get replaced by heavier verbs that add nothing.

- **Before:** The staging cluster serves as the integration environment and features three worker nodes.
- **After:** The staging cluster is the integration environment. It has three worker nodes.

### 9. Negative parallelism and tailing negation

**Watch:** not only... but also, it's not just X, it's Y, it's not merely, plus clipped negative fragments tacked to a sentence end.

- **Before:** It's not just a linter, it's a full type checker. Not only does it catch errors, but it also documents intent.
- **After:** It is a type checker rather than only a linter. It catches errors and records intent in the signature.
- **Before (tailing negation):** The defaults come from the lockfile, no guesswork.
- **After:** The defaults come from the lockfile, so nothing has to be guessed.

### 10. Rule of three

Ideas get forced into triples to sound comprehensive. The third item is usually the vaguest, because it exists to fill the slot.

- **Before:** The release improves speed, reliability, and developer experience. Users get faster builds, clearer errors, and better documentation.
- **After:** The release makes builds faster and error messages clearer.

*Register:* three items are correct when there are three things. Cut the triple only when one member is empty or duplicated. *(Authored register note.)*

### 11. Elegant variation

The same referent is renamed on every mention to avoid repetition, until the reader cannot tell whether one thing or four is being discussed.

- **Before:** The scheduler assigns jobs. The dispatcher then places the workload. The coordinator reports the outcome.
- **After:** The scheduler assigns each job and reports the outcome.

*Register:* confirm the synonyms name the same thing before merging them. In a system with a genuine scheduler and a genuine dispatcher, this is precision, not variation. *(Authored register note.)*

### 12. False ranges

**Watch:** from X to Y, where X and Y do not sit on any shared scale.

- **Before:** The audit covered everything from stale IAM roles to the philosophy of least privilege.
- **After:** The audit covered stale IAM roles and policies that granted more access than the role needed.

### 13. Passive voice and subjectless fragments

**Watch:** headless fragments such as *No configuration file needed*, and agentless passives that hide who acts.

- **Before:** No migration file needed. The old rows are archived automatically.
- **After:** This change needs no migration file. The job archives the old rows.

*Register:* rewrite only where the active form is clearer. The passive is the correct choice when the actor is unknown, irrelevant, or deliberately backgrounded, which covers incident write-ups, standards text, and method sections. *(Register note authored for this skill; the source states the "when active is clearer" condition without naming the registers.)*

## Style

### 14. Em dashes and en dashes

The dash gate in `SKILL.md` governs this pattern: the final rewrite carries no em dash, en dash, or spaced double hyphen used as one, unless a supplied writing sample overrides it.

Replace each one, in this order of preference: a period, starting a new sentence; a comma, for a tight aside; a colon, introducing an explanation; parentheses, for a true aside; or a restructured sentence.

- **Before:** The policy — announced without warning — affects every contractor. The rollout was delayed -- again -- by procurement, and the 2024–2025 backlog grew.
- **After:** The policy, announced without warning, affects every contractor. Procurement delayed the rollout again, and the 2024 to 2025 backlog grew.

The characters in that Before line are the ones to search for: the em dash, the en dash, and a spaced double hyphen standing in for either.

### 15. Boldface overuse

Phrases are bolded mechanically inside running prose until the emphasis carries no information.

- **Before:** It combines **OKRs**, **KPIs**, and **quarterly planning** into one **operating cadence**.
- **After:** It combines OKRs, KPIs, and quarterly planning into one operating cadence.

*Register:* reference documentation legitimately bolds parameter names, literal UI labels, and defined terms. The tell is bolding for emphasis in prose. *(Authored register note.)*

### 16. Inline-header vertical lists

List items open with a bold label and a colon, then restate the label as a sentence.

- **Before:**
  - **Performance:** Performance has been improved with a new cache.
  - **Security:** Security has been strengthened with encryption at rest.
- **After:** The update adds a cache and encrypts stored data.

*Register:* the shape is correct for glossaries, option references, and parameter tables, where the label is a term being defined. The tell is a label whose body only repeats it. *(Authored register note.)*

### 17. Title case in headings

- **Before:** `## Strategic Negotiations And Global Partnerships`
- **After:** `## Strategic negotiations and global partnerships`

*Register:* title case is house style for many publications and is not a tell there. Change it when the document's other headings are sentence case, or when its style guide asks for sentence case. Check the document's own convention first. *(Authored register note; the source states the rule unconditionally.)*

### 18. Emojis

Headings and bullets get decorated with emoji that carry no meaning.

- **Before:** 🚀 **Launch:** ships in Q3 / 💡 **Insight:** users prefer fewer options
- **After:** The product ships in Q3. Users prefer fewer options.

*Register:* some projects have a fixed emoji convention in changelogs or commit prefixes. Follow the document's convention; the tell is decoration on every item. *(Authored register note.)*

### 19. Curly quotation marks

Curly quotes appear where the surrounding context uses straight ones.

- **Before:** He said “the build is green” and closed the ticket.
- **After:** He said "the build is green" and closed the ticket.

*Register:* word processors, note apps, and most publishing systems curl quotes by default, so this is the weakest signal in the catalogue and counts only alongside other tells. In typeset prose the curly form is correct. Normalize only toward the document's existing convention. *(The last sentence is authored; the source states the rule absolutely.)*

## Communication artifacts

### 20. Chat correspondence pasted as content

**Watch:** I hope this helps, Certainly, Of course, You're absolutely right, Would you like me to, Want me to expand, Should I continue, let me know, here is a.

- **Before:** Here's an overview of the retry policy. I hope this helps! Let me know if you'd like me to expand any section.
- **After:** Delete the framing sentences and keep the content. "Here's an overview of the retry policy" becomes the heading `## Retry policy`.

### 21. Cutoff disclaimers and speculative gap-filling

**Watch:** as of my last update, up to my training data, while specific details are limited, based on available information, not publicly available, maintains a low profile, keeps personal details private, likely began, it is believed that.

Two related tells. A model either leaves a hard knowledge-cutoff disclaimer in the text, or, having found no source, writes a paragraph about finding no source and then fills the gap with plausible invention. The invention lands on the same stock phrases every time.

- **Before (disclaimer):** While specific details about the outage are not extensively documented in available sources, it appears to have lasted several hours.
- **After:** The outage duration is not documented in the available sources. Or cut the sentence.
- **Before (gap-fill):** Little is publicly available about her early career, suggesting she keeps a low profile. She likely began in academia before moving into industry.
- **After:** Her early career is not documented in the available sources. Or omit the section.

State what is not known, or cut the sentence. Do not dress a guess as a fact.

### 22. Sycophantic tone

**Watch:** Great question, You're absolutely right, That's an excellent point, I'd be happy to.

- **Before:** Great question! You're absolutely right that caching is tricky here.
- **After:** Caching is the hard part here.

## Filler, hedging, and rhetorical padding

### 23. Filler phrases

| Before | After |
| --- | --- |
| in order to achieve this goal | to achieve this |
| due to the fact that | because |
| at this point in time | now |
| in the event that you need help | if you need help |
| has the ability to process | can process |
| it is important to note that the data shows | the data shows |
| for the purpose of testing | for testing |
| a large number of users | many users |

### 24. Excessive hedging

- **Before:** It could potentially be argued that the migration might introduce some degree of risk.
- **After:** The migration introduces risk.

*Register:* one accurate hedge is precision, not padding. Keep *may* where the uncertainty is real; the tell is stacking qualifiers on one claim. *(Authored register note.)*

### 25. Generic positive conclusions

**Watch:** the future looks bright, exciting times ahead, a major step in the right direction, continues its journey toward.

- **Before:** The future looks bright for the platform, and exciting times lie ahead as the team continues its journey toward excellence.
- **After:** Cut the paragraph and end on the last concrete fact. If the source states real plans, state those instead.

### 26. Uniform hyphenation of compound pairs

**Watch:** third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end.

Machine text hyphenates these identically in every position. People hyphenate the compound when it sits before the noun and often drop the hyphen when it follows.

- **Before:** The cross-functional team shipped a data-driven report. The team is cross-functional and the report is data-driven.
- **After:** The cross-functional team shipped a data-driven report. The team is cross functional and the report is data driven.

*Register:* some style guides hyphenate in both positions, and a few compounds are permanently hyphenated by convention. Where the document follows a style guide, that guide wins. *(Authored register note.)*

### 27. Persuasive authority tropes

**Watch:** the real question is, at its core, in reality, what really matters, fundamentally, the deeper issue, the heart of the matter.

The sentence promises to cut through noise and then restates an ordinary point with ceremony.

- **Before:** The real question is whether the team can adapt. At its core, what really matters is organizational readiness.
- **After:** The question is whether the team can adapt, which depends on whether the organization is ready.

### 28. Signposting and announcements

**Watch:** let's dive in, let's explore, let's break this down, here's what you need to know, now let's look at, without further ado.

- **Before:** Let's dive into how caching works here. Here's what you need to know. The CDN holds responses for five minutes, and the client memoizes repeated requests.
- **After:** The CDN holds responses for five minutes, and the client memoizes repeated requests.

Delete the announcement and keep the content it was standing in front of. Where a signpost has nothing behind it, the section itself is the problem.

### 29. Fragmented headers

A heading is followed by a one-line paragraph that restates it before the real content starts.

Before:

```
## Performance

Speed matters.

When users hit a slow page, they leave.
```

After:

```
## Performance

When users hit a slow page, they leave.
```

### 30. Diff-anchored writing

Documentation or comments narrate a change instead of describing the thing as it is, so the text only makes sense to someone who saw the previous version.

- **Before:** This helper was added to replace the old nested loop, which was O(n squared).
- **After:** This helper avoids the O(n squared) cost of comparing every pair.

*Register:* documents that are version-scoped by definition, including changelogs, release notes, and migration guides, are supposed to narrate change. This pattern does not apply to them.

### 31. Manufactured punchlines and staccato drama

Every sentence is written to land like a closing line, and short fragments stack up to manufacture momentum.

- **Before:** Then the new scheduler landed. No heuristics. No tuning knobs. No excuses. The old playbook was dead.
- **After:** The new scheduler dropped the heuristics and the tuning knobs, which made most of the old playbook irrelevant.

*Register:* a single short sentence for emphasis is ordinary writing. Flag the run, not the sentence.

### 32. Aphorism formulas

**Watch:** X is the Y of Z, X becomes a trap, not a tool but a mirror, the language of, the currency of, the architecture of.

An ordinary claim is reshaped into a portable-sounding maxim that loses the precision it started with. Replace the formula with the concrete claim underneath it.

- **Before:** Latency is the currency of trust. Observability becomes a trap when teams instrument everything.
- **After:** Users lose confidence in a service that responds slowly. Teams that instrument everything end up paying to store data nobody reads.

### 33. Conversational rhetorical openers

**Watch:** Honestly?, Look, Here's the thing, The thing is, Let's be honest, Real talk, used as standalone hooks.

A fake-candid pause manufactures intimacy before an ordinary point. The tell is the theatrical setup and reveal.

- **Before:** Is it worth migrating? Honestly? It depends on how much of the API you use.
- **After:** Whether migrating is worth it depends on how much of the API you use.

*Register:* the same words mid-sentence are ordinary in casual writing. Only the standalone opener is the pattern.

### 34. Fake vulnerability arcs

**Watch:** I'll be honest, I used to think, I learned this the hard way, we failed at this for months, my biggest mistake was, and then it clicked.

A confession of struggle is staged in front of the real claim so the claim arrives sounding earned. The tell is that the failure is generic, costs the writer nothing anyone can check, and resolves into exactly the lesson the piece was always going to make.

- **Before:** I'll be honest: for months we shipped without tests and paid for it. That failure taught me what I now believe deeply. Testing is not optional.
- **After:** We shipped without tests for two quarters.

Keep whatever cost the source actually records, and nothing more. Where it records none, the arc goes and only the claim it was propping up survives; supplying the missing specifics is what the fabrication gate exists to stop.

*Register:* a real failure with a cost the writer can name is not this pattern — it is the hard-to-fabricate detail the guard protects. The tell is an arc with no particulars in it.

### 35. Engagement-farming closing questions

**Watch:** What's your take?, Am I wrong?, What would you add?, Curious what others think, Let me know below.

A question is bolted on after the argument has finished, addressed to nobody in particular, and answering it would change nothing in the text above it. It solicits replies rather than asking anything.

- **Before:** Caching halved the tail latency on that endpoint. What's been your experience with caching? Curious what others think.
- **After:** Caching halved the tail latency on that endpoint.

*Register:* a question the text has genuinely left open — one the author names and cannot answer — is content. Keep it, and keep it where the uncertainty actually is rather than bolted to the end. *(Authored register note.)*

## Provenance

The taxonomy is adapted from Wikipedia's advice page "Signs of AI writing", maintained under WikiProject AI Cleanup (`en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing`, verified 2026-08-17), and reached this file through an MIT-licensed community adaptation of that page. Every example above is written for this file rather than reproduced from either source. Patterns 26, 27, 28, 30, 31, 32, and 33 extend the Wikipedia families into software and product prose; every note marked *(Authored)* is not in either source. Patterns 34 and 35 come from neither: they restate two entries of a long-form drafting ban-list held in this library's intake material, and their examples and register notes are written here.
