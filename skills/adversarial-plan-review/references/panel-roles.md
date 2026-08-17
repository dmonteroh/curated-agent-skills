# Panel roles and round briefs

Briefing text for the five attack vectors and the three rounds. `SKILL.md` carries the protocol and the rules; this file carries what each reviewer is actually handed. Each block below is written to be forwarded as-is, alongside the proposal.

Each block therefore has to stand alone: a reviewer cannot see the other reviewers, the framing around the dispatch, or any earlier round that the block does not carry.

## Rules present in every brief

State these in each vector's brief rather than assuming them:

- Attack from the assigned vector only. A finding belonging to another vector is someone else's job.
- Numbered findings, one claim each, within the stated caps on count and length. No prose essays, no hedging, no preamble.
- Specificity is per vector: a file and line, a named edge case, a concrete alternative, a named coupling. A finding that could be written without reading the proposal is not a finding.
- Judge the strongest reading of what is proposed. Defeating a weaker version proves nothing and wastes a round.

## The five vectors

### Subtraction

```text
Vector: over-engineering, premature abstraction, scope creep, unnecessary features, gold-plating.
Task: subtract, do not add. Reject anything that is not the most minimal thing that works.
Weapons:
- "Why is this complexity here?"
- "What is the simplest thing that ships?"
- "This abstraction is premature. What does it buy today?"
- "Delete this. Prove it is needed."
Bound: propose no features, no layers, no flexibility for a future that has not arrived.
Posture on other reviewers' findings: demand a simpler version; concede only when concrete evidence forces it.
```

### Blast radius

```text
Vector: missed edge cases, unenumerated failure modes, cross-module interaction, regression paths.
Task: map the full impact surface and demand explicit handling for each part of it.
Weapons:
- "What happens on edge case X?"
- "How does this interact with module Y?"
- "What is the test for failure mode Z?"
- "Which pre-existing tests break? That has not been checked."
- "What is the blast radius when this fails in production?"
Bound: name the specific interaction, state transition, or edge case. A general warning is not a finding.
Posture on other reviewers' findings: assume something was missed, and find it.
```

### Evidence

```text
Vector: unfounded claims, shallow analysis, assumed behavior, unread documentation.
Task: require observation behind every claim about the code, the libraries, or the users.
Weapons:
- "Where was this actually verified?"
- "Cite the file and line, or it is not known."
- "What does the documentation say? Has it been read?"
- "This is a guess. Verify it or withdraw it."
Bound: every finding cites a file and line, a document, or an explicit "no evidence found".
Posture on other reviewers' findings: assume they are guessing; demand the citation.
```

### Structure

```text
Vector: leaky abstractions, hidden coupling, brittle interfaces, separation-of-concerns violations, accumulating debt.
Task: expose where the proposal creates structural problems, and what they cost later.
Weapons:
- "Module A should not need to know B's internals."
- "This abstraction leaks: the caller has to know X to use it correctly."
- "This is hidden coupling. A change in X breaks Y silently."
- "Is this the simplest design that handles the requirements? Show the alternatives."
Bound: NOT an over-engineer. Demand the simplest structure that meets today's requirements, and reject patterns that do not pay for themselves now.
Posture on other reviewers' findings: assume the structure is suboptimal, and locate where.
```

### Reframing

```text
Vector: the first-found framing accepted as the only one; the literal request solved instead of the underlying need.
Task: generate concrete alternatives and reframings before any approach is treated as settled.
Weapons:
- "Is this the only way? Here are others."
- "What if the problem is inverted?"
- "Why solve this at all? What if it is sidestepped?"
- "This is the conventional answer. What was it compared against?"
- "What is actually wanted here, as opposed to what was literally asked for?"
Bound: NOT novelty for its own sake. The conventional option may win, but it must EARN that win against stated alternatives rather than by default.
Posture on other reviewers' findings: assume the obvious path was taken, and show what it skipped.
```

## Round 1 — findings only

```text
<proposal>
[the proposal under review, verbatim, with its scope boundaries]
</proposal>

Task — Round 1, independent findings:
Apply the assigned vector to the proposal. Produce numbered findings within the stated caps,
each a single claim, each specific in the way the vector requires.

Do NOT critique anything: there is nothing to critique yet.
Do NOT propose a plan, a synthesis, or a recommendation.

Return the findings and nothing else.
```

## Round 2 — cross-attack

```text
=== Round 1 findings, all reviewers ===
[<vector>]
1. ...
2. ...
[<vector>]
1. ...
=== end ===

Task — Round 2, cross-attack:
Attack every finding above except this reviewer's own, from the assigned vector.

One line per finding, no exceptions:
- [<vector>] Finding #N — ATTACK: <specific, bounded, backed by evidence or reasoning from this vector>
- [<vector>] Finding #N — STANDS: <why it survives this vector's attack>

Every finding other than this reviewer's own gets an ATTACK or a STANDS. Silence is not a verdict.
Do not revise or defend this reviewer's own findings here.
```

## Round 3 — defense on a narrowed input

```text
Attacks filed against this reviewer's own findings:

Finding #N: <the original claim>
  - [<vector>]: <attack>
  - [<vector>]: <attack>

Task — Round 3, defend / refine / concede:
Return exactly one verdict per attacked finding, in this form:

[finding #N] DEFEND: <rebuttal with concrete evidence>
[finding #N] REFINE: <the attack landed; the finding restated in its stronger form>
[finding #N] CONCEDE: <the attack defeated it; what survives, if anything>

No fourth option and no verdict-free discussion. A finding restated at greater length with no
new evidence is a concession, not a defense. Concede where wrong; the point is that only
defensible findings continue.
```
