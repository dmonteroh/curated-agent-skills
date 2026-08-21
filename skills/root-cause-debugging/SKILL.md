---
name: root-cause-debugging
description: "Runs an evidence-first loop on a defect whose cause is unknown: journal every debug artifact before creating it, hold competing hypotheses on orthogonal axes, decide them on captured runtime values, confirm a cause only when toggling it toggles the bug, lock the fix with a failing-first test, then revert every artifact. Use when a program misbehaves and the failure does not name its own cause."
metadata:
  category: workflow
---
# Root-cause debugging

Provides an ordered loop that converges an observed defect onto a confirmed mechanism, then closes it with a test and a clean working tree. The entry condition is narrow: something ran, something was wrong, and the failure does not say why.

Two disciplines hold across every phase, and most of the procedure exists to enforce them.

1. **Runtime truth outranks code reading.** Every claim about why the bug happens cites a value that was observed and written down verbatim. A story assembled from reading source is a hypothesis, never a finding, and a remembered observation is not evidence.
2. **Leave no trace.** Debugging creates artifacts — instrumentation, scratch processes, fixtures, environment overrides. Each is recorded with its revert command *before* it is created, and reverted before the work is called done.

## Use this skill when

- A program produces wrong output, no output, a crash, or a hang, and the failure message does not identify the cause.
- Two or more explanations are plausible and reading the code has not separated them.
- A first fix attempt did not hold, or moved the symptom instead of removing it.
- The failure crosses a boundary — user code, a dependency, configuration, timing, built-versus-source output — and which side owns it is unclear.
- A defect has to be fixed in a way that stays fixed: locked by a test, with the tree left clean.

## Do not use this skill when

- **The failure already names its own cause.** A compile or type error with a file and line, an assertion whose message states the violated condition, a stack trace at the throw site. Read it and fix it. Forming three hypotheses about a typo is ceremony, and it is the most common way this loop misfires.
- **The symptom is measured slowness rather than wrong behavior** — latency, tail percentiles, throughput, a hot path. Performance work owns that; the cues here are wrong output, no output, a crash, or a hang.
- **The intermittence lives in the test suite and the fix is test infrastructure** — shared ports, shared temporary roots, order dependence, a leaked fixture, two suites running at once. Test-infrastructure work owns that. An intermittent defect in the product code is in scope; a suite that interferes with itself is not.
- **The code works and the goal is to understand it.** Explaining an existing system is a different job with a different output.
- **The goal is to find defects nobody has observed yet**, by reading a diff. Review owns that; this loop starts from a failure that already happened.
- **Nothing is running.** The deliverable is an artifact — an extraction, an audit, a document — and what is wanted is a skeptical final check. Reframing a finished artifact returns divergent "what if you tried" tangents, not a verdict.
- **What is failing is the agent's own run** — a loop, a tool error, an exhausted context — rather than the program under test.

## Workflow

### Phase 0 — Ground the session, then open the journal

Answer all seven before attaching anything; each answer goes in the journal's environment snapshot, where `references/journal-and-cleanup.md` records why each one decides the next step.

1. What actually launches the process, including any wrapper?
2. Are symbols, debug info, or source maps present and current?
3. Is another instance running, or the debug port already bound?
4. What configuration does the code path need to reach the bug?
5. Does a repro or a failing test already exist?
6. Will a watcher, reloader, or supervisor restart the process mid-session?
7. Does this session have a wall-clock budget before Phase 3's reframe triggers, and if so, how long?

**Gate.** Any answer of "not sure" blocks Phase 1. Guessing here produces false-positive hypotheses that cost a full round to refute.

Then open **one** journal file at the repository root, excluded from version control through the per-clone exclude mechanism rather than the committed ignore file — so it never appears in a diff and leaves no line behind in the repository's ignore list.

**The journal-then-modify rule.** Before any change to the repository, the shell, or system state, append the intended artifact and its revert command to the journal, then make the change. An artifact found at cleanup with no journal line is a failed run, not an untidy one.

### Phase 1 — Form competing hypotheses on orthogonal axes

Hold at least three at once. One hypothesis produces confirmation bias: evidence gets read looking for support, and contradictions get discounted. Several force queries that *distinguish* between them, which is the only way an observation decides anything. *(Three is a chosen default, not a measured threshold. The reason for a floor above one is the bias above, which is not a number.)*

Three variations on "the handler is wrong" are one hypothesis. Span the space instead:

| Axis | Example framing |
| --- | --- |
| User-code logic | A condition is unexpectedly true, so the handler early-returns. |
| Library behavior | The client swallows the error and returns a default. |
| Configuration | The value is read at load time, before it is populated. |
| Async or timing | The task fails after the response was already sent. |
| Inherited state | An earlier operation mutated state this one inherits. |
| Observability gap | The error is raised and suppressed before logging. |
| Build versus runtime | The code being read is not the code running. |

Each hypothesis carries three written fields: the **claim** in one sentence; the **distinguishing evidence** — the exact value or state that would confirm or refute it, and where it can be read; and **if true, the fix is** in two words, which forces fix cost into view before the hunt starts.

**Collapse rule.** Two hypotheses whose distinguishing evidence is identical are one hypothesis. Collapse them and find a genuine alternative. Being unable to state a third distinct one means the system is not understood well enough yet — read more code before investigating.

### Phase 2 — Run an evidence round

One hypothesis per investigator where the harness has concurrent investigators, sequentially where it does not. This phase fixes the assignment rule and the record format only; how concurrent workers are split, briefed, and integrated is owned outside this skill.

Every observation is recorded as four fields: **source** (file and line, log stream, request, breakpoint), **value** verbatim, **interpretation** in one line, and **which hypothesis it confirms or refutes**. `messages.length=0` is evidence. "The messages seemed empty" is a memory of an observation, and memories are where these sessions go to die.

**Round end.** Each hypothesis takes exactly one verdict: **confirmed**, **falsified**, or **inconclusive**. A round in which none reached confirmed or falsified is a **failed round**, including one that simply ran out of evidence sources. Record the count; it drives Phase 3.

### Phase 3 — Reframe instead of running the same round again

**Trigger:** two consecutive failed rounds, or a wall-clock budget named in Phase 0, whichever comes first. *(The round count is a chosen default. The source fixed its time trigger at two hours; replacing that constant with a budget the session names up front is authored. Either may be re-cut, but the new cut is written down before the session starts, not during one.)*

Past two failures the cause is usually in a category that was never imagined, and more time inside the current mental model is wasted time. Stop investigating and obtain **three independent analyses under three fixed framings** — obvious-but-missed, system-boundary, invariant-violation — whose bodies are in `references/reframing.md`. Run them as passes that do not see each other's output, and prefer a different model for one of them where a second is available; routing work to another vendor is owned outside this skill.

Then walk the outputs in order: **agreement scan** (a candidate appearing under two framings is the likely cause), **disagreement scan** (each conflict becomes the next decisive query), and build a fresh hypothesis set drawing from both. Reset the failed-round counter and return to Phase 2. If two more rounds fail after a reframe, escalate with the full trace rather than guessing a fix.

### Phase 4 — Confirm the cause

A cause may be called confirmed only when **all three** hold:

1. **The captured value is exactly what the hypothesis predicted** — not "consistent with", not "in the right range". The literal value, at the moment that matters.
2. **The observation reproduces.** A flaky observation means a symptom was isolated, not a cause.
3. **Toggle proof, in both directions.** Changing the suspected cause makes the bug disappear, *and* reverting brings it back. One direction alone is correlation. The toggle may be a debugger assignment, a configuration override, or a speculative one-line patch — and it is itself a debug artifact, journalled with its revert command before it is applied. *(Authored: implied by the journal-then-modify rule, never stated in the source, and the toggle is the artifact most often left behind.)*

**Compound-cause branch.** If two hypotheses both survive and neither toggles the bug alone, do not discard both — toggle them **jointly**. A joint toggle that works in both directions confirms multiple contributing causes, and the fix must address every one. Without this branch a binary confirmed/not-confirmed gate loops forever on a two-factor bug. *(Sourced from a second candidate in the same drop.)*

Then write the **mechanism** as one paragraph: the causal chain from cause to observed symptom. Being unable to write that paragraph means the bug is not understood yet — return to Phase 2.

### Phase 5 — Escalate only for a decision a human owns

Ask when evidence is exhausted and the remaining fork is a policy choice; when several valid fixes differ in scope and risk and the preference is not the agent's to hold; or when the fix would change observable product behavior rather than only repair it. Do not ask when one more query would answer it, when the reframe has not been run, or to get permission for the obvious thing.

Each escalation carries the verbatim evidence, **one** decision, options that are actually available today with their scope and risk, and a recommendation stated with its confidence rather than withheld. Two questions in one produce a partial answer and a second escalation. A human's choice of direction is not confirmation — return to Phase 4 and confirm on evidence anyway.

### Phase 6 — Fix test-first

1. **Red.** Write a test that fails *because of this bug*, named like a bug report rather than `test_bug_fix`, on the smallest infrastructure that captures the mechanism. Run it and record the failure output verbatim. A test written after the fix may pass with the fix reverted, and such a test locks something else.
2. **Green.** Make the smallest change that fixes the confirmed mechanism. Over-fixing looks like defensive checks around unrelated code, adjacent refactoring, new configuration the bug did not require, or new abstractions. A diff much larger than the mechanism means either more than the bug is being fixed or the cause was never confirmed — return to Phase 4. *(The source's alarm sat at roughly thirty lines: a chosen heuristic, not a measured limit.)*
3. **Regression.** Run the full suite for the affected package, not only the new test. A newly failing test is evidence, not noise — usually that the mechanism was load-bearing for a path nobody knew about. Return to Phase 4 with it.
4. **Close the observability gap.** If diagnosis burned rounds *because state was invisible*, ship the fix with the log line that would have shown it: this session is the evidence that the line earns its place. Standard — level chosen for the consumer, placed at the decision point, data in fields rather than string interpolation, emitted through the project's own logger. Skip it where the project deliberately does not log. This does not soften the artifact rule: a line whose ongoing consumer can be named is part of the fix, and every other line planted during diagnosis is an artifact.

### Phase 7 — Use the system the way its user does

Tests cover the cases that were thought of. Re-run **the original failing scenario**, not a similar one, on the product's real surface: a browser flow through a browser, a queued job through its trigger, a long-running process for as long as the bug took to appear. Substituting a cheaper surface is how a fix ships broken. Surface table and silent-failure signals: `references/qa-surfaces.md`.

Partial or regressed behavior is not "mostly done" — return to Phase 4. Silent-failure patterns spotted in adjacent code are **not** fixed here; they are recorded as follow-ups and reported.

### Phase 8 — Scrub, then verify the tree

Walk the journal's artifact list top to bottom. Check an item off only after its revert command has run without error *and* a confirming check shows the artifact gone. The tree afterwards differs from before by the fix and its test and nothing else — scan the diff against the detector list in `references/journal-and-cleanup.md`. Remove the journal and its exclude entry last, once the tree check is clean.

## Output contract

Four gates close the work, and **each carries its evidence in the final message**. A gate passed without its evidence shown is a gate failed.

1. **Red to green** — the failing output from before the fix and the passing output after, both shown.
2. **Full suite green** — the suite's own pass line, not just the new test's.
3. **Original scenario re-run** — the command or flow that first failed, with its now-correct output, verbatim.
4. **Tree clean** — the diff summary showing only the fix and the test, plus confirmation that no untracked debug files remain.

The message also states the **root cause as a mechanism in one sentence** rather than a symptom, the fix location, the test name, and any follow-ups deliberately not taken. A claim resting on evidence gathered when the real operation could not be run is labelled as partial evidence, per `references/partial-evidence.md`.

## Examples

**Toggle proof versus a fix that happens to work.** A request returns a success status with an empty body.

- *Wrong:* "The base URL is probably being ignored. Added a fallback — the response is populated now. Fixed." One hypothesis, no captured value, and a change that removed the symptom without ever showing that the suspected cause produces it.
- *Right:* Hypotheses on the configuration, library-behavior, and async axes. Captured at the call site, verbatim: the client's base URL is the library default while the override is set. Clear the override — bug persists. Patch the client to read it — bug disappears. Unpatch — bug returns. Both directions move, so the cause is confirmed; then the mechanism paragraph, then a red test named for the symptom.

**The stand-down, in practice.** A run ends with a type error naming a file and a line. That failure names its own cause: read the line, find the caller passing nothing, fix it. Opening a journal and forming three hypotheses here costs more than the bug.

## Common pitfalls

- Paraphrasing an observation instead of copying the raw value. The paraphrase is where the misreading enters and stops being checkable.
- Treating "the symptom went away" as confirmation. Without the reverse toggle it is correlation, and correlation-driven fixes ship bugs.
- Running a third round of the same framing after two failed ones, because the next query feels close.
- Writing the test after the fix, so nothing proves the test would have caught the bug.
- Keeping instrumentation because it looks useful, without naming the consumer that will read it — or fixing a second problem found along the way instead of recording it as a follow-up.

## References

- `references/journal-and-cleanup.md`: journal template, environment-snapshot rationale, observation format, the revert walk, and the artifact detector list.
- `references/reframing.md`: the three framings with their bodies, and the synthesis order.
- `references/qa-surfaces.md`: product-surface table for the re-run, and the silent-failure signal list.
- `references/partial-evidence.md`: evidence tiers and the combination rule for when the real operation cannot be run.
