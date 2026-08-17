# The review surface: what the page itself must contain

Companion to `SKILL.md`. That file covers the handoff — transport, protocol, state, lifecycle. This file covers the page the human actually looks at, and the artifact split that decides what goes on it.

Provenance: generalized from a single implementation, a design-mockup comparison board, plus its two design notes. The layout rules below were written for images; they are stated here in terms of "candidates" because nothing in them depends on what a candidate is. Rules marked *(authored)* are not in the source.

## Split the artifact by consumer

When one deliverable must be *judged* by a human and *built from* by an agent, that is two artifacts, not one.

- A rendering for the human to judge. Faithful, immediate, comparable at a glance.
- A structured form for the agent to build from. The source's rationale: raster images are opaque to an agent — no DOM, no states, nothing diffable — while structured markup "preserves a bridge back to code".
- The sequence is fixed and the human's approval gates it: produce renderings → human picks one → *then* produce the structured artifact matching the approved direction → implement from the structured artifact, never from the rendering.
- Producing both up front wastes the generation on candidates that were never chosen, and implementing from the rendering discards the approved structure.

## Layout

- One candidate per full-width row, scrolled vertically. Full viewport width per candidate preserves fidelity; a grid that shrinks every candidate to a thumbnail defeats the reason for leaving the chat in the first place.
- Per candidate: an exclusive pick control mutually exclusive across all candidates, a rating, a free-text note, and a "more like this one" action that seeds the next round from that candidate.
- One collapsed overall field for direction-level comment, expanding on focus. It is subordinate to the per-candidate inputs and must not compete with them for attention.
- A visually separated "another round" bar carrying preset directions — broaden, constrain to existing conventions, free text — on a distinct background, clearly not part of any candidate's row.
- Exactly one primary call to action.
- A declared result schema of fixed shape. The page constructs that object and nothing else, which is also what keeps the request body small enough that the missing body-size cap (`SKILL.md`, checklist item 11) stays theoretical.

## Required states

All four are part of the contract, not polish. A state the page cannot render is a state in which the human is stuck.

| State | What the page shows |
| --- | --- |
| Loading | A skeleton per candidate card, with every input disabled until content is ready. |
| Partial failure | The candidates that succeeded, rendered normally, plus an error card with a per-candidate retry for each one that did not. Never fail the whole page because one candidate failed. |
| Post-submit | The read-only record described in `SKILL.md`, checklist item 1. |
| Regenerating | A transition state: reset scroll position and clear the previous round's inputs, so the new round is not judged against stale ratings. |

## Accessibility and responsiveness

Part of the contract, for the same reason as the states: a control the human cannot reach is a field the agent will read as empty.

- Ratings are keyboard-navigable.
- Every text area is labeled with the candidate it belongs to — a note attributed to the wrong candidate is worse than a missing note, because the agent acts on it.
- Focus rings are visible.
- No horizontal scroll at narrow widths.

## Consent

- Ask once, before any content leaves the machine, and persist the answer so the question is not re-asked every round.
- State plainly what is sent and what is not. The whole point of a local page is that the artifact stays local; anything that leaves crosses a boundary the human has not otherwise agreed to.
- *(Authored)* The consent question belongs before generation, not before submission: by the time the page exists, the content has usually already been sent to whatever produced the candidates.
