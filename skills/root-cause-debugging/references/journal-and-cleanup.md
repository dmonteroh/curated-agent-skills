# The journal, the record formats, and the scrub

One file at the repository root holds the whole session. It exists for two reasons: everything created during the session can be reverted from it without guessing, and an interrupted session can be resumed or unwound by whoever picks it up.

Exclude it from version control through the **per-clone** exclude mechanism, not the committed ignore file. A committed ignore entry outlives the session and leaks a debugging convention into the repository; a per-clone exclude disappears with the clone.

## Why the seven environment questions decide the next step

| Question | What a wrong answer costs |
| --- | --- |
| What actually launches the process? | Wrappers, task runners, and supervisor scripts change how debug flags propagate, and frequently swallow them outright. |
| Are symbols, debug info, or source maps present and current? | Missing or stale ones place breakpoints on the wrong lines without saying so, and every observation after that is about the wrong code. |
| Is another instance running, or the debug port already bound? | Attaching to the wrong instance produces evidence about a process nobody is testing. Attach or stop deliberately; never compete silently. |
| What configuration does the code path need? | Missing configuration produces early-return paths that impersonate the reported bug convincingly. |
| Does a repro or a failing test already exist? | Amplifying an existing repro is cheaper and more faithful than inventing one that reproduces something adjacent. |
| Will a watcher or supervisor restart the process? | Restarts drop debugger connections and invalidate breakpoints mid-observation, which reads as a flaky bug rather than a flaky session. |
| Does this session have a wall-clock budget, and how long? | Without a stated figure, Phase 3's budget trigger has nothing to check, and a floor invented after the fact is not "written down before the session starts." |

## Template

```markdown
# Debug journal — <short bug name>
Started: <ISO timestamp>
Goal: <one-sentence statement of the reported failure>

## Environment snapshot (Phase 0)
- Runtime and version: <what actually executes the code>
- Launcher: <the command that starts the process, including any wrapper>
- Ports and sockets in play: <app, debugger, anything already bound>
- Symbols / debug info / source maps: <present and current? how was that checked?>
- Configuration the code path needs: <env, files, credentials>
- Existing repro or failing test: <path, or none>
- Watchers stopped: <yes / not applicable>
- Baseline: <revision under test, working tree clean? yes/no>
- Wall-clock budget: <duration, or none — the Phase 3 trigger>

## Hypotheses
1. [unverified|confirmed|falsified|inconclusive] <claim, one sentence>
   - Distinguishing evidence: <the exact value or state, and where to read it>
   - If true, the fix is: <two words>
2. ...

## Round counter
- Round 1: <verdicts reached, or "failed — no hypothesis decided">
- Round 2: ...

## Artifacts to revert
<!-- Appended BEFORE each artifact is created, never after. -->
- [ ] <file> — <what was added> — revert: <command>
- [ ] <background process or session> — revert: <command>
- [ ] <scratch file or fixture> — revert: <command>
- [ ] <environment override in this shell> — revert: <command>
- [ ] <toggle applied for the Phase 4 proof> — revert: <command>

## Findings
<!-- One block per observation, verbatim, appended in order. -->

## Reframe (if run)
<!-- One subsection per reframe: the three framings' outputs, the agreement and
     disagreement scans, and the hypothesis set they produced. -->

## Root cause
- Mechanism: <one paragraph — the causal chain from cause to observed symptom>
- Evidence: <where the confirming value was captured>
- Toggle proof: <the change, the good result, the revert, the bad result>
- Fix scope: <files, approximate size>

## Final fix
<!-- Fix location and test path, filled during Phase 6. -->
```

## Observation record

Every captured observation takes this shape. Verbatim values only.

```markdown
### <ISO timestamp> — <what was inspected>
- Source: <file:line | log stream | request | breakpoint location>
- Value: `<verbatim>`
- Interpretation: <one line — why this matters>
- Confirms / refutes: H<n>
```

`messages.length=0` is evidence. "The messages seemed empty" is a memory of an observation. Anything about to be paraphrased is worth going back for.

## The scrub

Walk the artifact list top to bottom and run each recorded revert command. Check an item off only when its command exits without error **and** a confirming check shows the artifact gone — the file restored, the process absent from the process list, the port unbound, the scratch path missing. A revert command that ran is not the same as an artifact that is gone.

Beyond the recorded list, three classes of residue are routinely created without being noticed, and each needs its own check:

- **Background processes** started with a debugger attached, and the ports they bound. Confirm the debug port recorded in the environment snapshot is free again.
- **Environment overrides** exported into the working shell rather than passed per-command.
- **Editor drift** — reordered imports or reformatted lines in files that were opened but not changed.

## Detector list for the final diff

Scan the diff and the untracked-file list for these before declaring the tree clean. Each is an artifact, not a fix.

| Pattern | Usually means |
| --- | --- |
| A breakpoint or debugger statement in any language's spelling | Instrumentation left behind |
| An ad-hoc print or console write tagged `DEBUG` | Diagnostic output left behind |
| A debug-macro invocation | Instrumentation left behind |
| `TODO DEBUG`, `HACK`, `XXX` near the fix | Stale marker from a trial fix |
| Commented-out blocks near the fix | Dead code from a discarded attempt |
| Reordered imports or reformatting in files unrelated to the fix | Autoformat drift during the session |
| A session-specific marker string used to find edits again | The marker itself was never removed |

Remove the journal and its exclude entry last, once the tree check is clean. The journal is not part of the fix, and neither is the exclude line.
