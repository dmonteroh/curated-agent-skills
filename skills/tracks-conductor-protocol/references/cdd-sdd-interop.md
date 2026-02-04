# CDD + SDD Interop Rules

This protocol assumes both:
- **CDD** provides stable project context artifacts.
- **SDD** provides executable work artifacts (specs/plans/tasks).

## When to create/update CDD context

Update `docs/context/` when any of the following change:
- Product goals, user personas, success metrics (`product.md`)
- Major dependencies, data stores, deployment, security posture (`tech-stack.md`)
- Team workflow, quality gates, phase checkpoints (`workflow.md`)

If context is missing, create minimal stubs and improve them as work progresses.

## When to create/update a Track spec

Create/update a track spec when:
- multiple tasks share a goal
- requirements must be agreed on before implementation
- there are cross-cutting constraints or non-goals that prevent scope creep

## When to create/update an ADR

Use `adr-madr-system` when:
- the decision affects architecture boundaries, data model, auth, reliability, scaling, vendor/tooling choices
- you need "supersedes" semantics for decision history

Track specs should link to relevant ADRs; ADRs should link back to the track/spec that triggered them.

## Multi-agent coordination

To avoid agents drifting:
- Always start by checking whether context/spec/plan artifacts exist and are current.
- Prefer adding missing context/spec details over guessing.
- Keep artifacts small; link across them instead of duplicating content.
