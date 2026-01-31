# Spec-Driven Development (SDD) Integration

This skill assumes architectural decisions are made as part of SDD artifacts (specs/tracks/tasks) and then recorded in ADRs.

## Traceability rules (bidirectional links)

- Every ADR must link to the initiating artifact(s):
  - spec, plan, track, or task brief (whatever your repo uses)
- The initiating artifact should link back to the accepted ADR once the decision is made.

This keeps the spec truthful and makes decisions discoverable from the work that triggered them.

## Where ADRs fit in an SDD workflow

Recommended decision checkpoints:

- End of discovery / before implementation begins (avoid rework)
- When a spec reaches an “architecture locked” checkpoint
- When you discover a constraint that invalidates the current plan (write a superseding ADR)

## Multi-agent roles and handoffs

To avoid conflicting decisions when multiple agents contribute:

- One “Facilitator” owns decision closure (what gets accepted).
- One “Scribe” owns the ADR document and index update.
- Other agents contribute:
  - Options and tradeoffs
  - Risk, security, cost, and operability review

The ADR is “accepted” only when the facilitator confirms:
- decision drivers are satisfied
- tradeoffs are acknowledged
- follow-ups are captured

## Superseding an ADR under SDD

When a decision changes:

1. Create a new ADR that includes a `Supersedes` section.
2. Update the ADR index: mark the old ADR as Superseded and link to the new one.
3. Update the spec/plan to reflect the new constraints/assumptions and link to the new ADR.
