# Quality Gates

Use this as a pre-merge checklist for ADRs created with `adr-madr-system`.

## Minimum requirements

- The ADR has a clear scope and “why now” trigger in Context.
- Decision Drivers exist and the Rationale explicitly ties back to them.
- At least 2 considered options are documented (or a clear justification for only 1 option).
- Decision is unambiguous (“We will …”) and includes any hard constraints.
- Consequences include at least:
  - 1 negative consequence (tradeoff)
  - 1 risk (if applicable) and a mitigation or acceptance rationale
- Links back to the initiating spec/track/task exist.

## Governance requirements

- If changing an accepted decision, the new ADR uses `Supersedes ADR-XXXX` semantics.
- Accepted ADRs are not rewritten to change the decision/rationale (except trivial typos if your repo allows it).
- ADR index entry is updated in the same change.
  - Prefer managing the index via a managed block and `scripts/update_index.sh` for deterministic multi-agent updates.

## Multi-agent hygiene

- “Deciders” are named (even if they map to roles rather than individuals).
- Any follow-up work is captured as actionable items (links to tasks if available).
