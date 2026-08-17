---
name: loop-design-check
description: "Designs an autonomous agent loop and reviews an existing one for the ways loops fail: spinning on a goal no machine can settle, gaming the verifier, or running a wrong answer to completion. Gates whether the loop is deserved, pairs a done-criterion with a boundary, picks a control shape and skeleton, and adds damping. Use before building a repeating unattended run, or when one already exists and might run away."
metadata:
  category: ai
---

# Loop Design Check

Provides the judgment layer of an autonomous loop: whether it should exist, what its goal is, and what stops it. A language model is feed-forward — prompt in, tokens out, with nothing that steers toward a goal across turns. Goal-seeking behavior is a property of the loop wrapped around it, so every property that keeps the loop safe is a property of that wrapper's design, decided before it runs.

Feedback splits into two levels, and only one of them can be automated:

| Level | Held by | What it does |
| --- | --- | --- |
| Execution | The machine | Measures distance from the stated goal and grinds it toward zero. The machine is strong here. |
| Judgment | The human | Decides whether the goal is the right goal, whether it should change, and whether to stop. The machine cannot step outside its own loop to question its set point. |

A thermostat drives the room toward whatever number it was given; it cannot decide the number is wrong for someone with a fever. Handing the second level to the machine does not slow the loop down — it removes the only feedback that could have caught a wrong goal, and the loop sprints toward it, quickly and at scale.

## Use this skill when

- A repeating task is about to be handed to an agent that runs it unattended, over and over.
- A loop already exists and there is a worry it spins, cheats its own check, or carries a wrong answer to completion.
- A loop's exit condition is written in words a person would accept and a machine cannot settle.
- The loop's verifier is the same agent that produced the work being verified.
- A loop is about to be moved from run-by-hand to scheduled, and nobody has named what stops it.
- A loop is proposed for work whose failure would be expensive to undo.

## Do not use this skill when

- The task runs once. Wrapping a loop around a one-off adds a failure mode and buys nothing; just do it.
- The schedule fires a fixed action with no goal to converge on and no verdict to reach. There is nothing to make decidable, and no comparator to design.
- A shipped agent already misbehaves and the failing part of its stack is unknown. Locating that is a post-hoc diagnosis over source, configuration, logs, and traces, layer by layer, with an evidence reference per finding — it reads a running system. This skill reads a design and asks whether its goal is settleable and what stops it running away; it does not identify which wrapper layer corrupted an answer.
- The question is how the loop is wired rather than what it aims at. Keeping an unsupervised background process singleton, signalling it safely, and letting it shut itself down when idle is process-lifecycle work and sits elsewhere.
- The question is dispatch inside one orchestrated pass — how to split work across concurrent workers, what each may touch, where verification barriers sit, how outputs merge. That is orchestration, and it is a different problem from whether a repeating run should exist.
- Step 0's gate says do not build one, and the repeated work is really a single deterministic unit that should be written down once and replayed. Promoting a repeated exploration into a replayable unit is a different procedure and the better answer. *(Authored: the source has no such exclusion, and this is the one its own gate most often produces.)*
- The unit of work is one sequential change carried from request to commit with a human approving at defined points. Sizing that ceremony is a delivery-process question, not a loop-design question.

## Action 1 — design a loop

### Step 0. Subtract first: is a loop deserved?

Four conditions, and any miss is a veto:

1. The task recurs often enough that building the loop costs less than doing it by hand for as long as it will run. *(The source fixes a frequency; no derivation is offered for it, so the rule is stated qualitatively here and the threshold left to whoever pays the build cost.)*
2. Verification can be automated. Something other than an opinion has to settle whether a run succeeded.
3. The budget absorbs repeated runs, including the failed ones.
4. The agent holds tools that actually execute and observe results, rather than describing what it would do.

On a miss: do not build a loop. The obstacle is almost never whether a loop can be written — it is whether this repository deserves one. A repository that deserves a loop already has something to reconcile against (a golden sample, an upstream total, a reference output), tests, and a guard that fails on a bad change. A repository that has none of those does not get improved by a loop; its errors get amplified by one.

- Output: the gate result, with each of the four conditions marked met or missed, and the veto stated plainly when one is missed.

### Step 1. Define a machine-settleable goal

The loop lives or dies here. The comparator only works if the exit condition can be answered yes or no by something that is not the agent. A vague criterion produces one of two failures, both silent: the loop never passes and spins, or it passes on a guess.

Five properties, all required:

1. **The done-criterion is machine-verifiable.** One check settles it. "Make it good" is not a criterion; "all unit tests green and a change-list produced" is.
2. **A boundary condition is written alongside it**, naming what the run must *not* do. A done-criterion without a boundary is a licence to reach it by any means, and the agent will.
3. **A fallback exists** — a retry cap, and escalation to a human when it is exceeded.
4. **The goal is layered**, so a partial result is distinguishable from a failure.
5. **Reconciliation beats assertion.** Anchor the criterion to an external fact where one exists — a golden sample, an upstream total, a financial tie-out. "All tests pass" can be gamed by loosening assertions, faking mocks, or swallowing exceptions. A comparison against a reference the agent does not control cannot.

- Check: read the goal to someone who does not know the domain. Can they run one command and say whether it is done? If not, it is not settleable yet, and no amount of prompt work downstream will fix it.
- Output: the done-criterion, its boundary, the retry cap and what happens past it, and the external reference the criterion reconciles against, or an explicit note that none exists.

### Step 2. Pick the control shape

| The task | Control shape | How it stops |
| --- | --- | --- |
| Has a clear done test — write until finished, process a batch | Goal-seeking: converges and terminates | Stops when the goal is reached |
| Has no endpoint; a state must be maintained | Regulating: runs indefinitely, acts only on change, with a dead band so noise does not trigger it | Never stops on its own |
| Samples periodically until a condition holds | Regulating with an exit | Stops when the exit condition holds |
| Must be guaranteed to happen on time | Any of the above, fired by a scheduler | As above; the scheduler owns when it starts |

Getting this wrong produces a specific, recognizable failure: a regulating loop given a terminating goal declares victory and stops maintaining, and a goal-seeking loop given no endpoint runs forever against a criterion it already met.

- Output: the named control shape and, for a regulating loop, the dead band that suppresses noise.

### Step 3. Pick a skeleton

**Maintaining something that already exists — document-driven dispatch.** The loop is not "run a fixed check on a timer"; it is "read a document on a timer and dispatch only where the document changed". The document is simultaneously the queue, the state machine, and the human interface. Three disciplines make it safe:

1. The problem column is human-write-only and the result column is loop-write-only. State advances one way and never rolls back.
2. The exit code is final. If the script says it failed, it failed, whatever the agent's summary says.
3. The loop may advance state no further than "awaiting verification". The cell that says *done* is flipped by a human. The loop is the worker, never the acceptance officer.

**Building something new — three separated roles.**

| Role | Does | The rule that makes it work |
| --- | --- | --- |
| Plan | Breaks the goal into a spec plus acceptance conditions | The acceptance conditions must be script-judgeable |
| Build | Works to the spec | May not edit the acceptance conditions |
| Judge | Runs acceptance independently; pass stops the loop, fail returns the reason to Build | Independent and deterministic |

Three rules, all of which bet on the judge: the judge is not the agent that built the work, because an agent grading its own work inflates the result; the judge decides by deterministic rules — a test run, a reconciliation diff, a type check — never by "looks right"; and Build may not weaken the acceptance conditions to pass them.

- Check: name the actor that flips the final accept. If the answer is the loop, the skeleton is wrong.
- Output: the chosen skeleton with its roles assigned, and for the document-driven form, which columns each party may write.

### Step 4. Add damping

A retry cap, a hard stop, and a human holding the last switch are damping. Negative feedback without damping oscillates: the loop spins in place, burning budget, making and unmaking the same change.

A cap of three attempts before escalation is **this skill's chosen default, not a measured threshold** — pick a different one deliberately if the work argues for it, and write down that it was chosen.

- Output: the retry cap, the hard stop condition, and the named human who holds the final switch.

### Step 5. Land it in three stages

1. **Run it once by hand.** This is what forces an exact statement of how the judge decides, and it is where most undecidable goals are caught.
2. **Harden it into a repeatable definition** that dispatches the roles, still triggered manually.
3. **Put it on a schedule.**

Skipping to stage 3 means the first fully automatic run is also the first run.

- Output: which stage the loop is at, and what has to be true before it advances to the next one.

## Action 2 — review an existing loop

Run the loop past each row. A hit on any one means it will misfire; send it back.

| # | Failure mode | The review question | Antibody |
| --- | --- | --- | --- |
| 1 | The goal is a correct platitude, so the loop spins and burns budget | Can the exit condition be settled yes or no by a machine, or does it say "manage it well"? | Replace with a decidable result condition (Step 1) |
| 2 | Verification is "check whether it looks OK", so the agent confidently declares success | Is the judge the defendant? Does verification rest on impression or on deterministic rules? | External reconciliation, exit-code rules, independent judge |
| 3 | The gate is only "all tests pass", so the agent deletes the tests | Is there a boundary saying what it must not do, or only a done-criterion? | Done-criterion and boundary written together |
| 4 | The design counts on the agent asking mid-run — it will not, and runs a wrong answer to the end | Is there any point where clarification is expected at runtime? | Front-load every clarification and settle it before launch |
| 5 | The standing documents the loop reads are stale or bloated, so the faster it runs the more it errs | Are the documents and notes it depends on fresh, and who maintains them? | An owner, and a periodic check that fails when they rot |

**Three red lines. Violating any one means the loop does not go fully automatic.**

- **Judgment stays with the human.** Acceptance is a human act. The loop may prepare the decision; it does not make it.
- **Responsibility does not transfer.** Anything whose failure the owner could not absorb — merging the wrong change, publishing the wrong thing, moving money — does not get its authority handed over automatically, however good the loop looks.
- **The more a loop rewrites its own rules, the stricter the gate in front of it.** This is the counter-intuitive one. A self-modifying loop needs a *tighter* human review, not a looser one, and the review has to sit before the action: the machine acts faster than anyone can intercept afterwards, so a post-hoc check is a report, not a control.

## Examples

**Reviewing a nightly loop that fixes failing tests.**

The naive design: "run every night and make all tests pass."

| Review row | Result | What it caught |
| --- | --- | --- |
| 1 | Clear | "All tests pass" is machine-settleable |
| 2 | **Hit** | The fixing agent also judged its own fix, so it would pass itself |
| 3 | **Hit** | With no boundary, deleting a failing test satisfies the goal |
| 4 | **Hit** | An ambiguous fix at 2 a.m. becomes a committed guess, not a question |
| 5 | Clear | No standing documents involved |
| Red lines | **Hit** | The design auto-merged |

The repaired design: done-criterion "all tests green **and** no test file deleted or weakened **and** coverage not lowered **and** a change-list produced"; goal-seeking shape with a retry cap; the judge is the continuous-integration run, not the fixing agent; ambiguous fixes are left for the human rather than guessed; the loop opens a change for review and does not merge it.

The two designs differ by four lines of constraint. That is the difference between waking to a clean proposed change and waking to a deleted test suite.

## Output contract

For a design, returns: the Step 0 gate result with each condition marked; the done-criterion and its boundary; the retry cap, the escalation path, and the named human holding the final switch; the control shape; the skeleton with roles assigned and the acceptance-flipping actor named; the external reference the criterion reconciles against, or a statement that none exists; and the rollout stage the loop may start at.

For a review, returns: each of the five failure modes marked hit or clear **with the evidence that settled it**, each red line marked, and one verdict — cleared for automation, or sent back with the specific repairs named. A row marked clear with no evidence is an opinion; state it as unassessed instead. *(Authored: the source gives the checklist but no report shape, so a review could return a feeling.)*

## Provenance

- **Sourced:** the feed-forward premise and the two-level feedback split; the four-condition build gate; the five-property goal framework including reconciliation over assertion; control-shape selection; both skeletons with their disciplines and role rules; damping; the three-stage rollout; the five failure modes with their antibodies; the three red lines; and the nightly-test worked example.
- **Attributed, unverified:** the source credits the execution-versus-judgment split to Norbert Wiener, *The Human Use of Human Beings* (1950). Carried as attribution only — it has not been checked against the book here. The source also credits its three-role pattern to two informal write-ups it does not locate; those are not carried.
- **Authored:** the exclusion for repeated work that is really one deterministic unit, and the requirement that a review cite evidence per row and mark an unevidenced row unassessed — both marked where they appear. Every `Check:` and `Output:` line under a step is authored as well: the source states each step but names no artifact it has to leave behind, so a step could be satisfied by agreeing with it.
- **Numbers:** a retry cap of three is a chosen default, labelled where it appears. The source's minimum recurrence frequency is not carried, because it had no derivation; the rule is stated qualitatively instead. No figure in this procedure is measured.
