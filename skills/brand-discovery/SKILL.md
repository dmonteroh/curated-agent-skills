---
name: brand-discovery
description: "Runs a brand identity interview across several sessions: one question per turn, captured to disk after every section, and checkpointed so a later session resumes where the last one stopped. Interviews multiple stakeholders separately and reconciles them afterwards. Produces a written identity reference that designers, writers, and outside collaborators can be briefed from. Use when a brand's identity is being created, repositioned, or made explicit across multiple sessions or stakeholders."
metadata:
  category: marketing
---
# Brand Discovery

Provides the elicitation procedure for getting a brand's identity out of the people who hold it, and the state discipline that lets the process survive being interrupted. The failure it exists to prevent is ordinary: an hour of good conversation ends, nothing was written down in the participant's own words, no record says where the thread stopped, and the next session restarts from adjectives.

Identity work sits upstream of product and interface work. This procedure establishes what a brand is, who it is for, and how it speaks — not how a built product should behave for a user.

## Use this skill when

- A brand is being created, repositioned, or made explicit so that collaborators can be briefed from one document instead of from a founder's memory.
- The conversation will span several sittings across days or weeks.
- Several founders or stakeholders each need their own interview before their answers are compared.
- Brand knowledge exists but is implicit, scattered across decks and chats, or dependent on one person being in the room.
- The requester wants a repeatable method with a written artifact, not an ad hoc conversation.

## Do not use this skill when

- The goal is a specification for how a product should behave for its users — task flows, screens, friction, desired changes. That is discovery about interacting with a built thing, it runs after identity rather than instead of it, and its questions and its output are different.
- The requester wants one short brand conversation and no artifact. The checkpointing and file discipline here cost more than a single chat returns.
- The output needed is a visual direction for one artifact — a landing page, a logo, a colour and type direction. A short brand-feel interview attached to that artifact owns that job and stops at what the artifact needs.
- A brand direction has already been approved. Apply it. Re-running discovery over an approved direction produces a second, conflicting answer and no way to choose between them.
- The question is about the market rather than the brand: competitor scoping, sizing, pricing, or channel selection.

## Session start protocol

On every activation, before asking a single interview question:

1. **Check for prior progress.** Look for the checkpoint file and the section files in the agreed output directory. If neither exists this is a fresh start: confirm the brand name, the participants, and the output directory, then open the first section.
2. **Read the open section file** if the checkpoint names one, including everything already captured in it. A question whose answer is already on disk is the clearest signal that no state was read.
3. **Report, then ask.** In a few sentences: which section is open, its status, and what remains. Then ask whether to continue there or switch sections.

**Decision point:** if the checkpoint names an in-progress section whose file already carries a finished synthesis, the checkpoint is stale, not a resume point. Correct it per the terminal-section rule below and report the correction before continuing.

## Interview discipline

1. **One question per turn.** Never present a list. A list returns a checklist answer, and the thinking that the question existed to provoke does not happen.
2. **After each answer:** a short paraphrase, then either one deepening probe or an explicit close of the thread. Never move on silently — an unacknowledged answer teaches the participant to give shorter ones.
3. **Ladder every "what" answer.** Ask why it matters until something the participant believes surfaces, rather than something they sell. Typically two to four iterations, but the count is an expectation, not a target: the stop condition is a belief on the table.
4. **Push claims to their root reason.** A stated belief or positioning claim is the surface; keep asking why it is true here until the reason underneath it appears or the participant discovers there is none.
5. **Treat thin answers as unanswered.** Generic, jargon-heavy, or vague answers get exactly one request for something concrete: a named client, a specific incident, a number.
6. **Break a plateau with a projective prompt,** at most one per section, when direct questions have stopped producing:
   - "If the brand walked into a room, how would it walk in?"
   - "If the organisation closed in five years, what would customers miss — and what would you regret never having said?"
   - "Name a peer you admire but would never want to become. What specifically makes them the wrong model?"
7. **Saturation gate.** A section closes when probing stops returning information — that observable condition is the rule. Two consecutive probes producing nothing that is not already captured is the chosen default for confirming it. If the last two probes did produce something new, the section is not finished, whatever the elapsed time or the word count.
8. **At the end of a section,** write the section file, then update the checkpoint. In that order: an unwritten section that the checkpoint calls complete is unrecoverable.

## Section sequence

| Section file | What it establishes |
| --- | --- |
| `10_purpose.md` | The belief the brand acts on, stated independently of what it sells |
| `20_positioning.md` | Who it is for, which category it competes in, and what it does that the alternatives do not |
| `30_audience.md` | A concrete portrait of the best-fit client, their trigger situation, and who is a bad fit |
| `40_personality.md` | How the brand behaves treated as a person, and what it must never resemble |
| `50_voice-tone.md` | The verbal register, and how it shifts between a sales page, an apology, and a proposal |
| `60_narrative.md` | The founding story, the conflict it resolves, and what it asks of clients |
| `70_founder-boundary.md` | What the founder's reputation owns, what the organisation's brand owns, and where the dependency is a risk |
| `90_synthesis.md` | The consolidated identity reference, with contradictions between sections resolved |

Run the sections in order. Honour a request to jump, and record the skip in the checkpoint so a later session knows the sequence is not contiguous. **The list is closed:** a section name that is not on it is rejected, not created.

*(If a named instrument is used to structure a section — an archetype set, a positioning template, an identity prism — introduce it to the participants by author and title rather than presenting it as this procedure's own.)*

## Section file contract

Every section file carries two parts, and merging them is the failure to avoid:

- `## Raw` — verbatim quotes, examples, and the participant's own phrasing, attributed by speaker when more than one person is interviewed. Paraphrase does not belong here. Smoothed language cannot be un-smoothed later, and the participant's exact words are the asset the rest of the process spends.
- `## Synthesis` — the interpretation: more than one candidate formulation, so the participant chooses rather than ratifies; open threads; and any contradiction with an earlier section, named rather than quietly reconciled.

## State and file writes

The checkpoint is one small file beside the section files, rewritten after every section:

```json
{
  "session": "<brand>-brand-<YYYY-MM>",
  "outputPath": "<absolute path to the brand identity directory>",
  "completedSections": [],
  "inProgressSection": "10_purpose.md",
  "nextSection": "20_positioning.md",
  "participants": ["founder-a"],
  "lastUpdated": "<ISO-8601 timestamp>"
}
```

**Terminal section.** While the synthesis is being written, `inProgressSection` is `90_synthesis.md` and `nextSection` is `null`. Once it is written, add it to `completedSections` **and set `inProgressSection` back to `null`**. Leaving it populated makes the next session read a finished identity reference as work in progress and re-open it.

**Validate before writing.** Every path segment here arrives from conversation, so all of it is untrusted input:

- Participant names: alphanumerics and hyphens only. Reject any name containing `/`, `\`, or `..`.
- Section file names: only names on the enumerated sequence above.
- Output directory: an absolute path inside the agreed project directory. Reject relative paths and any path containing a `..` segment.

Reject and ask again rather than silently repairing the value.

After each write, confirm in one line: which section was saved, that the checkpoint is updated, and what comes next.

## Multi-participant mode

1. **Interview each participant separately**, writing their answers to a per-participant file rather than into the shared section file. Discussing a section as a group first anchors everyone to whoever speaks first, and the disagreement that would have been the most useful material never surfaces.
2. **Finish a section with every participant before reconciling it.**
3. **Reconcile in the shared section file:** where the answers converge, where they diverge and who holds which position, and which tensions are productive enough to take into a group conversation rather than settle on paper.
4. **Never average two answers into one.** A split recorded as a split is data; a split averaged is invention.

## Output contract

- One file per completed section, each with its `## Raw` and `## Synthesis` parts.
- One file per participant where several people were interviewed, plus the reconciliation in the shared section file.
- A checkpoint file that is current as of the last section write.
- A consolidated identity reference at the end that states which formulation was chosen for each section, records the tensions that were resolved and how, and lists what remains open. It has to be usable as a brief with the interviewer absent.
- A closing status each session: sections completed, section left open, next section, output path.

## Common pitfalls

- Compressing the whole sequence into one sitting, which produces a document with the right headings and nothing under them.

## Examples

**Opening a resumed session.**

- Wrong: "Great — let's talk positioning. Who's your target customer, what category are you in, and what makes you different?" Three questions in one turn, and no state was read: if positioning closed two sessions ago, this re-elicits a thinner version of an answer already on disk.
- Right: read the checkpoint and the open section file, then: "Last session closed purpose and opened positioning — the target-client answer is captured, the category question is not. Continue there, or switch?" Then one question.

**Closing a section.**

- Wrong: "That's forty minutes on audience, so let's move on to personality." Elapsed time is not the condition.
- Right: the last two probes returned only restatements of the disqualifier already captured, so summarise the section back, confirm it, write the file, update the checkpoint. If instead the second probe had produced a new red-flag client type, the section stays open and the next probe follows that thread.
