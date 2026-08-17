# Decision brief format

The shape a question takes so a human can answer it in seconds, an automatic path can act on it safely, and a reader can audit it later. Every element below is drawn from a shipped workflow definition, not from a proposal.

## Elements

| Element | Rule |
| --- | --- |
| Label | A stable identifier for this decision, unique within the run, reusable to refer back to it. |
| Title | One line, plain language. |
| Grounding | One sentence naming the work the decision belongs to — project, branch, task — so the question is answerable without scrollback. |
| What is being decided | Two to four sentences a non-specialist can follow. Names the stakes, not the call sites. Function names, file paths, and internal jargon do not belong here. |
| What breaks if this is wrong | An explicit line. Not implied by the pros and cons. |
| Options | Each with pros *and* cons. |
| Coverage score | A per-option score, included only when the options differ in how much of the problem they cover. When they differ in *kind* instead, an explicit note saying so replaces the score. The score is never silently dropped. |
| Effort | Where an option carries effort, state it on both scales — human-team time and agent time (for example: "human: ~2 days / agent: ~15 min"). One scale alone reads as commensurate when it is not. |
| Recommendation | A line of the form "Recommendation: <choice> because <reason>", always present, plus exactly one marker on the recommended option itself. |
| Net | A closing line stating the actual tradeoff being made. |

## Why the recommendation marker is load-bearing

An automatic path that suppresses a question reads the marker to know what to choose. Two markers, or none that parses, forces the question to be asked instead. This has two consequences worth stating separately:

- A question with no unambiguous recommendation cannot be auto-decided, ever — which is the correct outcome, not a limitation.
- **Neutral posture is explicit, not implicit.** When there is genuinely no preference between the options, say so *and still mark a default*. Omitting the marker to signal neutrality reads to every automatic path as an unparseable question.

## Pro and con floors

The source sets minimums — at least two pros, at least one con, and a minimum length per bullet — to stop the con from being pro-forma. **These are chosen defaults with no stated justification in the source; treat the intent as binding and the exact figures as arbitrary.** The intent: a con short enough to be a formality is not a con, and an option with no stated downside has not been analyzed. A hard-stop confirmation for a one-way door is exempt — it is not offering a tradeoff.

## Phrasing

- **Frame in outcome terms**, not implementation terms: "what breaks for the people using this if X" rather than "should the adapter own the retry".
- **Close each decision with its user impact.**

## Self-check before emitting

Run against the drafted question; any failure is a rewrite, not a caveat.

- Does the label exist, and is it unique in this run?
- Could someone outside the codebase say what is being decided, from the explanation alone?
- Is the "what breaks if this is wrong" line present as its own line?
- Does every option carry at least one real con?
- Is there exactly one recommendation marker, and does a recommendation line name the same option?
- Where options carry effort, are both scales present?
- Where options differ in coverage, is the score present — or, where they differ in kind, the note that replaces it?
- Does the option set match the real decision space, with nothing dropped to fit the cap?
- In a split chain: does each option carry its own stable identifier, and does any option that depends on another say so in its own explanation?

*This check runs at the instruction layer and is therefore the weakest enforcement in the protocol — every stronger guarantee sits outside the agent's own diligence. Its value is that every item on it is mechanically checkable, so it can be promoted to an enforced check later.*

## Prose channel

When the question tool is absent or the session falls back to prose, the brief carries the same content, laid out differently:

- One paragraph per choice, not bullets — prose reads worse as a list.
- The same triad survives the transport: the plain-language explanation, the per-option comparison including coverage, and the recommendation with its marker.
- Close with an instruction to reply with a letter, then **stop**. Do not continue working past the question.

For a one-way door on this channel, the weaker gate is compensated explicitly: state plainly what is irreversible, require the exact option typed back, and treat any vague, partial, or ambiguous reply — "ok", "sure", "go ahead" — as not-yet-confirmed.

## Continuation

- Each brief keeps its stable label for the life of the run.
- A bare letter maps to the single most recent **unanswered** brief.
- With more than one brief open — any split chain — do not guess which one a bare letter answers. Ask which.
