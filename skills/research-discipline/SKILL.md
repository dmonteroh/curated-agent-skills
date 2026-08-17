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

## Do not use this skill when

- The task is pure execution — writing code, applying a change, running a command — with no findings to report back.
- The user has already supplied a complete, verified answer and only wants it applied, not re-investigated or re-labeled.
- The output is a single stable fact with no freshness risk and nothing inferred from it (a definition, a constant) — the classification machinery adds no signal over just stating it.

## Workflow

Use the lightest source that can actually answer the question, and stop there:

1. **Local documentation first.** Check whatever is already supplied or already on disk — files, docs, prior conversation context — before doing anything else.
2. **The repository itself, if documentation doesn't settle it.** Code and data are often more current than the docs describing them; read or search the actual repository before going outside it.
3. **External search last, and only after 1 and 2 have been checked and found insufficient.** "Found insufficient" means actually checked, not skipped because it seemed slower.

The floor: an external search is not justified for something local documentation or the repository already answers. If step 1 or 2 settles the question, stop and report from that evidence — do not escalate for thoroughness's own sake.

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

## Freshness dating

Any claim whose truth can change over time — pricing, versions, personnel, the current state of a system — carries the date it was established: when it was checked, not just what was found. Use a concrete date, not "recently" or "currently," which age silently as the report is read later. Stable facts (a definition, a spec that doesn't change) do not need a date; attaching one there implies a volatility that isn't real.

## Common pitfalls

- Blending an inference into a list of sourced facts without a label, because the inference feels obvious.
- Escalating to external search before local documentation or the repository has actually been checked.
- Reporting a freshness-sensitive claim as if it were evergreen, with no date attached.
- Presenting a recommendation as a finding — the two answer different questions ("what is true" vs. "what to do").

## Output contract

A research report produced under this skill states, for each claim or claim cluster:

- Its evidence class (sourced / user-supplied / inference / recommendation).
- Its source or basis, if sourced or user-supplied.
- A concrete date, if freshness-sensitive.
