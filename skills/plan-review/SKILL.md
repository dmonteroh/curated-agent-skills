---
name: plan-review
description: "Reviews an implementation plan before any code is written: confirm the target, require alternatives beside the plan, set a scope posture (expand, cherry-pick, hold, cut), then audit architecture, code quality, tests, and performance. Every finding carries a confidence score and a quoted line of evidence, or it is suppressed."
metadata:
  category: architecture
---
# plan-review

Provides a plan-stage review of work that has not started yet. The artifact under review is a plan, design doc, or spec; the product is a posture decision, an approved implementation approach, findings scored for confidence and backed by quoted evidence, and a review report written as the plan's final section.

## Use this skill when

- An implementation plan, design doc, or spec is about to be handed to implementation.
- A plan exists and its scope is the open question — too small, too large, or never examined.
- The review must produce decisions the user signs off on, not a list of opinions dropped at the end.
- Past reviews on this codebase produced findings that turned out not to be real, and false positives need a mechanical gate rather than more care.

## Do not use this skill when

- The code already exists and the question is whether the diff is correct. This audits a plan; written code needs a code review.
- No plan exists yet and the work is still ambiguous. Deciding what to build is a different job from auditing a decision already made.
- The change is a one-line fix, a mechanical rename, or a config bump with no design content: the posture gate and four sections produce noise around a change that has no architecture.
- The repository the plan targets cannot be read. Every finding here needs a quoted line from the source it is about, so with no source access every finding lands in the suppressed band. Say that and stop, rather than emitting a review made entirely of unverifiable findings. (Authored; see Provenance.)
- The approach is already settled by someone with the authority to settle it and only execution is wanted. The alternatives step will stall the session — say so instead of running it hollow.

## Required inputs

- The plan under review, named explicitly: a file path, a pasted document, or a specific branch.
- Read access to the code the plan changes. Findings are gated on quoting it.
- Who decides. The review stops for approval repeatedly and cannot proceed on its own judgment.

## Workflow

### 1) Fix the target before reading anything

Name the artifact under review before the first repository read, search, or command. When several candidates exist — a design doc, a drafted plan, and a branch of work in progress — ask which one, and do not explore to decide. Whatever gets read first anchors the review, so an unconfirmed target quietly chooses the review's subject.

### 2) Alternatives — the plan is one option, not the option

Run this before the posture and before any section. Treat the plan under review as Approach A (authored framing; see Provenance) and produce at least two more:

- one **minimal viable** — the fewest files and smallest diff that still achieves the stated outcome;
- one **ideal architecture** — the best long-term trajectory, regardless of diff size;
- a third when a meaningfully different framing of the problem exists.

Give each approach a summary, effort, risk, pros, cons, and what existing code or infrastructure it reuses.

- Minimal and ideal carry equal weight. Do not default to minimal because it is smaller, or to the plan because it is written.
- When only one approach is genuinely available, name each alternative considered and the concrete reason it was eliminated. "No alternatives" without that list is a skipped step, not a finding.
- Stop for an explicit choice. An approach that obviously wins is still a decision the user makes, and an obvious winner is exactly where the review is most likely to be wrong about what the user values.

### 3) Scope posture — pick one, then commit to it

| Posture | Default when | What the review does | Ambition check | Expansions |
| --- | --- | --- | --- | --- |
| **Expansion** | Greenfield feature or new surface | Push scope up: describe the version that is far more valuable for modestly more effort, and the ideal a user would feel | Mandatory | Each proposed individually, opted into individually |
| **Selective** | Enhancement of an existing system | Hold the current scope as the baseline and make it bulletproof; surface expansion opportunities separately as candidates | Surfaced, not pushed | Presented for cherry-picking, neutral posture |
| **Hold** | Bug fix, hotfix, refactor | Scope is accepted; spend the whole review on failure modes, edge cases, observability, and rollback | Not run | None surfaced |
| **Reduction** | The plan is overbuilt | Find the minimum that achieves the core outcome; everything else is deferred, explicitly | Not run | None surfaced |

Depth follows the posture. Under expansion and selective, error mapping and observability are held to "would this be a joy to operate"; under hold, to "can this be debugged from logs alone"; under reduction, to "can anyone tell when it breaks".

Two rules bind every posture:

- **Commit.** Once a posture is chosen, execute it. Do not argue for less work during later sections under expansion, and do not slip scope back in under reduction. Raise the concern once, here.
- **Sovereignty.** Every scope change is an explicit opt-in. Never silently add or remove scope — an item the user never ruled on is unresolved, not decided.

Complexity signal: a plan touching more than 8 files or introducing more than 2 new classes or services (chosen defaults; see Provenance) is a smell. Stop before any section, name what is overbuilt, and propose a smaller version that still achieves the core goal.

### 4) The four sections, in order

Architecture → Code Quality → Tests → Performance. Three rules govern all four:

- **Never skip one.** "This is a strategy document, so the implementation sections do not apply" is always wrong — implementation detail is where a strategy breaks. A section with nothing in it reports "no issues found" after being evaluated, never instead of being evaluated.
- **Stop after each section.** Walk the user through findings one at a time and wait for the decision before the next section.
- **The plan file is the review's output, not a substitute for it.** Writing every finding into a single edit and declaring the review complete is the failure this rule exists to prevent: the findings were produced, the decisions never were.

**Architecture** — component boundaries and the dependency graph before and after; every new data flow traced along four paths (happy, missing input, empty input, upstream failure); a state machine for each new stateful object, including the transitions that must be impossible and what prevents them; single points of failure and what breaks first under an order-of-magnitude more load; auth boundaries and who can call each new entry point; rollback posture — what the procedure is if this ships and immediately breaks; distribution — a new artifact type (binary, package, image) with no build-and-publish path in the plan is a finding, not an implementation detail.

**Code quality** — organization against the patterns already in the codebase, and a stated reason for each deviation; repetition, flagged aggressively with the file and line that already does it; naming that says what a thing does rather than how; error-handling patterns, with catch-all handling named as a smell and each caught error given a specific class, a rescue action, and something the user sees; abstractions solving a problem that does not exist yet; fragile code assuming the happy path; any new method branching more than five times (chosen default) proposed for refactor.

**Tests** — trace every codepath the plan introduces, then map the user flows and the error states a person actually sees: double submission, navigating away mid-operation, a stale session, a slow network, zero results, very large result sets, a batch job failing partway through. Check each branch and each flow against the tests that exist today and produce a coverage map marking every one tested or a gap. Rate what exists rather than counting it: behavior with edge and error cases, happy path only, or a smoke check that would pass no matter what the code did. Mark flows spanning several services or processes as needing an integration test rather than a unit test, and changes to prompts or model-facing instructions as needing an output-quality evaluation rather than an assertion. One exception to the stop-and-ask loop: where the plan changes behavior existing callers depend on and no test covers that path, the regression test is added to the plan without asking.

**Performance** — repeated per-row queries and missing indexes on every new access path; the maximum production size of each new data structure; caching for expensive computations and external calls; the slowest new codepaths and their expected worst case; pressure on connection and worker pools.

### 5) Confidence, and the gate that has to pass before a finding is emitted

Every finding carries a confidence score from 1 to 10, written into the finding, and the score decides whether the user ever sees it:

| Confidence | Meaning | Effect |
| --- | --- | --- |
| 9-10 | Verified by reading the source; a concrete defect, demonstrated | Reported normally |
| 7-8 | Strong pattern match, very likely correct | Reported normally |
| 5-6 | Plausible, could be a false positive | Reported with a caveat naming what would confirm it |
| 3-4 | Suspicious pattern that may be fine | Suppressed from the report, kept in the appendix |
| 1-2 | Speculation | Dropped unless the severity would be the highest on the scale |

Band boundaries are chosen defaults (see Provenance). The mechanism is the point: a scale whose low bands remove a finding from the report instead of decorating it with hedged language.

Finding format: `[SEVERITY] (confidence: N/10) file:line — description`

**The gate.** Before a finding is promoted to the report, quote the verbatim line or lines that motivate it, each with its file and line number. If the finding is "this field does not exist on that model", quote the body of the model where it would be declared. If it is "this lookup can return nothing", quote where the structure is initialized. If it is "these two paths can race", quote both.

If the motivating lines cannot be quoted, the finding is unverified: drop its confidence into the suppressed band and send it to the appendix. Do not route around this by assigning a 7 to a finding that could not be quoted — that defeats the only mechanism here that can actually fail.

**Framework-generated symbols.** Where a symbol is created by a framework rather than written in a class body — ORM model metadata, a migration, a decorator, a schema file, a generated client — quote the construct that creates it. The bar is "I read the source that creates this symbol", never "I searched for the name and did not find it."

The gate exists for one family of false positives, all of the same shape — a claim that something is absent, made from a search rather than from reading:

| Claimed finding | What quoting forces |
| --- | --- |
| "field does not exist on this model" | Quoting the class body or its metadata block, where the field's presence or absence becomes visible |
| "this lookup may return nothing" | Quoting the initialization, which often guarantees the key |
| "saving here may lose fields" | Quoting the persistence signature or model definition |
| "this update may miss an attribute" | Quoting the attribute set, which settles it either way |

**Calibration.** A suppressed finding the user then confirms as real is a calibration signal, not a win: record what evidence would have made it quotable, so the same shape of finding clears the gate next time rather than being suppressed again.

## Output contract

The review produces, in the conversation and then in the plan file:

- The posture and the approved approach, each named with the decision the user made.
- Findings per section: severity, confidence, quoted evidence, and the decision taken on each.
- A suppressed appendix listing every finding the gate demoted, with its score. Deleting it hides the gate's own error rate and makes the calibration unauditable.
- **NOT in scope** — everything considered and deliberately deferred, one line of rationale each. Deferred distribution or observability work is listed here explicitly rather than dropped silently.
- **What already exists** — the code and flows that already solve part of the problem, and whether the plan reuses or rebuilds each.
- The coverage map, with every gap marked.
- **Unresolved decisions** — every question the user did not answer. Never default one to its recommendation; an unanswered question is an output of the review.

Write the report as the plan file's final section and record the commit the review ran against. A later reader compares that commit with the current head — `git rev-list --count <reviewed-commit>..HEAD` — to see how far the plan has moved since. A stale review is worse than no review, because it reads as clearance. The report's last line is either the unresolved-decisions list or an explicit statement that there are none; an absent line is indistinguishable from a review that never asked anything.

## Common pitfalls

- Emitting a finding at a confidence high enough to display when its motivating line was never quoted.
- Holding every finding until the end and delivering them as one document. That is a report, not a review; the decisions never happened.
- Skipping a section because of the plan's genre.
- Letting the posture drift: arguing for less work under expansion, or adding scope back under reduction.
- Presenting the plan as the only implementable option because it is the one already written down.
- Dropping the suppressed appendix to make the review look cleaner.
- Treating an unanswered question as agreement.

## Examples

Passes the gate — the evidence is quoted, so it reports normally:

```
[P1] (confidence: 9/10) billing/charge.py:88 — the retry wrapper swallows the
timeout and returns nothing; the caller reads that as "no charge due" and marks
the invoice paid.
Evidence:
  billing/charge.py:88    except TimeoutError: return None
  billing/invoice.py:41   if charge is None: mark_paid(invoice)
```

Fails the gate — same suspicion, no quotable line, so it is demoted rather than shown:

```
[P1 → suppressed] (confidence: 4/10) billing/models.py — "the plan writes
settled_at, which does not exist on Invoice".
Evidence: none. The attribute is absent from the class body, but this model's
columns are declared in migrations that were not read.
Appendix only. Reading the migration directory either promotes this to 9/10 or
deletes it.
```

## Provenance

- The confidence bands, the suppression thresholds, and the complexity signals (8 files, 2 new classes or services, 5 branches per method) are chosen defaults carried from the source material. None is backed by measurement here. Tune or replace them per project; do not read them as calibrated.
- The false-positive family in the gate table is the one the source material reports the gate catching. The source's claim to have measured it on a specific project is not reproduced.
- Authored rather than sourced: the stand-down rule for a target repository that cannot be read, and the framing of the plan under review as Approach A within the alternatives step.
