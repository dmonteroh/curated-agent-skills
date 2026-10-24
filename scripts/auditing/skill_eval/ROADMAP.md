# Agent evaluation suite: where it stands and what comes next

Written 2026-10-07 for the operator. Sources: `scripts/auditing/skill_eval/` (README, DESIGN, PERFORMANCE, REPLACEMENT-BRIEF), `tmp/skill-eval-build/BOARD.md` and `CONTINUATION.md`, `tmp/eval-rollout/STATUS.md` and the five task-quality run records under `~/.cache/skill-eval/runs/20261005T17*`–`19*`, `tmp/testing-overhaul/PLAN.md`, and the recovered writing-style campaign in `tmp/writing-style-recovery/out/files/` (README, LEARNINGS, TEST-PLAN, COMPLETION-PLAN, CALIBRATION, `measure/README.md`, `measure/claims.md`). Fact means read in a file or a run record. Inference means judgement.

Paths under `tmp/` and `~/.cache/skill-eval/`, and learned-rule ids, name local working files and memory that are not committed. They are kept as provenance. The `testing` brief that §7 step 10 points to is [TESTING-REBUILD.md](TESTING-REBUILD.md).

## 1. Short answer

The isolation, activation, and corpus layers are built and have run on the whole library. The task-quality layer exists as a runner but has produced no usable verdict yet: five skills, two tasks each, three repeats, and every result sits inside the noise. The runner is generic. It lacks the per-skill precision of the writing-style campaign. That campaign had claims written before the runs, a verdict per claim, harm probes, calibrated difficulty, enough trials, and a rule for what to rerun after an edit.

The proposal is one generic protocol that evaluates every skill, with a per-skill eval card. The card holds the claims that no mechanical check can confirm, the tasks that probe them, and a map from skill files to the claims they affect. Setup per skill is work to schedule, never a reason to exclude a skill (operator decision, 2026-10-07). A full evaluation costs up to 100 agent calls, so it runs when the operator picks a skill to fix, never across the whole list. During the fix, a planner reads each diff and reruns only the claims that diff invalidates.

## 2. Where each layer stands

| Layer | What it answers | Built | Run on the library | Gap |
| --- | --- | --- | --- | --- |
| Isolation (`vendors.py`, `trace.py`) | Is an arm, judge, or generator running in a polluted environment? | Yes, three review rounds, 555 tests at the build close (fact, BOARD) | Every run | Arms can still read any path, detection is a trace heuristic. Codex has no visible-skill list (fact, README "Known limits") |
| Corpus (`cases.py`) | Is the trigger-case set good enough to measure anything? | Yes | All 96 files: 246 lint errors repaired to 0 (fact, BOARD 2026-10-05) | `monitoring-expert` was split after the sweep, so the corpus now covers 97 skills and the status table 96 (fact: 97 skill folders, 98 trigger-case entries incl. README) |
| Integrity (`integrity.py`) | Has a skill absorbed its own evaluation material? | Yes, 0.6 s over the library | Yes | Not wired into `audit-skills.sh`. Operator decision R7 |
| Activation selftest | Does the description load the skill, and stop loading it under an unrelated one? | Yes | 93 of 96 pass on both vendors. Fails: `monitoring-expert` (both), `research-discipline` (Claude), `sys1-mcp` (Claude) (fact, STATUS) | 1 repeat, 3 cases per vendor. It proves the detector works, not that the description is good |
| Activation run plus sealed holdout | How often does the description load on prompts it never saw? | Yes, with a look budget of 3 per description | Holdouts sealed for 95 of 96. Only `sys1-mcp` has a holdout measurement (fact) | `writing-style` has no holdout: its negatives are an open operator decision |
| Task quality (`performance run`) | What changes in the work with and without the skill? | Yes: paired arms, objective checks, hidden assertions, blind cross-vendor pairwise judge, budget guards | 5 skills: code-review, pr-description, smart-conventional-commits, root-cause-debugging, testing | Everything in §3 and §4 |

## 3. What the five task-quality runs show

Fact, from `tmp/eval-rollout/compile_perf.py` over the saved runs. Each row is one vendor and task at 3 valid pairs.

| Skill | Objective check delta | Assertion delta | Pairwise preference |
| --- | --- | --- | --- |
| code-review | 0.00 on 3 of 4 rows, −0.17 on one | −0.07 to +0.13 | Claude favours with, Codex split |
| pr-description | 0.00 on 3 of 4 rows, −0.17 on one | +0.10 to +0.40 | Claude: without 5, with 0 |
| smart-conventional-commits | 0.00 on 3 of 4 rows, −0.33 on one | −1.00 to 0.00 | Split |
| root-cause-debugging | 0.00 on all rows | −0.11 to +0.33 | Mostly with, small n |
| testing | 0.00 on all rows, mutation kill ratio 1.00 vs 0.96 and 0.83 vs 0.83 | −0.17 to 0.00 | Mostly without on discount-tests |

Four readings follow.

1. **The tasks sit at their ceiling** (fact for checks, inference for cause). Objective checks almost never separate the arms, because both arms pass. `testing` scores 75 to 100% kill rate with and without the skill (fact, `testing-overhaul/PLAN.md`). A task both arms pass cannot show a skill's value.
2. **Six pairs per vendor cannot rank anything** (fact plus inference). The writing-style campaign set the floor at four trials across five probes for close variants, after three-trial screens pointed the wrong way three times (fact, LEARNINGS §6). These runs are two tasks at three trials.
3. **The generic pairwise judge disagrees with the assertions** (fact for the numbers, inference for the cause). On pr-description with Claude, assertions moved +0.10 in the skill's favour while the judge preferred the without arm 5 to 0. An unanchored "which is better" judge measures something other than the requirements, plausibly length or format taste. It cannot be the headline number.
4. **Several assertions came back unsupported** (fact: 1 to 5 per row on six rows). The judge could not quote evidence, so those requirements were never scored.

None of this is a verdict on the five skills. The runs show that the runner works end to end and that the suites are too easy and too small.

## 4. What the writing-style campaign had that the suite lacks

The writing-style campaign ran 1,645 agent runs (fact, README) and found every shipped defect by running, none by reading (fact, LEARNINGS §6). These are its mechanisms that `performance run` does not yet have.

| Mechanism in the campaign | Source | State in `skill_eval` |
| --- | --- | --- |
| Claim rubrics written before the runs. A claim present in the without arm is baseline, and the skill earns nothing for it | `measure/claims.md` | Partial. Hidden assertions exist, but there is no claim object and no per-claim verdict. The summary is per task |
| A verdict per band, never one per skill ("baseline on four bands and differentiates on a fifth") | `measure/README.md` "Reading a result" | Missing |
| Harm probes: an already-clean input left alone (H2), quoted material kept byte for byte (H3), a stand-down on out-of-scope work (W6) | `claims.md` T3, W6 | Possible through assertions, but no convention or task kind requires one |
| Gate-run rate: did the agent execute the skill's script | LEARNINGS §3: "the single most vendor- and tier-shaped behavior in the whole campaign" | Missing. The trace records tool calls, but no metric counts calls to `skills/<name>/scripts/` |
| Cost as half of every claim (the hard gate cost about double per deliverable) | LEARNINGS §6 | Partial. Run totals only, no per-arm cost delta |
| Offline re-scoring of stored outputs after a scorer change (`score.sh <tag>`, free) | COMPLETION-PLAN §0 | Missing. `performance report` rebuilds the summary but does not rerun command checks |
| Variant arms: body A/B, block A/B, component ablation | `run-body.sh`, `run-ab.sh` | Missing for task quality (`--description-file` exists for activation). `testing-overhaul/PLAN.md` asks for `--variant NAME=DIR` |
| An invalidation table: which file change invalidates which numbers, and which command restores them | COMPLETION-PLAN §0 | Missing. This is the mechanism that makes the suite measured instead of a sweep |
| Screen nominates, floor confirms | LEARNINGS §6 | Missing as a mode. Repeats are a flag with no screen/confirm distinction |
| A scorer validated against planted good and bad outputs before it is trusted | TEST-PLAN ("mutation run reported 9 survivors"), suites README rule | A written rule in the suites README, not enforced by tooling |
| Multi-turn sessions, chat surface, instruction-file arm, persistence | `run-depth.sh`, `run-chat.sh`, `run-persist.sh` | Out of scope by design (PERFORMANCE.md). Inference: only always-on skills need these, and writing-style is the only one in the library |
| Calibration of a rule against accepted prose and several pre-LLM registers | CALIBRATION.md | Specific to writing-style's linter. Not a suite feature |

One tension needs a ruling. The suites README says a requirement copied from the skill grades compliance, not quality (DESIGN T-B). LEARNINGS §6 says the scorer must encode the skill's own contracts, or it measures a different skill. Both are right about different things (inference).

The proposed resolution: a claim states a reader-visible outcome that a user would want without having seen the skill, for example "the hedge in the source survives in the output". The skill's procedure words never enter a claim. Carve-outs, such as reply versus deliverable in writing-style, belong in the scorer, because they decide what counts as the output. Task prompts and fixtures stay written by someone who has not read the skill. Both arms are graded on the same claims, so a claim the baseline already meets scores zero.

## 5. Proposal: one protocol, one eval card per skill

### 5.1 The eval card

The card extends the existing suite JSON (`version: 2`) in `scripts/auditing/suites/<skill>.json`. It adds three things to the task list that exists today.

- **Claims.** Each claim has an id, a band, a one-line outcome statement, and the `SKILL.md` section or script it rests on. It also names its measurement: an objective check, a scorer metric with a direction, a hidden assertion, or a trace metric such as gate-run rate. A task lists the claims it probes.
- **Task kinds.** `deliverable` probes a claim. `harm` gives an input the skill must leave alone or must not over-apply to. `stand-down` gives a near-miss request where the correct behaviour is to decline the skill's procedure. Every card carries at least one `harm` or `stand-down` task (chosen default).
- **Invalidation map.** Skill paths mapped to the claims they affect, with `description` mapped to activation. This generalises writing-style's COMPLETION-PLAN §0 table from a document to data the tooling reads.

### 5.2 Generic measurements every card gets for free

These need no per-skill authoring and apply to any skill.

| Measurement | How |
| --- | --- |
| Activation in natural mode | Exists (`--mode natural`) |
| Gate-run rate, for skills that ship scripts | New trace metric: calls that execute a path under the installed skill's `scripts/` |
| Cost delta per arm | New: Claude dollars and Codex tokens per arm, never converted |
| Cross-vendor shape agreement | New summary line: do the two vendors' with-arms move in the same direction per claim. Inference: this would have caught the `tutorial-engineer` contradiction, where the two vendors emitted opposite document shapes (learned rule 2026-08-22) |
| Position bias and judge flip rate | Exists |

### 5.3 Precision rules the runner enforces

1. **Pre-registration.** Claims, assertions, and control markers are hashed into `plan.json` and frozen before the first arm runs.
2. **Calibrate before measuring.** A `--calibrate` pass runs the without arm only, at low n. A task whose without arm already passes every check for a claim is flagged as at ceiling for that claim, and the runner refuses to score that claim until the task is hardened.
3. **Spend where the answer is still open.** The first half of the budget runs every task once per vendor. The second half goes only to claims whose interval still straddles the without arm's rate. A claim decided early stops spending. §6.2 gives the sizes.
4. **Validated scorers.** Each check and scorer ships with a planted good output and a planted bad one. `suite validate` (free) runs them and refuses a suite whose check passes the bad one or fails the good one.
5. **Pairwise preference is secondary.** It is reported, but a verdict rests on claims. Inference from §3: an unanchored preference contradicted the assertions on pr-description.
6. **Sealed task holdout for the final measurement.** The same mechanism as activation holdouts: a second task set, sealed, measured once at the end of a fix, with a look budget.
7. **One judge call grades every claim.** Today `judge.grade` makes one call per assertion per output (fact, `judge.py:545`), so five assertions cost ten judge calls per pair before the pairwise comparison. A batched grade sees both outputs under opaque labels, grades every claim in one call, and runs in both orders. Each verdict still needs a quotation that passes the mechanical check.

### 5.4 Verdicts

The verdict is per claim and vendor. STRONG means the with-arm is better on both vendors and the interval excludes zero at confirm size. The others are BASELINE (the without arm already meets it), WEAK (no reliable difference), HARM (with-arm worse), UNMEASURED (ceiling, unsupported evidence, or screen only). A skill's report is the table of claims, never a single word. This matches the per-band verdict the writing-style harness used and the `DIFFERENTIATION: STRONG|WEAK` line the review pipeline already reports.

## 6. One protocol for every skill, run on demand

Operator decision, 2026-10-07: one generic protocol must evaluate every skill correctly. Per-skill setup is work to do, never a reason to exclude a skill. A full evaluation costs 10 to 100 agent calls, so it runs to fix or settle a particular skill, never across the whole list.

Agent evaluation fills the gaps mechanical checks cannot see. Anything `audit-skills.sh`, `cases lint`, `integrity scan`, or a skill's own unit tests can establish is never re-measured with agents.

### 6.1 What runs when

| Layer | Scope | When |
| --- | --- | --- |
| Mechanical | Every skill | Every change, every audit. Free |
| Card setup | One skill | Once, before its first full evaluation (§6.3) |
| Full evaluation | One skill | The operator picks the skill to fix or settle |
| Rerun of invalidated claims | One skill | After each edit during a fix, chosen by the planner (§6.4) |
| Final measurement on sealed tasks | One skill | Once, when the fix is done |

### 6.2 The call budget of a full evaluation

Objective checks and scorers cost no calls. With the batched judge (§5.3 rule 7), one pair costs 2 arm calls and 2 judge calls.

| Stage | Size | Calls |
| --- | --- | --- |
| Activation on the sealed holdout | about 10 cases × 2 vendors | about 20 |
| Task quality | 5 tasks × 2 repeats × 2 vendors = 20 pairs | 80 |
| Total | | about 100 |

What 20 pairs can and cannot decide (fact: Wilson 95% intervals from `common.wilson_interval`). A claim met 18 of 20 times with the skill, [0.70, 0.97], against 6 of 20 without, [0.15, 0.52], separates. A claim met 14 of 20 times, [0.48, 0.85], against 10 of 20, [0.30, 0.70], does not. Per vendor at 10 pairs, even 9 against 3 only touches: [0.60, 0.98] against [0.11, 0.60]. Inference: the budget decides large effects pooled across vendors. It cannot rank two close body variants. That needs the writing-style floor, four trials across five probes per vendor, spent only on the claims in question during a fix.

Today's runner spends more than this per pair. The Claude pr-description run made 85 calls for 6 pairs: 1 baseline, 12 arm calls, and 72 judge calls (fact, `plan.json` of run `20261005T181416Z`). The judge spent 85% of the calls, because each assertion costs a judge call per output.

A fix costs one full evaluation, then one rerun of the invalidated claims per edit, then one final measurement. Inference: a typical fix lands between 150 and 300 calls.

### 6.3 Card setup: the work that makes it precise

Setup is a pipeline with separated readers, so the evaluation cannot learn the skill's words (DESIGN T-B).

1. **Archetype.** Classify the skill (§6.5). The archetype fixes the fixture kind, the scorers, and any runner support it needs.
2. **Claims.** An agent that reads the skill lists its claims as reader-visible outcomes, each with the section it rests on. The operator approves the list. It is the specification of what the skill promises.
3. **Tasks.** An agent that never reads the skill receives the approved claims and a one-line job. It writes task prompts, fixtures with planted ground truth, and hidden assertions, including at least one harm or stand-down task. Half the tasks are sealed as the holdout.
4. **Scorer validation.** Every check and scorer passes a planted good output and fails a planted bad one (`suite validate`, free).
5. **Calibration.** The without arm runs each visible task once per vendor, about 10 calls. A task the without arm already passes for a claim is hardened or replaced.

Setup calls are authoring calls. They are spent once per card and stay separate from the evaluation budget.

### 6.4 The planner

`skill-eval.py plan --since REF` reads `git diff REF`, maps each changed skill file through the card's invalidation map, and prints the runs required with their call estimates. It runs nothing itself. The same mapping drives a `--claims` filter on `performance run`. This turns writing-style's "standing loop after any body change" into a command, with the blast radius stated by data instead of memory. One caution from the campaign applies: a body edit is never surface-local (fact, `memory/writing-style-harness.md`), so any `SKILL.md` body section maps to every behavioural claim by default. A card narrows that only with evidence.

### 6.5 Archetypes the protocol must cover

The protocol stays one protocol. What varies is the ground truth a card can build and the runner support it needs. Skill placement below is inference from names and descriptions, to be settled in step 1 of each card's setup.

| Archetype | Examples | Ground truth | Runner support today |
| --- | --- | --- | --- |
| Deliverable from a repository | pr-description, smart-conventional-commits, changelog-automation, doc-sync | Collected artifacts and objective checks | Yes |
| Code change | testing, refactor-clean, root-cause-debugging, performance | Fixture tests, mutation kill rate, behaviour-preserving rewrites | Yes, with a scorer per task |
| Review or audit | code-review, security-auditor, architect-review, plan-review, production-audit | Recall of planted defects and a false-positive count | Yes, once fixtures carry planted defects |
| Advisory design | backend-architect, cloud-architect, brainstorming, subagent-orchestrator | Trap scenarios with one decisive constraint, plus judged claims | Yes, through the judge |
| Tool or environment bound | terraform-engineer, grafana-dashboards, postgresql-engineering, office-files, pdf-files, ui-visual-validator, sys1-mcp, mcp-server-development | The tool run on the artifact: validate, parse, render, query | Partial. No binary artifacts, no per-card tools in the arm, no per-card MCP server |
| Always-on or conversational | writing-style | Per-turn scoring across a session, with an instruction-file arm | No. Needs multi-turn sessions |

Advisory design is where precision is hardest (inference). A judge grading open advice is the weakest ground truth in the table. The trap scenario is what makes it decidable. The subagent-orchestrator trap (two "independent" tasks that collide on one table and one port) separated the stale skill, the current skill, and no skill on both vendors (fact, `tmp/subagent-orchestrator-eval/RESULT.md` §2). Every advisory card needs at least one such trap.

## 7. Build order

Steps 1 to 7 are tooling with unit tests and no vendor calls. Steps 1 to 6 landed on 2026-10-07 in commits `818c24d`, `b147955`, and `0070774`. The planner shipped as `performance plan` rather than a top-level `plan` command.

1. ~~Suite `version: 2`: claims, task kinds, invalidation map, with v1 still accepted.~~ Done: `load_card`, plus a required `harm` or `stand-down` task.
2. ~~`suite validate` with planted good and bad outputs.~~ Done: `performance validate`. Not yet run over the five existing suites, because they are version 1 and carry no planted outputs (D5).
3. ~~Batched judge.~~ Done: `judge.compare_and_grade`, the default (`--grading batched`). Two judge calls per pair, so a pair costs four calls.
4. ~~`performance rescore RUN_DIR`.~~ Done. Rescoring a copy of the October 5 `testing` run reproduced its kill ratios exactly.
5. ~~Trace metrics and per-claim verdicts.~~ Done: `script_runs` in the trace, cost per arm, and a claim table per vendor and pooled with vendor agreement.
6. ~~Adaptive allocation, `plan --since REF`, and `--claims`.~~ Done. Checked on real history: the sys1-mcp body-only commit invalidates no activation, and the research-discipline description commit does.
7. ~~Card setup commands.~~ Done on 2026-10-07 (`665ff73`): `card draft`, or `card claims`, `card tasks`, and `card assemble` one stage at a time. Assembly drops checks that cannot fail and records every drop. Added beside it (`e43fada`): `usage scan`, which reads saved transcripts and reports what followed each load of a skill. Its `usage-notes.txt` feeds `card tasks --usage-notes`, so tasks can mirror real use. Not yet run live: `card draft` costs 2 calls per skill.
8. `--calibrate` (without arm only). This is the first step that spends.
9. Sealed task holdout with a look budget, and `--variant NAME=DIR` for body A/B and ablation.
10. Pilot one skill per archetype that the runner already supports. `testing` goes first, following [TESTING-REBUILD.md](TESTING-REBUILD.md).
11. Runner support for the remaining archetypes: binary artifacts and per-card tools, per-card MCP servers, then multi-turn sessions with an instruction-file arm. Until the last one lands, writing-style keeps its harness in `tmp/writing-style-skill/measure/` (REPLACEMENT-BRIEF R8).

Found while building, not yet acted on. On the rescored `testing` run, the Codex with-skill arm used about 3.2 times the uncached input (26,860 against 8,329 tokens). It used 2.6 times the output (3,920 against 1,484). Both are facts from the cost split in `5ec9c0c`. An earlier reading of 4.3 times counted cached input, which is billed at a discount. The extra work is the skill's step to prove each new test can fail. Those two tasks could not reward it, since the no-skill tests already killed the mutants. Old runs show skill script runs as "not recorded", since their traces predate the field.

## 8. Decisions for the operator

| # | Question | Evidence or default |
| --- | --- | --- |
| D1 | ~~Which skills get an eval card~~ Decided 2026-10-07: every skill can, and a full evaluation runs on demand for a skill being fixed, at 10 to 100 calls | Operator, this session |
| D2 | Claims may state outcomes the skill promises, as long as they never use the skill's procedure words, and carve-outs live in scorers (§4 tension) | The suites README rule and LEARNINGS §6 conflict as written |
| D3 | Pairwise preference becomes secondary to claim verdicts | pr-description Claude: assertions +0.10, judge 5–0 for without |
| D4 | The full-evaluation size: 5 tasks × 2 repeats × 2 vendors, adaptive, about 100 calls. Close variant ranking during a fix uses the writing-style floor on the claims in question only | §6.2 intervals |
| D5 | Rebuild the five existing suites to v2 or keep them as screens | All five sit at ceiling today |
| D6 | ~~Who approves a card's claim list~~ Decided 2026-10-07: agents author the claims and the tasks, and the tooling enforces the shape. `authoring.json` records the calls and every dropped check, so any card can be reviewed | Operator, this session |
| D7 | Open from before: writing-style holdout negatives, Codex scratch-root browsing, R1 to R11 in REPLACEMENT-BRIEF | `BOARD.md` "Open after 2026-10-05" |
