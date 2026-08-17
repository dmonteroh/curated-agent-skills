---
name: delivery-pipeline
description: "Sizes how much process one unit of work deserves using three independent signals, then runs only the phases that size earns, stopping for human approval before code is written and before commit. Use for one sequential change carried from request to commit: a new capability, a behavior change, a defect fix, a refactor, or an MVP bootstrapped from a spec."
metadata:
  category: workflow
---
# Delivery pipeline

Provides a gated procedure for carrying one unit of work from request to commit. Its subject is the sizing decision that comes first — how much ceremony this particular change has earned — and the phase order that decision selects. Ceremony scales to blast radius: a three-line change and a cross-cutting redesign run different subsets of the same pipeline, and the pipeline states which subset before any code is written.

## Use this skill when

- A change request has arrived and the amount of process it deserves is not obvious — the request reads small but touches something load-bearing, or reads large but is mechanical.
- Work should stop for human approval at defined points rather than run to completion autonomously.
- A team wants the same phase order applied to features, tweaks, fixes, refactors, and bootstraps instead of a different improvised sequence per operation.
- An agent has been over-processing small changes (planning documents for a typo) or under-processing large ones (editing a public interface with no plan).

## Do not use this skill when

- **Nobody is available to approve.** Both gates are human stops. An agent that approves its own plan and confirms its own commit has run a different procedure and must not report having run this one. For unattended work, use something whose safety does not rest on a human being present.
- **The question is how to run several workers at once.** This pipeline is strictly sequential: one phase at a time, one handler at a time, with human approval as the only barrier. It carries no rules for partitioning claims between concurrent writers, no barriered verification between agents, and no deterministic merge of parallel outputs. It neither provides those nor substitutes for them.
- **The work is exploratory** — a spike, a throwaway prototype, or a question answered by reading code — and ends with nothing to commit. The pipeline terminates in a commit gate; work that never commits pays for ceremony it cannot use.
- **The task is to review or audit a change someone else produced.** Review here is one phase of producing a change, not a standalone service.
- **The unit is a program, not a change** — a multi-week initiative tracked across many work items. This sizes and runs one unit from request to commit; it is not a work-item tracking system.

## Sizing the work

Score the request on three independent signals, then take the **highest** tier any single signal reaches.

| Tier | Files touched | New dependency or contract | Design ambiguity |
| --- | --- | --- | --- |
| trivial | one file, a few lines | none | none — one obvious way to do it |
| small | one file, one function or unit | none | resolved by reading the code |
| standard | a handful of files, one module | a new internal module or interface | one real choice with live alternatives |
| large | many files, or cross-cutting | a new external dependency, a public API, or a spec document to satisfy | several open questions |

**Highest wins; never average.** The three signals measure different kinds of exposure, and a change can be extreme on one and null on the other two. Averaging or eyeballing a blended impression is what produces the characteristic failure — a one-line edit to an authorization check classified as trivial because two of three signals said so.

**Tie-breaker.** Anything touching a security trigger (below) or a public API or contract is **at least** standard, regardless of file count.

**State the tier in one line before doing anything else**, naming the signal that set it, so the user can override it cheaply:

```
Tier: standard (design ambiguity — two viable storage layouts).
Phases: intake, research, plan [gate], implement, review, commit [gate].
```

The file counts in the table are chosen defaults carried from the source pipeline, not measured thresholds; the same holds for the tier floors in the operations table below. A project may re-cut the bands — but it writes the new cut down before the first run, not during one.

## The phase order

| Phase | trivial | small | standard | large |
| --- | --- | --- | --- | --- |
| 0. Intake — restate the request, name the operation, state the tier | run | run | run | run |
| 1. Research and reuse — look for an existing implementation before writing new code | skip | run | run | run |
| 2. Plan — produce an ordered task list → **Gate 1** | skip | skip | run | run |
| 3. Scaffold — stand up the first end-to-end slice | skip | skip | skip | bootstrap only |
| 4. Implement — one task at a time, test-first per the operation's first move | run | run | run | run |
| 5. Review — read the diff as a reviewer; add a security pass when triggered | run | run | run | run |
| 6. Commit — one commit per logical change → **Gate 2** | run | run | run | run |

**A phase either runs or is skipped.** There is no light research, no informal plan, no quick review. A smaller tier gets fewer phases, never degraded versions of them: an unapproved plan is not a cheaper plan, it is an ungated one. Intake, Implement, Review, and Commit are never skipped at any tier. *(Authored: the source pipeline permitted "light" variants of Research and Plan; this rewrite replaces them with the binary rule.)*

Research order, when the phase runs: the repository's own code first, then the documentation of the dependencies already in use, then published packages, then the open web. Adopting a proven implementation beats writing a new one; the phase exists to make that search happen before the code does, not after.

Research ends in one of four named decisions, recorded: **adopt** an existing implementation as it stands, **extend** one behind a thin wrapper, **compose** a small number of existing pieces, or **build** custom *informed by* what the search found. Naming the decision and the finding that drove it is the phase's artifact; a research phase that ends in "I had a look around" hands Plan and Review nothing they can check.

A channel that could not be checked is reported as unchecked, never as nothing found. If a package registry was unreachable, the repository search covered only the files in view, or a dependency's documentation was not available, name the channel and what it leaves unestablished. "Nothing exists for this" and "I could not look" support different decisions, and only the first one justifies building custom.

Scaffold runs only when no end-to-end path exists yet — bootstrapping from a spec document. Everywhere else the first slice already runs and there is nothing to stand up.

If the work turns out to be larger than its stated tier mid-flight, re-state the tier upward and run the phases the new tier adds. **The tier moves up, never down** — a plan skipped on a trivial reading is owed once the reading is corrected. *(Authored: the source pipeline stated floors but not the direction rule.)*

## The two gates

This pipeline is gated, not autonomous. Two stops, both hard:

1. **Gate 1 — after Plan.** Present the task list. Do not create or edit an implementation file until the user approves it. A violation looks like a source edit with no approval preceding it.
2. **Gate 2 — before Commit.** Present the diff summary and the proposed commit messages. Do not run a commit until the user confirms. A violation looks like a commit whose message the user never saw.

**Everything between the gates flows without stopping.** Asking for approval task by task is not extra safety; it teaches the user to wave through every prompt, including the two that matter.

**When Plan is skipped there is no Gate 1.** Do not simulate one by asking permission to start, and do not treat its absence as license to soften Gate 2 — at trivial and small tiers the commit gate is the only stop the work gets, which is exactly why it is unconditional. *(Authored: sharpened from a parenthetical in the source family.)*

## Operations and first moves

A request routes to exactly one operation. What separates them operationally is what happens to the tests first.

| Operation | Recognize it by | Tier floor | First move | Not this operation when |
| --- | --- | --- | --- | --- |
| add | the capability does not exist in any form | standard | write **new failing tests** for the new behavior, then implement to green | some version of the behavior already runs |
| change | the behavior works but should differ | small | update the **existing tests** to the new spec, then change the implementation until they pass | the current behavior is wrong rather than merely unwanted |
| fix | the behavior is broken: wrong output, an error, a crash | small, often trivial | reproduce the defect as a **new failing regression test**, then fix until it goes green | the behavior matches its spec and the spec is what should change |
| refactor | behavior stays identical, structure improves | standard | confirm the existing tests are **green before** touching code; write no new behavior tests — the existing suite is the safety net | any observable behavior is meant to change |
| bootstrap | a spec or design document must become a running system | large | read the document; extract scope, locked decisions, and the feature list; order into thin vertical slices | a running end-to-end path already exists |

Two of these first moves carry the same distinction from opposite sides: changing the tests first is what separates a tweak from a fix, and proving the defect exists first is what separates a fix from a tweak. Get the operation wrong and the test suite records the wrong story about why the code changed.

A tier floor raises the tier the classifier produced; it never lowers it. A trivial-looking refactor still gets a plan.

**Thin vertical slices.** For a bootstrap, order the task list as slices that run end to end — one request path through every layer it touches, delivering one working behavior — not as horizontal layers. All the models, then all the endpoints, then all the views produces nothing runnable until the last layer lands and defers every integration risk to the end. One end-to-end path first; the second slice is planned in detail only once the first one runs.

## Security escalation

Escalate to a full security review pass whenever the diff touches any of:

1. authentication or authorization
2. handling of user-supplied input
3. database queries
4. file-system paths
5. calls to external APIs
6. cryptography
7. secrets or credentials

This is a list checked against the changed lines, not a judgment about whether a change *feels* security-sensitive — replacing that judgment is the point of the list. It is also what the tie-breaker in *Sizing the work* reads. A triggered diff's Review phase is not complete until the security pass has run.

## Handoff artifacts

The pipeline carries no hidden state — what one phase writes down is the whole of what the next one receives.

- The task list produced at Plan is the single input to Implement. Work not on the list does not get implemented; work that turns out to be needed goes back on the list first.
- Larger work may also emit durable design documents — requirements, architecture, interface design — wherever the repository keeps its docs, per that repository's own conventions.
- Review findings at blocking severity are resolved before Gate 2. The diff presented at Gate 2 is the fixed one, not the original with a list of known problems attached.

## Examples

**A one-line change that is not trivial.** Request: *"make the session cookie expire after 30 days instead of 7."*

- Single-axis reading (file count only): one file, three lines → trivial → straight to implement, review, commit.
- Three-signal reading: files touched says trivial; new contract says none; design ambiguity says none. But the diff touches authentication, so the tie-breaker floors it at standard: research how the session store treats expiry, plan → Gate 1, implement, review plus a security pass, commit → Gate 2.

The signal that decided the tier was not size at all. A ladder with one axis cannot express that, which is why this one has three and a tie-breaker.

**Skipping a phase versus degrading it.** Request: *"the retry count should be 5, not 3."*

- Wrong: *"Small change — I'll sketch a quick plan and start coding."* Plan ran without a gate. The user never approved a plan that nonetheless existed and drove the work.
- Right: *"Tier: small (one function; no new contract; ambiguity resolved by reading the code). Research only. Plan is skipped, so the commit gate is the only stop."* Then update the existing test to expect 5, change the implementation, review, and present the diff at Gate 2.

## Common pitfalls

- Sizing from the request's wording rather than from the change it implies. "Just a quick fix" that rewrites a query layer is not small; "a full redesign" that renames one enum is not large.
- Reading the operation off the request's verb. "Update the export" is a change if the current output is what was asked for and a fix if it is not, and the two start with opposite moves on the test suite.
- Running Review as a formality on work the same agent just wrote, producing no findings on any diff. A review phase that has never returned a finding is not evidence of clean code.

## Verification

Each check names what its failure means and where to return.

1. A tier was stated before any code was written, and the work that followed matched it. If it did not, the classifier read the wrong signals — re-size and re-state.
2. Every phase the tier included produced its artifact, and every phase it excluded produced nothing. A half-written plan means Plan ran degraded, which the phase order forbids.
3. Gate 1 was honored if Plan ran, and Gate 2 was honored unconditionally. An implementation edit or a commit with no preceding approval is a failed run, not a fast one.
4. The security pass ran whenever the diff touched a trigger. If it ran on a diff that touched none, the trigger list was read wrong — check which category was thought to apply.
5. Commits are conventional and each is scoped to one logical change, and changed behavior has tests, per the repository's own testing policy.

## Provenance

- **Numbers.** The only figures here are the sizing bands and the tier floors, both labeled chosen defaults where they are stated. Neither is a measured threshold, and nothing else in the procedure turns on a constant.
- **Dropped.** The source pipeline's closing checklist carried a numeric test-coverage gate imported from a host rule file with no stated basis. It is gone. What survives is the requirement: changed behavior has tests, to whatever standard the repository already sets.
- **Authored.** Three rules are this rewrite's rather than the source's, marked inline where they appear: the run-or-skip rule replacing "light" phase variants, the direction rule for mid-flight re-sizing, and the treatment of a skipped Plan as the absence of Gate 1 rather than an implicit one.
