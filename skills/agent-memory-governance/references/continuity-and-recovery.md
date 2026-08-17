# Continuity across session boundaries

Consult when the concern is losing context at a compaction, a session end, or a handoff. The trust rules that govern what may be reloaded are in `SKILL.md`. Rules marked *[authored]* are this skill's generalization rather than a statement in the source designs.

## The missing piece is awareness, not storage

Context compaction preserves a generic summary and destroys file reads, reasoning chains, and intermediate decisions. Artifacts written to disk survive it — plans, reviews, checkpoints — but the agent no longer knows they exist, so the reasoning behind decisions already made silently vanishes and the next stretch of work re-litigates or contradicts them.

The store was never the failure. The pointer to it was. What standing instructions have to say is that these files exist, that they contain decisions already made, and that they are to be re-read after a compaction.

## Three layers, all cheap

1. **Context recovery.** After a compaction or at session start, list the artifact directory and read the most recent file. A few lines of standing prose buys this.
2. **Session timeline.** Every unit of work appends one line: timestamp, unit name, branch, key outcome.
3. **Cross-session injection.** At session start on a branch with recent artifacts, state the last session and the latest checkpoint before the user types anything.

## Checkpoints

A checkpoint records four things:

- what is being done;
- which files are being edited;
- what was decided;
- what remains.

Take one before stepping away, before a complex operation, and at any handoff between agents. Carry the branch in the checkpoint's own metadata, so recovery can filter by it.

**Archive on completion; do not delete.** A finished run's checkpoints stay readable, which is what keeps a failed run debuggable afterwards.

## Recovered context is not trusted context

Recovery can inject wrong-branch state, obsolete plans, or invalid checkpoints, and it does so confidently. Three filters apply before recovered material is presented as current:

- filter checkpoints by the current branch, using the branch recorded in the checkpoint itself;
- filter displayed history by branch as well;
- flag an artifact past the staleness bound as possibly stale rather than presenting it as current (`SKILL.md`, `Chosen defaults`, for the bound and its status).

## Conditional injection and progressive disclosure

Memory guidance is injected only where it can be acted on, and disclosed in layers:

- Where no memory backend exists, suppress the guidance before the agent ever sees it, rather than shipping instructions it cannot follow.
- Keep standing overhead to the short form — when to read, when to write, and what the budget is.
- Put the detailed write rules in a document read at the moment of writing, not in every prompt.

## Verify the round trip

The persistence path is the part most likely to be untested, because it fails silently: the agent reports a save, the run ends, and nothing was stored. Run a round-trip check that answers one question — is the data the run intended to save actually retrievable afterwards — by writing a record and reading it back through the normal retrieval path in a separate session or process. A save that returns success is not evidence; a retrieval that returns the record is. *[authored: the sources name the untested-persistence gap and pair it with a round-trip test; requiring the check is this skill's rule.]*
