---
name: research-discipline
description: Labels every claim in a research or investigation report as sourced, user-supplied, inferred, or a recommendation, escalates through sources lightest first, and dates freshness-sensitive findings. Use when reporting results from a lookup, investigation, comparison, or fact-finding task where the reader needs to tell verified fact from the agent's own inference.
metadata:
  category: research
---

# Research Discipline

Provides evidence-labeling and escalation discipline for research and investigation output: every claim tagged by how it was known, sources checked lightest first, and freshness-sensitive findings dated.

## Use this skill when

- Reporting findings from a lookup, investigation, comparison, or fact-finding task.
- The output will be acted on by someone who needs to know how confident to be in each claim, not just what the claim is.
- The question is freshness-sensitive: pricing, versions, current system state, or anything else that could have changed since it was last checked.
- A search or lookup is about to run and the question's phrasing may not match the vocabulary the sources actually index.
- The answer will come from outside sources of differing authority — an issuing authority, an index that mirrors it, a summary of that index — and which one it came from changes how much weight the claim can carry.

## Do not use this skill when

- The task is pure execution — writing code, applying a change, running a command — with no findings to report back.
- The user has already supplied a complete, verified answer and only wants it applied, not re-investigated or re-labeled.
- The output is a single stable fact with no freshness risk and nothing inferred from it (a definition, a constant) — the classification machinery adds no signal over just stating it.
- The retrieval is one exact identifier against one known authoritative source — a record number, a named file — with no phrasing to reframe and no competing source to rank. *(Authored: the source material gates its pre-flight on matching a known failure class and proceeds silently otherwise; this states that gate as a stand-down.)*

## Workflow

Use the lightest source that can actually answer the question, and stop there:

1. **Local documentation first.** Check whatever is already supplied or already on disk — files, docs, prior conversation context — before doing anything else.
2. **The repository itself, if documentation doesn't settle it.** Code and data are often more current than the docs describing them; read or search the actual repository before going outside it.
3. **External search last, and only after 1 and 2 have been checked and found insufficient.** "Found insufficient" means actually checked, not skipped because it seemed slower.

The floor: an external search is not justified for something local documentation or the repository already answers. If step 1 or 2 settles the question, stop and report from that evidence — do not escalate for thoroughness's own sake.

### Before the ladder: is the question searchable as phrased?

A question can be well-formed and still be unanswerable in the words it was asked in, because the sources index a different vocabulary than the asker used. Read the question against these classes before spending a search on it — a reframe or one clarifying question costs a turn, while a doomed search costs the whole run and returns confident noise:

- **The asker's framing is not the sources' vocabulary.** The literal phrase describes the asker's situation rather than how anyone writing about it would title it. Reframe into the attributes the sources actually carry, or ask once for them.
- **A number in the query collides with unrelated content.** A bare figure drags in everything else that figure names. Strip it unless removing it changes the subject — a version number is part of the subject, an age or a count usually is not — and keep it in the framing reported back to the asker.
- **Tutorial-shaped phrasing against discussion-shaped sources.** "How to use X" matches instructional titles; practitioners writing about X say "my X setup" or "X in production". Reframe to the vocabulary of the corpus being searched.
- **A bare common noun with no anchor.** The corpus is unbounded and everything returned is nominally on topic, so nothing returned is a finding. Ask which facet is meant before searching.
- **The topic's language or script is not the corpus's.** A source set dominated by one language returns padding rather than a real absence for a topic in another. Route to a source with genuine coverage of that language, and say up front which sources are expected to return nothing so the gap is not read as a finding.

Ask at most one clarifying question, then proceed on whatever comes back; if the asker declines to narrow, search the reframed query rather than the literal one and record the reframe. A question that matches no class needs one line saying so, not a written pre-flight.

### Rank external sources by authority, not only by cost

The ladder above orders sources by what they cost to check. Once the question leaves the local material a second ordering applies: prefer the system of record — the authority that issues or maintains the fact — over an index, aggregator, or mirror that republishes it. Secondary sources are convenience: fast to reach, fine for orientation, and labeled as secondary wherever a claim rests on one. When a claim is materially consequential, a convenience index is a lead rather than the answer, and it is confirmed against the record before the claim leaves the report as sourced.

The two orderings do not conflict: cost decides which tier to enter, authority decides what to trust once outside. A cheap mirror that answers the question is still the right first stop — it just cannot be the last one when the answer matters.

## Evidence classes

Every claim in a research output belongs to exactly one of four classes. Tag it inline, next to the claim — not once in a preamble the reader has to map back onto the findings:

- **Sourced** — found in a checkable source (a doc, a file, a search result). Name the source.
- **User-supplied** — the user asserted it; it was not independently checked.
- **Inference** — follows from combining the above but was not itself stated anywhere.
- **Recommendation** — the agent's judgment call about what to do next, distinct from what was found.

A report where the reader cannot tell which class a claim belongs to is not research — it is prose in the shape of research. The specific failure to guard against is treating an inference as if it were sourced, because it followed naturally from something that was.

Contrast:

- Weak: "The vendor's status page says the outage was caused by an expired certificate, so add expiry monitoring and rotate every other cert now."
- Labeled: "Sourced (vendor status page, checked 2026-08-17): outage caused by an expired certificate. Recommendation: add expiry monitoring. Inference: since one cert expired unnoticed, others may be unmonitored too — not yet confirmed which."

**A silent source and a source that never answered are different results.** A check that completed and returned no matches establishes an absence. A check that was rate-limited, timed out, was refused authentication, was unreachable, returned a shape that could not be read, or was never configured establishes nothing at all. Track the outcome per source and never collapse the second kind into "nothing found in X" — that sentence claims a negative result the run did not earn. Where a source did not complete, name it, report the conclusion as partial coverage, and rest it only on the evidence that actually came back.

**A recorded fact and the conclusion drawn from it are different claims.** What a register, ledger, or log records is sourced; what it implies — who currently owns the thing, whether the obligation still binds, whether the arrangement is compliant — is an inference, and often one the agent is not competent to assert in its confident form. Label the record as sourced, label the reading as inference, and where the conclusion carries legal or material consequence, hand it to a qualified reviewer with the record attached instead of settling it in the report.

## Freshness dating

Any claim whose truth can change over time — pricing, versions, personnel, the current state of a system — carries the date it was established: when it was checked, not just what was found. Use a concrete date, not "recently" or "currently," which age silently as the report is read later. Stable facts (a definition, a spec that doesn't change) do not need a date; attaching one there implies a volatility that isn't real.

## Common pitfalls

- Blending an inference into a list of sourced facts without a label, because the inference feels obvious.
- Escalating to external search before local documentation or the repository has actually been checked.
- Reporting a freshness-sensitive claim as if it were evergreen, with no date attached.
- Presenting a recommendation as a finding — the two answer different questions ("what is true" vs. "what to do").
- Searching a collision-prone name bare. When the subject's name is also a common word or another public figure, anchor every query to a specific named entity — the organization, product, or role that pins it — not just the first query, and mirror that anchor in whatever criterion ranks the results. A partly anchored search returns a set that looks on topic and is not.
- Reading a tool's degradation notice as a limit on the agent. A pipeline reporting that it fell back to a default path is often reporting that the step it wanted was skipped upstream, not that the capability is unavailable; check which before recording the gap as a finding.

## Output contract

A research report produced under this skill states, for each claim or claim cluster:

- Its evidence class (sourced / user-supplied / inference / recommendation).
- Its source or basis, if sourced or user-supplied.
- That the source is a secondary index or mirror rather than the issuing authority, wherever a claim rests on one.
- A concrete date, if freshness-sensitive.

And once for the report as a whole: which sources were consulted, and for any that did not complete, that coverage is partial and which channel is unestablished.
