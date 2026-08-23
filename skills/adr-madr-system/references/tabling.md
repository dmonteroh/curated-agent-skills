# Tabling a decision

Use this template when a decision is sound and reviewed but blocked by something outside the team's control. A tabled ADR is neither a rejection (permanent, no path back) nor a proposal (nothing settled yet) — it is a decided-yes that is on hold, and its entire value is being resumable later without re-deriving the investigation that produced it.

The rule for when and how to table a decision lives in `SKILL.md` Step F; this file is the reusable artifact shape.

## Template

```markdown
# ADR-XXXX: <Title>

## Status

Tabled (blocked — see "Blocked by" below)

## Blocked by

<The specific falsified assumption, capability gap, or missing dependency, with citable evidence:
- a documented gap, quoted from its source ("the docs explicitly state: '...'")
- a tracked upstream issue, numbered, with its current state (open/closed)
- if a workaround might exist, the specific check performed against it and why it does not clear the bar (e.g. a competing implementation read at a named file/line)>

## Cost of tabling

<What was and wasn't spent so far: code written (or none), research time, artifacts produced. This is what justifies keeping the tabled artifact intact instead of deleting it.>

## Decisions preserved for resumption

<The settled sub-decisions from review, not just the pitch. Each one is a MUST for the eventual implementation unless the un-tabling checklist below finds it invalidated. A future resumer should not have to re-litigate ground already covered.>

## Un-tabling trigger

<The specific external event that clears the blocker, stated as something independently checkable: an issue tracker state change, a changelog entry, a released capability. Not "revisit later".>

## Un-tabling checklist (run in order when the trigger fires)

1. Re-confirm the blocking assumption's real current shape. Read whatever changed, capture a concrete example of the new reality, and record it here.
2. Re-check that the original premise still holds under that reality. Does what made this worth doing still apply in full, or only a narrower slice of it? If narrower, revisit the pitch before touching implementation.
3. Re-run the review that originally vetted this decision, against the revised plan, not the frozen one. Most of the decisions above should carry forward; adjust only what depended on the blocked capability's exact shape.
4. If a second, independent review also vetted the original decision, re-run that one too. Concerns tied purely to the now-resolved blocker should disappear; concerns independent of it still apply.
5. Only then execute the plan below.

## Links

- Spec/track/task: <link or path>
- Upstream issue tracking the blocker: <link>
```

## Distinguish from rejection

A single document can hold both a tabled main path and permanently rejected alternatives — for example, a "What we're not doing" list of options considered and declined for good. Keep them under different statuses: rejected entries get no re-trigger and are not resumable; a tabled entry is. Filing a blocked-but-sound decision as `Rejected` loses the resumable path; leaving it `Proposed` indefinitely loses the fact that it was already decided.
