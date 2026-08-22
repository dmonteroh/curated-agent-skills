---
name: codify-exploration
description: "Promotes a repeated exploratory task into a deterministic, replayable on-disk unit: a written contract, a script with a pure parser, a frozen copy of its dependency, a dated fixture captured from the real source, and a test pinned to that fixture. Use when an exploration just succeeded and will be asked for again."
metadata:
  category: workflow
---
# Codify Exploration

Provides a procedure for turning an exploration that already succeeded — probing a page, an API, a log format, a command's output — into a self-contained unit on disk that later replays as code instead of being re-derived as reasoning. The entry condition is recognition: this exploration has been done before, and its answer should be the same one next time rather than a plausible near-match.

The pattern applies wherever acquisition is cheap to re-run but interpretation was the expensive part to work out, and interpretation can be written as a pure function of one capturable input. That seam decides whether a unit is worth building; the subject matter does not. It transfers unchanged to an HTTP response, a command's stdout, a log file, a config dump, or a query result set.

Replay is also faster than re-exploration, but the source material asserts that speedup without ever measuring it — state the benefit qualitatively and never as a latency figure or a multiplier.

## Use this skill when

- An exploration just produced a result the user accepted, and the same request is likely to arrive again.
- The agent is about to re-derive selectors, field names, paths, or record boundaries it has derived before.
- Interpretation of the raw response can be expressed as a pure function — same input, same output, no I/O.
- The answer must be stable across sessions, and a subtly different answer each time would go unnoticed.

## Do not use this skill when

- Acquisition is the hard part — multi-step auth, stateful navigation, timing, lazily loaded content. A stored fixture pins the parser and proves nothing about acquisition; codify only with that limit written into the contract.
- No bounded prior exploration is in reach and the unit would have to be assembled from scattered chat fragments.
- The result came out of an already-codified unit. There is nothing left to codify.
- The exploration answered a one-time question. A unit that runs once is pure overhead.
- The flow mutates state — writes, posts, purchases, deletions. Those need per-step confirmation and stay outside this procedure: codification is what converts an open-ended capability into an enumerable one, so until the unit exists there is nothing enumerable to approve.
- The right artifact is a service that other clients call through a published schema. This procedure produces a unit an agent authors for itself from its own transcript: no server to run, no schema to negotiate.
- What is worth keeping is facts rather than a procedure. Notes recalled into a prompt are a different artifact with a different lifecycle; do not build a unit to hold them.
- The question is how much process a piece of work deserves in general — depth of review, which gates run, whose approval lands it. That is a per-change delivery judgment; this procedure decides only whether one exploration becomes a unit, and where that unit lives.

## The unit on disk

Five files, one per concern. "Copy the directory anywhere and it still runs" is the test of self-containment.

```
<unit-name>/
├── CONTRACT.md                       # machine-readable header + 2-3 sentences of prose
├── script.<ext>                      # acquisition in main(), interpretation in exported pure helpers
├── _lib/<dependency>                 # frozen copy of the client library, taken at authoring time
├── fixtures/<source>-<YYYY-MM-DD>.*  # one real captured response
└── script.test.<ext>                 # parser test pinned to that fixture
```

The contract is the only metadata file: machine-readable header (name, trigger phrases, arguments, source, dependency version, whether ambient credentials are granted) plus the prose, in one file. A second sidecar of metadata is a second thing to drift.

Naming: lowercase letters, digits and single dashes, starting with a letter, no consecutive dashes, short enough to retype from memory (the source caps length at 32 characters — a chosen default, not a measured one). The header carries 3-5 trigger phrases (also a chosen default) mixing the canonical phrasing with the paraphrases a user would actually say, because those phrases are the unit's entire matching surface.

**Where the unit is written is a second decision.** The five files are the same at either tier; what differs is the location and who is expected to find it.

- **Task-local.** A task that recurs with changing inputs inside one piece of work gets its unit in a scratch or project-local working area — same contract, same fixture, same pinned test, discoverable only by whoever is doing that work, and promoted no further.
- **Shared.** A task that recurs across sessions, repositories, or people gets its unit in the single location every agent enumerates before exploring (step 11), where its trigger phrases have to compete with every other unit's.

Promotion between the two is a separate call from building the unit at all, and it is skipped in both directions: promote everything and the shared location fills with units nobody else can trigger, promote nothing and each operator rebuilds the same one. Five signals argue for shared: the workflow recurs across sessions, repositories, or people; it needs a specific tool or safety sequencing; failures repeat because a gate keeps getting skipped; it has a stable input/output contract; others benefit from seeing its status. The source's bar is "at least two of the five" — a chosen constant with no derivation behind it — so record *which* signals hold and argue from those, rather than promoting on a count. A unit that stays task-local is a finished outcome, not a half-promoted one.

## Workflow

1. **Locate the exploration, or refuse.** Walk back over recent turns (the source bounds the walk at 10 — a chosen default) for the most recent exploration that is bounded — an identifiable intent line and the trailing structured output it produced — and whose result the user did not later invalidate. Output: the intent string and the winning calls, or a refusal.
2. **Name it and look it up.** Output: a name that satisfies the naming rule, plus the result of a lookup for an existing unit of that name in every location the agent would search.
3. **Slice the input down to the winning attempt.** Keep only the final-attempt calls that produced the accepted output, plus the user's stated intent string. Output: that slice. Drop failed selector attempts, unrelated conversation, and anything from an earlier session. Synthesizing from the agent's own recent context is a legitimate replay source when no structured recorder exists, but only because the walk-back is bounded and the slice is explicitly narrowed.
4. **Split acquisition from interpretation.** Interpretation MUST be a pure function. Keep every acquisition call in `main()`, however many there are, and extract parsing into exported helpers that take the raw response and return records. Output: a script whose parser can be called directly, with nothing live running behind it. This is the rule the whole pattern rests on: it is what makes the unit testable, and what makes the pattern apply outside the domain it came from.
5. **Capture one real fixture.** Re-run the acquisition step once and write the raw, unmodified response under `fixtures/`, with the source and the capture date in the filename. Output: the fixture file. The date is the only staleness signal the unit carries.
6. **Write the test against that fixture.** Output: a test asserting both shape and content — at least one record parsed, and every record's key fields present, non-empty, and of the expected type. A test that only asserts the parser did not throw is not sufficient; it keeps passing after the parser starts returning nothing.
7. **Freeze the dependency inside the unit.** Copy the shared client library into `_lib/` byte-identically at authoring time, so version drift becomes structurally impossible rather than something to detect. Output: the vendored copy, plus the version or commit it was taken from recorded in the contract header. *Authored, not sourced:* the version stamp is an addition — the source freezes the copy but defers the command that re-vendors it, which leaves a frozen unit with no route for an upstream security fix. Recording what was frozen is the minimum that makes a deliberate re-vendor possible later.
8. **Write the contract prose.** Two or three sentences: what the script does, what it acquires, what shape it returns. Output: `CONTRACT.md`. No conversation context, no chat fragments, no narration of how the exploration went. This is a durable on-disk artifact that other agents will read cold — the input slice was narrowed in step 3, and this is the separate rule that keeps the output from reading like a transcript.
9. **Stage, test, approve, then rename.** Write the unit into a temporary directory outside the live tree, run its test there, and move it into place only on test pass *and* explicit user approval. Output: either a committed unit or an empty temp directory. On either failure, delete the staged directory entirely: no tombstone, no partial artifact, no "almost shipped" state. A broken unit visible to future agents is worse than no unit, because agents will reach for it. Resolve the destination path and check what it actually is before the rename, so a symlink cannot redirect the commit.
10. **Verify against the prototype's own output.** Run the committed unit once and compare its result with what the exploration produced. Output: a match, or a stated discrepancy. A mismatch means synthesis drifted — surface it and let the user decide. Never silently roll back a unit the user approved.
11. **Make it discoverable, or the work is write-only.** Output: the unit written to the single location the agent enumerates before exploring, with trigger phrases written for that scan. *Authored, not sourced:* the source's own answer to discovery was never built, and nothing else in it fills the slot. Absent something here, units accumulate and nothing ever reaches for them — see Limits.

## Decision points

- Nothing bounded inside the walk-back → refuse in one fixed sentence and stop. No silent fallback, and never assemble a unit out of fragments. A candidate exists but the conversation has moved on → ask once, and accept only an explicit yes.
- The name is taken where the unit would be written → refuse. Taken where lookup takes precedence → the new unit would be shadowed; say so and get a decision before writing, not after.
- The test fails on a fixable parser bug → fix it inside the staging directory and retry, showing the diff before each retry, within a small fixed budget (the source allows 2 — a chosen default). The test fails environmentally — import error, unreachable service, missing runtime → discard at once. Retrying does not fix an environment.
- Approval is declined → discard the staging directory. Offer the code for reading, never a half-landed unit.
- The unit needs ambient credentials → the default is no. Granting them flips a declared field in the contract, and the root credential is withheld even then.

## Constraints

- **Never evaluate agent-authored code inside the host process.** Three named escape routes make it unsafe regardless of what was scrubbed beforehand: ambient globals the code inherits, gadgets reachable through constructors of objects it is handed, and a time-of-check gap in which code can change what it does between the moment a human approved it and the moment it runs. In-process isolation strong enough to close these is a large project. Running the unit as an ordinary external process that talks to the service over the same interface any third-party client would use costs nothing and closes them all — and it means the unit earns no privilege from proximity.
- **Scrubbing a child process's environment is hygiene, not a sandbox.** This is a separate ruling with separate reasoning, and it is the one the "security theater" verdict was aimed at: the original design called env-scrubbing a sandbox, and naming it that was the error. Removing secrets from a spawned unit's environment is worth doing as defense in depth, but the unit can still read every file the operating-system user can read. The enforceable boundary is a scoped, per-spawn capability minted by the service that owns the resource, excluding administrative verbs and revoked when the spawn exits. Enforcement must sit with the resource owner; anything the child is asked to enforce about itself is advisory. Keep trusted-versus-untrusted a declared contract field so real OS-level isolation can be installed behind it later without redesign. Detail: `references/trust-and-execution.md`.
- **No index file — enumerate the directory.** Discovering units by listing the directory and reading each contract's header eliminates the "index disagrees with disk" bug class instead of managing it: a hand-copied, pulled, or deleted unit is correct immediately. This rule is about executable units, which always have an on-disk representation; it says nothing about indexes over items that have none.
- **Output protocol.** The structured result goes to stdout, logs go to stderr, success is the exit code, and the unit carries a per-run timeout and a maximum stdout size so a hung or runaway unit is distinguishable from a slow one (the source sets 60 seconds and 1 MB, justified as matching common CLI conventions — chosen defaults, not measurements).

## Examples

**Parser extraction — wrong, then right**

```
# Wrong: interpretation is welded to acquisition, so nothing is testable offline.
def main():
    raw = client.get(SOURCE)
    for row in raw.split(ROW_MARKER):
        print(extract_title(row), extract_score(row))
```

```
# Right: acquisition stays in main(), interpretation is exported and pure.
def parse(raw):                       # raw -> list[Item]; no I/O, no globals
    return [item_from(row) for row in raw.split(ROW_MARKER)]

def main():
    print(to_json(parse(client.get(SOURCE))))
```

**Test assertion — wrong, then right**

```
# Wrong: passes forever, including after the parser starts returning zero rows.
assert parse(load_fixture()) is not None
```

```
# Right: shape and content, so a format change turns the test red.
items = parse(load_fixture())
assert len(items) > 0
for it in items:
    assert isinstance(it.title, str) and it.title != ""
    assert isinstance(it.score, int)
```

**Contract prose — wrong, then right**

- Wrong: "After a few tries we found the right rows — the first selector matched the nav bar, so we switched to the list container the user confirmed was correct."
- Right: "Fetches the source's front page and returns one record per list item as JSON on stdout: title, score, permalink. Fixture captured 2026-08-16; the parser is pinned to that snapshot's markup."

## Limits and unsolved problems

- **The fixture proves the parser, not the world.** A fixture-pinned test shows the parser still parses what it parsed. It never shows the source still looks like the fixture. *Authored, not sourced:* the source defers staleness detection entirely, so the working rule here is to re-capture the fixture whenever the unit fails against live input, and to treat the capture date as an argument for re-checking, never as an expiry that fires on its own.
- **Discovery is the pattern's real gap, and it is unsolved.** Nothing reaches for a codified unit once it exists unless something makes the agent look. The source's answer — inject a listing into the session at start — was planned and never built. Until a location convention and a scan step are actually in place, codification is write-only, and this is the largest distance between the pattern as documented and the pattern as useful. Treat step 11 as the minimum, and say plainly when a library has no such step.
- **A frozen dependency does not receive upstream fixes.** That is the price of making drift impossible. The version stamp in step 7 makes a deliberate re-vendor possible; nothing makes it automatic.
- **The unit inherits a runtime requirement** from whatever language it was written in. Choose a runtime the host already guarantees, or "copy the directory anywhere and it runs" is false in practice.
- **Synthesis from conversation is best-effort.** A complex prototype may need a hand edit; the post-commit comparison in step 10 is what catches the difference, and it only catches what the comparison covers.
- **One acquisition target per unit.** Parameterize through declared arguments when the pattern is regular; otherwise write a second unit.
- **The approval gate assumes someone can answer.** *Authored, not sourced:* in a non-interactive run, leave the unit staged, report its path and its test result, and do not commit. Committing without approval and refusing outright both discard work the human might want.

## References

- `references/trust-and-execution.md` — the two execution rulings with their separate reasoning, the capability-versus-environment trust model, and the output protocol.

Provenance: distilled from a design document and reference implementation for a browser-automation skill system; the browser framing is incidental and was stripped. Every figure in that source was asserted rather than measured, so figures appear here only where labelled as chosen defaults, and nothing in this skill is a benchmark.
