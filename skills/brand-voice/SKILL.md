---
name: brand-voice
description: "Derives a reusable writing-voice profile from an author's or brand's real published material — posts, essays, memos, outbound that worked, product copy — and emits it as a named block later drafting can load instead of re-deriving style. Use when written output has to sound like a specific person or brand and real samples exist to derive it from."
metadata:
  category: marketing
---
# Brand Voice

Provides the procedure for turning real writing into an operational voice profile: which sources to derive from and in what order, what to observe in them, what to do when the sources disagree, and the fixed shape the profile is emitted in so it can be reused rather than re-derived per task.

The product is a description of habits that is specific enough to draft against. "Professional but approachable" is not one. A profile earns its place only if two different writers could produce copy from it that sounds like the same person.

## Use this skill when

- Written output has to sound like a specific author or brand, and material that author already published is available.
- A team needs one shared style reference so that everything it ships reads as one voice.
- The same voice will be needed repeatedly, and re-deriving it from scratch each time is the waste being removed.
- Material written for different contexts — public launch copy and internal memos, say — appears to be in two different voices, and the split needs settling before anything new is written.

## Do not use this skill when

*(This section is authored. The source procedure ships no stand-down.)*

- A profile has already been derived in this session. Reuse it. A second derivation from the same sources produces a second, slightly different answer and no reason to prefer either.
- The job is editing prose that already exists so it reads less machine-generated. That is an editing pass against a draft, and calibrating to a sample is one step inside it, not a separate deliverable.
- No real source material exists. A profile derived from nothing is invention presented as observation, and everything downstream inherits the fiction. Say the samples are missing and ask for them.
- The request is to draft a specific piece and no reusable artifact is wanted. Read the samples and write the piece.

## Required inputs

- The source material itself, or where to find it. Nothing else substitutes.
- Who the voice belongs to: one person, a brand, or a person writing as a brand.
- Which channels the profile will be used for, since the profile records how the voice changes across them.

## Source selection

Derive from the strongest real material available, in this order:

1. The author's own original posts and threads.
2. Articles, essays, memos, launch notes, or newsletters.
3. Real outbound — emails or messages that got the response they were sent for.
4. Product docs, changelogs, and site copy.

Rules that decide the set:

- **Prefer recent material**, unless the requester states that older writing is the canonical voice.
- **Never use generic platform exemplars** — a "great LinkedIn post" template, a viral thread teardown, a model's idea of how a founder writes. Those describe a format's conventions, not this author's habits, and a profile built on them reproduces the average of the platform, which is the exact output the profile exists to prevent.
- **Separate a public voice from a working voice** when the set clearly splits, rather than blending them.
- **Gather enough that each habit appears in more than one sample.** A single piece shows a mood; a habit is what repeats. Stop adding samples once new ones stop changing the profile. *(Authored: the source names a fixed sample count with no justification. The observable condition replaces it.)*

## Workflow

1. **Assemble the source set** by the priority above. Record what is in it — the profile carries its own sources, so a later reader can see what it was derived from and what it never saw.
2. **Read for habits, not for content.** Go through the samples looking only at how they are written, per the observation list below. Note the concrete instance behind each observation; an observation with no instance behind it is a guess.
3. **Resolve conflicts explicitly.** Where the set disagrees, call out the split instead of averaging it into mush — record both patterns and the condition that selects between them. If no condition is visible, say the split is unexplained rather than picking the more frequent one.
4. **Emit the profile** in the fixed shape below, as a named block that later work can load whole.
5. **Confirm the profile before it is used.** Show it to the requester and ask what is wrong with it. Corrections are cheap here and expensive in every draft written from it.

## What to observe

Each maps to a field in the emitted profile:

| Observation | What to record |
| --- | --- |
| Rhythm | Sentence lengths, pacing, whether fragments appear and where |
| Compression | Dense or explanatory; how much context is assumed rather than stated |
| Capitalization | Conventional, situational, or deliberately broken — and when |
| Parentheticals | What they are used for: qualification, narrowing, aside, joke — and where they never appear |
| Question use | Frequent or rare; genuine, rhetorical, or absent |
| Claim style | How sharply claims are made, and what backs them — numbers, mechanisms, receipts, or nothing |
| Preferred moves | Concrete constructions this author reaches for, quoted from the set |
| Banned moves | Patterns this author demonstrably never uses |
| Calls to action | How, when, and whether the writing closes with an ask |

**Every banned move must be observable in the source set or explicitly requested by the requester.** A generic list of disliked phrases is not a finding about this author, and importing one turns the profile into someone else's taste.

## Output contract

A single named block, structured, and short enough to carry in context for later drafting:

```text
VOICE PROFILE
=============
Author:
Goal:
Confidence:          (what the source set supports, and where it is thin)

Source Set
- what was read, and roughly when it was written

Rhythm
Compression
Capitalization
Parentheticals
Question Use
Claim Style
Preferred Moves
Banned Moves
CTA Rules

Channel Notes
- per channel the profile will be used for: what changes, and what does not

Unresolved Splits
- any conflict in the source set, both patterns, and what selects between them
```

Rules for the block:

- Short bullets under each field, not paragraphs. The point is operational reuse, not literary criticism.
- Every field is source-backed. A field the samples do not support is marked thin rather than filled in from expectation.
- The profile is a session artifact by default. Save it to a durable location only when asked, and do not commit a personal voice fingerprint into a shared repository unless the request is explicit about that.

## Examples

**A field that works, against one that does not.**

- Not usable: `Rhythm: professional but approachable, fairly concise.` Nothing in it can be checked against a draft.
- Usable: `Rhythm: two or three short declaratives, then one long sentence carrying the qualification. Fragments only as a closing beat, roughly once per post — "Which is the whole point."`

**A conflicting source set.**

- Wrong: launch posts are punchy and capitalized conventionally; internal memos are lowercase and hedged. The profile averages this into "moderately informal, mixed capitalization" — which describes neither, and every draft written from it sounds slightly off in both places.
- Right: record both. `Capitalization: conventional in anything public-facing (all 9 launch posts). Lowercase throughout in internal memos (6 of 6). Split is by audience, not by date.` Later drafting picks the branch its channel calls for.

**A source set that does not support a profile.**

- The requester supplies three sentences from a bio page and asks for a full profile. Report that the set supports capitalization and little else, and ask for posts, memos, or sent emails. A profile filled out past its evidence is invention wearing the shape of a finding.

## Common pitfalls

- Deriving from what the author *should* sound like — their category, their role, their platform — instead of from what they wrote.
- Averaging a split source set into a single blurred description.
- Writing fields that restate the samples' subject matter rather than their construction.
- Filling a thin field to make the block look complete.
- Re-deriving the profile on the next task instead of loading the one already produced.
- Carrying an inherited list of banned phrases the author's own writing never demonstrates.

## Provenance

The source-selection order, the conflict rule, and the profile's field set come from the candidate procedure this skill was rewritten from. Its shipped defaults for one named individual's voice were dropped: a fingerprint for a specific person is not a default for anyone else, and it made the file look populated where it was actually empty. Rules marked *(Authored)* are this skill's, not the source's.
