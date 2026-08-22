---
name: code-review
description: "Provides high-signal, fast code review with selectable modes (quality, security, performance, tooling), triage of a third-party review bot's comments, an optional blind second-opinion pass, and stop conditions when the review applies its own fixes. Includes a safe-by-default script to scan diffs and produce a deterministic report."
metadata:
  category: workflow
---
# code-review

Provides a canonical code review workflow designed for speed, depth, and low noise.

It replaces overlapping code-review skills by providing explicit review modes:
- **quality**: correctness, clarity, maintainability, API ergonomics, review tone
- **security**: authz/authn, input validation, injection, secrets, supply chain
- **performance**: hot paths, I/O patterns, query behavior, allocations, scalability
- **tooling**: CI/CD checks, linters, static analysis, test signals, automation hooks

## Use this skill when

- Reviewing pull requests, diffs, or local changes.
- Establishing code review standards for a team.
- Auditing for correctness, security, performance, or maintainability before merge/release.
- Reviewing a machine-generated or bulk-refactored change, where the likely defect is an omission rather than a wrong line.
- A third-party review bot has already commented on the diff and its comments need triage.
- A second, independent reviewer is available and the two reviews need to be combined.
- The review is authorized to apply its own findings to the working tree and needs stop conditions.

## Do not use this skill when

- There are no code changes to review.
- The request is to implement a feature (review can be a follow-up).
- A hard, automatic merge gate is what is wanted: the scan in step 3 is advisory by construction and exits zero whatever it finds. Blocking rules belong in the project's CI configuration.

## Required inputs

- Diff, PR link, or changed files list.
- Change intent and constraints (risk tolerance, compatibility needs).
- Runtime context (production vs internal, threat model, scale).

## Quick start

1) Run the scan (optional but recommended):

```sh
scripts/review.sh scan
scripts/review.sh report
```

2) Review manually using the mode checklists:
- `references/checklists.md`

## Workflow

### 1) Establish review context

Output:
- change intent (what and why)
- constraints (deadlines, compatibility, risk tolerance)
- target environment (prod/internal, scale, threat model)

### 2) Triage scope

- Identify changed files and entrypoints.
- If the diff is huge, sample by risk: auth, money, data integrity, concurrency.
- If requirements are missing or ambiguous, ask clarifying questions before findings.

Output:
- changed files summary
- high-risk areas to prioritize
- open questions (if any)

### 3) Run automated signals (best-effort)

- Run `scripts/review.sh scan` to collect:
  - changed files list
  - suspicious patterns (best-effort heuristics)
  - TODO/FIXME hotspots
- If project tooling exists, run it (tests/linters). If not available, note it.
- If `git` is unavailable, document that the scan used a full-repo fallback.

Wiring rules for any advisory scanner used here — this skill's script or a project's own:

- Mark its output INFORMATIONAL and keep it out of the pass/fail decision. It rides inside this step's report section; it never becomes its own pipeline stage, and it never gets a row in a review-readiness or gating dashboard. Those dashboards track reviews that are run and then pass or fail; a diagnostic that cannot fail has no status to show there.
- Report it as a delta against the base ref — findings this diff introduced and findings it removed (`+2 new / -3 removed`) — not as an absolute count over the tree. A delta is attributable to the diff under review; an absolute count is not, because it also counts hits that predate the change.
- Exit zero regardless of what the scan finds. A nonzero exit turns the diagnostic into a gate, whatever its documentation says.
- If the tool is not installed or not runnable, omit its section silently: no warning line, no degraded-mode banner. Availability of an advisory tool is not a review finding.

The bundled `scripts/review.sh` scan reports hits on the changed files as they currently stand; it does not compute the delta itself. Where a delta is required, produce the same hit set for the base version of those files — from a checkout or worktree at the base ref — and subtract. Where that is not possible, label the figure an absolute count — never present a whole-tree count as if it were attributable to this diff.

Output:
- scan artifacts paths
- scan delta (new / removed) against the base ref
- tooling results or missing-tool notes

### 4) Triage third-party review-bot comments

Applies when another automated reviewer has already commented on the diff. Triage every open comment before writing findings — untriaged bot comments pile up until the whole stream gets ignored, which costs the team the tool. Do not pass the comments through raw, and do not dismiss them in bulk.

Put each open comment in exactly one bucket:

- **Valid** — fold it into this review's own findings at this review's severity scale and fix it before merge. It stops being a separate comment stream at that point.
- **Already fixed** — reply naming the commit that fixed it. Identify that commit before replying (for example, search history for the change to the cited lines). If no commit can be named, the comment does not belong in this bucket.
- **False positive** — never auto-dismiss and never auto-reply. Draft the reply explaining why the comment does not apply, present it to a human next to the alternative of accepting the comment, and send only after the human confirms.

Keep a false-positive history file checked into the repository under review, at a fixed path recorded in the project's own docs so every run finds the same file. Append one entry per human-confirmed false positive, recording what a later run must match on — the bot's rule identifier and the code pattern it fired on — plus why it does not apply. Decide and write down that match criterion when the file is created: an entry is reusable only if a later run can decide "same pattern as before" from what is written in it.

On later runs, check each new bot comment against the history first and skip the ones matching a recorded entry, noting the skip in the report instead of replying again.

Count triage outcomes each run (valid / already fixed / false positive) and keep the running totals alongside the history. The bot's precision then becomes a counted trend rather than an impression, and a tool whose precision keeps falling can be argued about with numbers.

Decision points:
- If a bot comment is valid and no first-party finding covers it, it becomes a finding with its own severity, not a footnote.
- If the human rejects a drafted false-positive reply, the comment moves to the valid bucket and no history entry is written.

Output:
- a bucket for every open bot comment, plus the list skipped by history match
- valid comments merged into the findings list
- drafted false-positive replies awaiting human confirmation
- new history entries appended, and this run's triage counts

### 5) Manual review by mode

Pick one or more modes and follow the corresponding checklist:
- `quality` (default)
- `security`
- `performance`
- `tooling`

**Absence pass** — run alongside whichever modes are selected. Every mode checklist tests properties of the lines that are present; a whole class of defect consists of lines that are not there, and no amount of scrutiny applied to the diff will surface them. Ask what is missing, not what is wrong. This matters most on machine-generated and bulk-refactored changes, which are written for the representative case and are fluent enough that an omission reads as a finished implementation — but the three checks below are good review checks against code of any origin, so run them on the change rather than on a judgment about who or what wrote it.

- **Failure paths.** For every operation in the change that can fail — I/O, network, permissions, allocation, parsing — locate the handler and confirm it catches a specific condition rather than everything. A bare catch-all, an empty handler, or a log-and-continue where continuing is wrong is a finding. Check the candidate against the scanner-exemption patterns listed under "Applying fixes to the working tree" before raising it: deliberate fire-and-forget, catch-and-log where an uncaught error would take the process down, and total suppression on a shutdown path are correct as written, and this pass must not re-raise what that list already exempts.
- **Resource pairing.** For every acquisition in the change — opened handles, pooled connections, subscriptions, listeners, timers, watchers, temporary files, spawned tasks — locate the matching release, and confirm it runs on the failure path as well as the success path. An acquisition with no release is a finding whether or not the language is garbage-collected: collectors reclaim memory, and do not close connections, cancel timers, or unregister listeners.
- **Named-symbol existence.** Every module the change imports resolves to a declared dependency, and every external API member it calls exists in the version actually pinned. Generated code invents plausible module names and plausible method names, and calls members a previous major version exported. Neither compilation nor type-checking is this check — a dynamic language will not catch it, and a lockfile that happens to contain a same-named package does not establish that the member exists. Resolve each name against the installed or pinned source, never from memory.

Decision points:
- If changes touch auth, secrets, or input parsing, include `security`.
- If changes touch hot paths, queries, or batch jobs, include `performance`.
- If no tests exist for new behavior, record a test gap.
- If an imported module or called API member cannot be resolved against the pinned version, that is a finding on its own, not a note — an unresolvable symbol is a change that cannot run.

Output:
- mode-specific notes
- absence-pass results: unhandled or over-broad failure paths, unpaired acquisitions, unresolved imports and API members
- draft findings list with severity

### 6) Second-opinion pass

Optional, and worth running only under one constraint: the second reviewer must not see the first review's findings. Blindness is what makes agreement evidence. A reviewer that read the first review and then agreed with it has confirmed nothing — record that as a re-read, not as a second opinion.

- Back the second pass with a different underlying model, or with a human. Two runs of the same model over the same diff share the same blind spots, so their overlap measures little.
- Give the second pass the same diff and the same change intent, and nothing else from the first pass.
- Have each pass grade its own findings on the severity scale in `references/output-format.md` and return one verdict: PASS or FAIL. Any BLOCKER means FAIL, mechanically, however the rest of the review reads — the verdict is computed from the findings, never judged after them.

Split the two finding sets three ways and report them as three lists, never merged into one:

- **Overlap** — both passes flagged it. Highest confidence; work these first.
- **Unique to the first pass** and **unique to the second pass** — one reviewer saw it and the other did not. These are the reason for running two passes at all: they are where each reviewer's blind spots show. A finding is not discounted for being single-source; it is triaged like any other.

**Deciding that two write-ups are the same finding.** Computing the overlap bucket is itself a judgment call, so fix the criterion before splitting rather than per finding. Left unstated, the test drifts run to run: the same diff reviewed twice yields a different overlap set depending only on how loosely the matcher read, and the skill's highest-confidence bucket becomes its least reproducible one.

- **Match on location and issue, both.** Two findings are the same finding only when they cite the same file and line *and* describe the same underlying problem. Either alone is not a match.
- **Same location, different problem — keep both**, tagged co-located. Proximity is not identity; collapsing on it deletes one of two real findings and leaves no trace that it existed.
- **Same problem, different locations — keep both**, cross-referenced. That pair is evidence the mistake was reused across the diff, which is a larger finding than either instance alone. It is not one finding reported twice.
- **Matched findings with different severities take the higher.** Not an average, not the first pass's. It is the combined verdict's max rule applied one level down, at the finding level.
- **Matched findings with different fixes keep both recommendations, each attributed to its pass.** Silently picking one discards the disagreement, and disagreement between two blind reviewers is the most informative thing the second pass produces.

Combined verdict: FAIL if a BLOCKER appears in either pass. The same rule applied to the union of the two finding sets, so one reviewer failing the diff is enough to fail it.

If no second reviewer is available, skip this step and say so in the report. A single-pass review is a complete review; a simulated second opinion — the same reviewer re-reading its own output — is not one, and must never be reported as overlap.

Output:
- per-pass verdicts
- the three finding lists (overlap, unique to each pass), with co-located and cross-referenced pairs kept as separate findings
- combined verdict, or a note that only one pass ran

## Applying fixes to the working tree

Everything above produces a report. When the review is additionally authorized to apply its findings, it does not simply loop over them and edit: an auto-apply loop with no risk tiering and no halt condition is unbounded by construction.

**Classify before applying.** Sort every candidate fix into one of three classes:

- **Free** — mechanically reversible and behavior-preserving: formatting, comments and docstrings, dead-import removal, a rename confined to one file's local scope. Apply without drawing on the budget.
- **Budgeted** — anything that can change behavior: control flow, error handling, concurrency or ordering, resource lifetimes, query shape, serialization and persistence formats. Each one draws down the risk budget.
- **Never auto-applied** — public API or wire-format signatures, security-relevant logic, authentication and authorization decisions, migrations touching existing rows, generated or vendored files. Report these; do not edit them.

This three-class split is this skill's own cut for code review, chosen so each class is decidable at the moment the fix is written, not measured against outcome data. A project may re-cut the classes — but it writes the new cut down before the first auto-apply run, not during one.

**Two stop conditions, both required.** An absolute cap on fixes applied per run, and a ceiling on accumulated budgeted-class risk that halts the run and hands control back to a human when crossed. Either one alone leaks: a cap alone admits a long run of individually cheap structural edits, and a risk ceiling alone admits an unbounded number of free-class edits. Neither value has a measured right answer, so this skill states none — choose both before the first auto-apply run and record them with the project's review configuration, as chosen defaults rather than derived thresholds.

**One fix per commit.** Each applied fix lands as its own atomic commit carrying the finding's ID in the subject, e.g. `fix(review): FINDING-014 <what changed>`. That is what makes a single fix revertible without unwinding the rest of the run, and what lets the final report point at one commit per finding.

**Re-verify each fix as it lands**, not once at the end. Re-run the specific check that surfaced the finding — the failing test, the linter rule, the scan pattern, the reproduction — and record its result with the commit. If that check does not pass afterwards, revert that commit and demote the finding to reported-only. A fix whose check was never re-run is reported as applied-unverified; it is never reported as verified.

**Report the counts separately**, with verified as a breakdown of applied: `12 applied (11 verified, 1 best-effort), 4 deferred`. Deferred covers both the never-auto-applied class and anything a stop condition cut off. A single "fixed N findings" figure hides exactly the distinction the reader needs.

**Before auto-applying anything a scanner or linter flagged**, enumerate the patterns that tool legitimately mislabels and exempt them by name. A scanner's flag/no-flag output is not a fix list. Patterns that get flagged and are frequently correct as written: deliberate fire-and-forget calls, catch-and-log where an uncaught error would take the process down, total error suppression on a shutdown or emergency path, and pass-through wrappers kept for API stability. Record that list with the project's review configuration, next to the stop-condition values and keyed to the scanner it covers. Re-derived from memory each run, it exempts a different set each run, and the exemptions stop being reviewable.

## Common pitfalls

- Treating lint/style nits as blockers.
- Missing security boundaries at request or data layer edges.
- Skipping tests or observability impacts for behavior changes.

## Output contract

Provide the report sections and finding format in `references/output-format.md`.

## Scripts

Commands:
- `scripts/review.sh scan`
- `scripts/review.sh report`

Requirements:
- `git` for diff context (falls back to full repo scan if missing).
- `rg` for faster pattern search (falls back to `find` + `grep`).

Verification:
- Confirm `docs/_docgen/code-review/REPORT.md` was created.
- Confirm the report lists changed files and pattern hits.

## Examples

```
Findings:
- src/auth/session.ts:42 (HIGH): Session cookie lacks HttpOnly/SameSite.
  Risk: cookie theft / CSRF amplification.
  Fix: set HttpOnly=true, SameSite=Lax/Strict, Secure=true in prod; add a test.

Open questions:
- Is this endpoint reachable from public traffic?

Suggested follow-ups:
- Add a regression test for cookie attributes.

Change summary:
- Adds session refresh endpoint for mobile clients.
```

## Resources

- `references/README.md` (index of supporting references)
- `scripts/review.sh` (scan + report wrapper)
