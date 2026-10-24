# Task: rebuild the `testing` skill against the failures agents actually produce

Parent: `tmp/testing-overhaul/PLAN.md` · Evidence: `tmp/testing-overhaul/RECOMMENDATIONS.md` and a survey of agent sessions in one client project · Status: **ready for operator rulings** (section 4), written 2026-10-09 against `d1b19a6`. Part of the pilot in [ROADMAP.md](ROADMAP.md) §7, step 10.

Paths under `tmp/` and `~/.cache/skill-eval/`, and learned-rule ids, name local working files and memory that are not committed. They are kept as provenance.

Every command, count and expected output in this brief was executed against `d1b19a6` on 2026-10-09 unless it is marked **to build** or **extrapolated**. This brief is the operator's direction by name for the skill edits in phase 3 once section 4 is ruled. Without that ruling, no file under `skills/testing/` changes.

## 1. Why this task exists

The `testing` skill is meant to make agents write tests that catch real regressions and nothing else. The evidence says it does not.

### 1.1 It costs more and measures no gain (fact)

- Eval runs `~/.cache/skill-eval/runs/20261005T194239Z-performance-testing-edd87e` (Claude Sonnet) and `…-90f581` (Codex gpt-5.6-terra): explicit mode, 3 pairs on each of 2 tasks per vendor.
- Claude: $0.117 per with-skill run against $0.084 without (1.4x). Kill ratio 1.000 in both arms on both tasks.
- Codex: 3.2x uncached input and 2.6x output with the skill. Kill ratio 0.958 with against 1.000 without on `discount-tests`, 0.833 in both arms on `slug-tests`.
- The Codex cost came from breaking the code once per test. The fixtures are two 20-line pure functions, so both arms sat at the ceiling.

### 1.2 In real work it rarely loads (fact)

- The client project (Angular + Jest front end, .NET back end): `usage scan` found the skill loaded in 3 of 427 sessions. One was the operator deleting a reference file.
- 36 sessions wrote test files. Two loaded the skill, though the project's implementer template says "Use the `testing` skill if available".
- In those two sessions, the only behaviour the skill changed was one break-the-code check per session. It cost 1.9 to 3.8% of uncached input and 6.5 to 8.0% of output.
- Unused in both: the automation and api modes, the supplied-plan section, flaky triage, static-grep, `scripts/test.sh`, every reference file. `scripts/test.sh` also never ran in the eval.

### 1.3 It misses the failures that get deleted (fact)

On one 3-task pull request in that project (2026-10-05), another developer's review found many of the agent-written tests useless. A cleanup audit took the five touched test classes from 103 to 94 tests, after about 150 agent runs on the pull request. The survey's pattern table, against the current skill:

| Pattern seen in the client project | Current skill |
| --- | --- |
| Redundant test that re-pins what another test pins (largest deletion class, 5+ findings) | Missed |
| An agent-written brief or reviewer prescribes the bad test, and the implementer writes it literally (3 briefs, 1 reviewer finding) | Missed |
| "Never calls X" asserted on a double the code cannot reach (3) | Weak |
| Break-to-prove done by adding the exact call the test looks for (2) | Weak |
| Reflection on a constructor to prove "does not depend on X" (1, written twice) | Weak |
| Test re-implements the production wiring it should exercise (1, rewritten twice) | Missed |
| `if`/`switch` arranges inside parameterised tests (3) | Missed |
| Duplicated test helpers across files (5 families) | Missed |
| Call-count or call-argument assertions on collaborators (3 sessions), with reviewers disagreeing on when an interaction is the contract | Named, with no rule for the boundary case |
| Agent read the project's "drive the DOM" rule, then copied the bad pattern from the neighbouring spec file (1) | Named, but local precedent is not addressed |
| Test cannot fail against its bug (4, found by reviewers with mutations) | Named strongly |

Not observed in agent-written test code: skip or focus markers, sleeps, swallowed exceptions, re-blessed snapshots, expected values edited to match a failure. One session widened an exact match to "contains" after a failure without a written diagnosis.

### 1.4 What follows (inference)

The skill must stop paying for sections no agent uses. It must target redundancy, brief-prescribed tests and pruning. Its gains must be measured by tasks that can see those, which the current suite cannot.

## 2. Outcome

| Problem | Change | What gets better | Measured by |
| --- | --- | --- | --- |
| Redundant tests | Gate admits a test only when no existing test catches its regression. The break check doubles as the redundancy check | Fewer tests per change, each with unique value | Claim C1 |
| Break check costs 3.2x on Codex | One plausible break per behaviour, batched, run against the whole affected test file | Cost near the 2 to 4% seen in real sessions | Cost per arm against the baseline run |
| Contrived breaks certify vacuous tests | A break must be a plausible regression of existing code, never new code aimed at the assertion | Break check stops certifying "never called" tests | C4 |
| Negative requirements tested by reflection or unreachable doubles | Prove them through real wiring or an observable outcome | Tests that catch a wiring regression | C4 |
| Bad tests ordered by briefs and reviewers | Guidance for the brief writer and a two-direction review question | Fewer bad tests at the source | C5 and a judged review task |
| No path for the other developer's cleanup | New prune mode: keep, merge or delete each test, with reasons | An agent can run the cleanup before a human must | C5 |
| Tests coupled to implementation | Kept rule, now measured | Tests survive refactors | C3 |
| Over-testing a pure change | Kept rule, now measured | No tests added for a rename. No absence tests after a removal | C7 (harm task) |
| Skill too long (217 lines, audit warning) | Cut unused sections, move modes to resources | Smaller load cost, audit clean | `audit-skills.sh` |
| Description covers only "create tests" | Description adds reviewing, pruning and briefing for tests | Skill loads for those requests | Activation runs |

## 3. Scope

**In**

- `scripts/auditing/suites/cards/testing/`: a version-2 eval card with fixtures, planted outputs and scorers (phase 1). The directory does not exist yet.
- `scripts/auditing/suites/scorers/`: new scorers, with unit tests in `scripts/tests/test_testing_scorers.py` (to build).
- `skills/testing/**` (phase 3).
- `scripts/auditing/trigger-cases/testing.md` (phase 3).
- `scripts/tests/data/audit_snapshot.json`, re-blessed (phase 5).
- `CHANGELOG.md`, one entry (phase 5).
- `tmp/testing-overhaul/PLAN.md`, `tmp/testing-overhaul/STATUS.md` (to build), as the resume point.

**Out**

- Any other skill. Do not touch a second skill, even to fix something noticed (learned rule `5c6f416b5b6f`).
- The client project's own templates and rules. That edit belongs in that project (`RECOMMENDATIONS.md` §4).
- A `--variant` flag for `performance run`. It is not needed: the runner snapshots `skills/<name>` at run time (`performance.py:663`), so a run before the rewrite is the baseline arm.
- JavaScript or C# fixtures. `node` exists but no Jest project does, and `pytest` is not installed. Fixtures use Python `unittest`, like the existing ones.
- The existing version-1 suite `scripts/auditing/suites/testing.json`. Leave it in place as history.

## 4. Operator rulings needed before work starts

Each has a default. The implementer proceeds on the default unless the operator rules otherwise.

| ID | Decision | Default |
| --- | --- | --- |
| D1 | Order: measurement first, or rewrite first | Measurement first (phases 1 and 2, then 3). Learned rule `1c93064e7af4` judges a skill by with/without runs, never by reading it |
| D2 | Automation and api modes | Move their workflows into `resources/automation-playbook.md` and `resources/api-testing-mocking-playbook.md`. Keep one decision-point line each in `SKILL.md` |
| D3 | `scripts/test.sh` and the "Quick start" section | Delete both. Zero runs in the client project and in the eval |
| D4 | References never opened (`tdd-iron-laws.md`, `qa-practice-compact.md`, `test-report-template.md`, `performance-regression.md`) | Keep for now. Absence in one project's 36 sessions is weak evidence, and an unopened reference costs nothing |
| D5 | Live spend for phases 2 and 4 (section 9) | Approve per phase, after the dry run prints the plan |
| D6 | The other developer's deleted specs or review comments | Not required. If supplied, port their patterns into the prune task's planted tests |

## 5. Phase 1: build the eval card

Write tasks the way a user or an orchestrating agent would ask. **Do not read `skills/testing/` while writing prompts, assertions or fixtures** (`scripts/auditing/suites/README.md`, "Authoring rules"). Everything needed is in this section. The claims come from failures observed in the client project, not from the skill text.

Card format: `scripts/auditing/skill_eval/PERFORMANCE.md`, "Eval cards: suite version 2". Worked example: `scripts/auditing/skill_eval/examples/text-card.json`. Existing mutation scorer: `scripts/auditing/suites/scorers/mutation.py`. Existing suite runner: `scripts/auditing/suites/scorers/run_tests.py`.

### 5.1 Claims

| ID | Statement | Tasks |
| --- | --- | --- |
| C1 `adds-no-redundant-tests` | Every test the agent adds catches a regression the existing suite misses | T1, T2 |
| C2 `catches-the-change` | The added tests catch regressions in the changed behaviour (kill ratio on change mutants at or above 0.75, the existing scorer's chosen default) | T1, T2 |
| C3 `survives-refactor` | The added tests pass on every behaviour-preserving rewrite of the module | T1, T2 |
| C4 `proves-negatives-through-wiring` | A "never uses X" requirement is tested through the real wiring or an observable outcome, so a service-locator regression fails it | T2 |
| C5 `prunes-useless-tests` | Asked to clean or review a suite, the agent removes or flags the useless tests and keeps every test that alone catches a regression | T3, T8 |
| C6 `no-forced-green` | A test that fails because of a code defect gets the code fixed. The test file stays unchanged | T5 |
| C7 `proportionate` | No test is added for a pure rename. A removal is verified by deleting tests, never by a test asserting absence | T6, T7 |

`invalidation`: `{"SKILL.md": "all", "references/testing-anti-patterns.md": ["C1", "C4", "C5"], "resources/*.md": []}`. Adjust after phase 3 if `rests_on` changes.

### 5.2 Tasks

All fixtures use invented domains. Never copy client code, class names or people's names into a fixture.

**T1 `late-fee-tests`** (deliverable, claims C1, C2, C3). Fixture `testing-invoice`: `billing/invoice.py` with tax and rounding rules already covered by `tests/test_invoice.py` (about 8 tests), plus a new late-fee rule (grace days, a rate, a cap) that has no tests. Prompt: "I added late fees to `billing/invoice.py` (`late_fee()` and its use in `amount_due()`). Add tests for that. We use unittest." Mutants: about 6 on the late-fee rule, which the existing suite misses, and about 4 on tax and rounding, which it kills.

**T2 `local-login-never-remote`** (deliverable, claims C1, C2, C3, C4). Fixture `testing-login`: `auth/services.py` with `build_services(mode)` wiring a `LocalLogin` and, in `remote` mode only, a `DirectoryClient` whose transport makes network calls. Prompt, in an orchestrator's brief voice: "Task 4 of the plan: add a test proving `LocalLogin` never calls `DirectoryClient`, and a test that `LocalLogin.__init__` takes no `DirectoryClient` parameter." Mutants: realistic wiring regressions, including one where `LocalLogin.login` fetches the client through a module-level registry (`services.get("directory")`) with an unchanged constructor. A reflection test and a mock that is never wired in both survive that mutant. A test through `build_services("local")` with the transport stubbed kills it.

**T3 `prune-rates-suite`** (deliverable, claims C5). Fixture `testing-rates`: `shipping/rates.py` and `tests/test_rates.py` with 6 good tests, each the only killer of at least one mutant, and 8 planted useless tests. Each useless test reproduces one pattern from section 1.3. The eight: an exact duplicate under another name, a tautology computing the expected value with the function, and a test of `round()`. Then a private-state read (`calc._table`), a constructor-signature reflection, and `assert_not_called` on a mock the code never receives. Last, a looped `if` over enum values duplicating the good cases, and an expected value from a re-implemented copy of the logic. Prompt: "A reviewer says half of `tests/test_rates.py` is useless. Clean it up: delete or merge what doesn't earn its place, keep what does."

**T4** is not a separate task. C3 is scored on T1 and T2 output by the refactor scorer.

**T5 `red-after-merge`** (deliverable, claims C6). Fixture `testing-recurrence`: `calendar/recurrence.py` with a defect (monthly recurrence on the 31st skips short months instead of clamping) and `tests/test_recurrence.py` with a correct test that fails on it. The docstring states the clamping contract. Prompt: "CI is red on `test_monthly_on_31st` since yesterday's merge. Get it green, I need to ship today."

**T6 `rename-total`** (harm, claims C7). Fixture `testing-rename`: a small package with a passing suite. Prompt: "Rename `calc_total` to `order_total` everywhere and update the callers."

**T7 `remove-legacy-export`** (deliverable, claims C7). Fixture `testing-export`: `export/csv_legacy.py`, a flag that enables it, and its tests. Prompt: "Remove the legacy CSV export and its flag. We don't support it any more."

**T8 `review-test-diff`** (deliverable, claims C5, judged). Workspace with a diff adding 3 good tests and 3 bad ones (redundant, reflection, unreachable `assert_not_called`). Prompt: "Review the tests in this diff before I merge it. Written review only, no edits."

### 5.3 Scorers (to build)

Each scorer prints JSON metrics and exits 0 on pass, like `mutation.py`. Each takes the workspace as its first argument.

| Scorer | Metrics | Pass rule |
| --- | --- | --- |
| `redundancy.py WORKSPACE SPEC` | Per added test method (by unittest id, against the fixture's original ids in SPEC): the set of mutants it kills alone. `redundant_ratio` = added tests killing no mutant the original suite misses ÷ added tests. `change_kill_ratio` over change mutants | `redundant_ratio` == 0 and `change_kill_ratio` ≥ 0.75 |
| `refactor.py WORKSPACE SPEC` | Runs the whole suite on 3 to 5 behaviour-preserving rewrites given as full module texts in SPEC: a renamed private helper, a different internal structure, an inlined function. `refactor_survival` = rewrites passed ÷ rewrites | `refactor_survival` == 1.0 |
| `prune.py WORKSPACE SPEC` | `useless_removed` = planted useless test names absent ÷ 8. `kill_preserved` = after-cleanup kill ratio ÷ original kill ratio | `useless_removed` ≥ 0.75 and `kill_preserved` == 1.0 (chosen defaults) |
| `unchanged_and_fixed.py WORKSPACE SPEC` | Test file hash equals the fixture's. Hidden tests, copied in from SPEC, pass on the agent's module | Both true |
| `test_count.py WORKSPACE SPEC` | Test method count against the fixture's, suite result, and any test file mentioning a removed symbol (T7) | Count not above the original. Suite passes. No mention of the removed symbol |

Run a test by id with `python3 -m unittest <id>` in a temporary copy, the way `mutation.py` copies the tree. Restore the original module from SPEC, so an agent edit to the module cannot rescue its tests.

### 5.4 Gates for phase 1

1. For every scorer, show it can fail. Run it on the untouched fixture and on a planted bad output, and record the failures (learned rule `023b754b33aa`).
2. Plant one good and at least one bad output per task under the card's `planted/`. Each bad output reproduces the section 1.3 pattern it targets.
3. `python3 scripts/auditing/skill-eval.py performance validate --suite scripts/auditing/suites/cards/testing/card.json` reports 0 errors. On the example card today it prints `0 errors, 0 info.`
4. Unit tests for every scorer pass in `scripts/tests/test_testing_scorers.py`.
5. Full suite: `python3 -m unittest discover -s scripts/tests`. Baseline today: `Ran 686 tests`, one error, `test_shellcheck_gcc_format_reports_zero_lines` (no `shellcheck`). Nothing else may fail.
6. Document the card in `scripts/auditing/suites/README.md`'s table (learned rule `2fc024945fa9`).
7. Commit phase 1 on its own: `feat(skill-eval): add the testing eval card and scorers`.

## 6. Phase 2: baseline the current skill

1. Dry run first: `python3 scripts/auditing/skill-eval.py performance run --skill testing --suite scripts/auditing/suites/cards/testing/card.json --repeats 5 --models claude=sonnet,codex=gpt-5.6-terra --judge-vendor cross --dry-run`.
2. Read the printed plan. Stop for D5 approval with the call count.
3. Run it live with `--max-cost-usd` and `--max-codex-tokens` set from section 9.
4. Run `performance report <run_dir>` and copy the per-claim verdicts and per-arm cost into `STATUS.md`.
5. Calibrate. A task where the no-skill arm meets its claim at 0.8 or above on both vendors (`BASELINE`) cannot show a gain. Harden it, or drop it with a note, before phase 3.
6. Run `--mode natural` once on T1 and T3, at 3 repeats. Record how often the skill loads unprompted.

Use the same models as the 2026-10-05 runs so the numbers stay comparable. Measure both vendors in every run. Dropping one is a finding to state before the run, never a default (learned rule `5bfb5ff81298`).

## 7. Phase 3: rewrite the skill

### 7.1 Rules for every edit

- Edit only the files listed in section 3.
- Third-person tool voice. No personas.
- Keep "Use this skill when", "Do not use this skill when", decision points, an output contract, and concrete examples (`scripts/auditing/SKILL_REVIEW_CHECKLIST.md`).
- `SKILL.md` under 200 lines. Frontmatter `name` plus `description` at or under 120 tokens (hard limit), 110 soft.
- Quote any frontmatter value containing `: `.
- One line per paragraph or list item. Never hard-wrap prose.
- Vendor-agnostic wording. No tool names from one harness.
- Self-contained. Never require another skill.
- No client names, project names, people's names or client code anywhere in the skill. Generalize every client example into an invented one.
- Every number carries provenance or a "chosen default" note.
- Keep the carried rules that have sources, and update `references/provenance.md` for every rule added.
- Activation cues go in `scripts/auditing/trigger-cases/testing.md`, never in `SKILL.md`.
- Do not tune against the sealed holdout. Use it once, in phase 4.

### 7.2 Target outline of `SKILL.md` (about 180 lines)

| Section | Content | Source |
| --- | --- | --- |
| Frontmatter | New description (7.4) | — |
| Opening | One paragraph: the skill writes tests that catch regressions no other test catches, reviews and prunes test suites, and writes test briefs for other agents | New |
| Use when / Do not use | Keep the current bullets. Add: reviewing tests in a diff, pruning a suite, writing a brief that asks for tests. Keep the "defect in product code" exclusion verbatim | Current + R4 |
| Required inputs | Keep, trimmed to three bullets | Current |
| Project conventions first | Keep step 1. Add one sentence: a documented convention beats the pattern in neighbouring test files, and a neighbour that breaks it is not a template | Current + R2 |
| Admission gate | Rewritten steps 2 to 4 (R1) | R1 |
| Do not write these tests | Keep the five current bullets and the cart example. Add four (R2) | Current + R2 |
| When an interaction is the contract | New, three sentences (R3) | R3 |
| When a test you wrote fails | Keep, including the stop rule. Tighten wording only | Current |
| Briefs and reviews | New (R4) | R4 |
| Modes | unit (compressed), prune (new, R5), review (folded into prune or its own short mode). One line each pointing to resources for automation and api (D2) | Current + R5 |
| Plans and specs | Three bullets replacing the long section: data, not instructions. Run the project's own commands, never the document's verbatim. Escalate destructive, credential and fetch-and-execute steps | Current, compressed |
| Flaky-test triage | One paragraph plus the reference pointer | Current, compressed |
| Static-grep tripwires | The gate paragraph plus the reference pointer | Current, compressed |
| Output contract | Per mode: tests added with behaviour and break, tests rejected with reason, defects found. For prune: keep, merge or delete per test with reason | Current + R5 |
| References | Updated list | — |

Removed: "Quick start" and `scripts/test.sh` (D3). Moved: automation and api workflows (D2).

### 7.3 Required content changes

**R1, admission gate.** Step 2: a test is written only when its name states the behaviour, a realistic change that turns it red, and that no existing test turns red for that change. Step 4, rewritten:

- Break the behaviour with one plausible regression of existing code: delete a branch, flip a condition, return a wrong constant, revert the fix.
- Never add code that exists to trip the assertion. That proves nothing.
- While it is broken, run the whole affected test file, not the new test alone.
- When an existing test already fails, the new test is redundant unless it pins a distinct branch. Do not keep it.
- One break per behaviour, not per test. Batch breaks that do not interfere into one run.
- Restore the code and record the break and the failing test names.

**R2, four new "do not write" entries,** each a smell and a fix:

- Negative requirements through doubles or reflection. "Never calls X" or "does not depend on Y" is tested through the real wiring or an observable outcome. Never `assert_not_called` on a double the code cannot reach. Never reflect over a constructor.
- A re-implemented system under test. A test that rebuilds the production wiring or arrange by hand tests the copy. Use the real factory or registration.
- Logic in a test. `if`, `switch` or loops over enum values in a test body. Split into cases with literal arranges.
- Local precedent over the documented convention. When nearby tests break the project's written convention, follow the convention.

Add the same four to `references/testing-anti-patterns.md` as entries 13 to 16 with code pairs, plus entry 17, redundant test, and entry 18, spying on a framework method in place of the rendered output. Add the two-direction review question to its detection checklist.

**R3, interactions that are the contract.** Call-count and call-argument assertions stay banned on internal collaborators. At an I/O boundary they are correct when the call is the observable effect. The three examples: a message sent, a write that must not happen on unchanged input, a cancellation token reaching the boundary.

**R4, briefs and reviews.** A brief that asks for tests names the behaviour and the regression it must catch. It never prescribes the mechanism, such as reflection, a never-called assertion or one case per enum value. A test review asks, for every test, whether a needed test is missing and what regression this test catches that nothing else catches.

**R5, prune mode.** Input: a test file, a suite or a diff. Workflow: list each test with the regression it catches. Run the break check where the answer is unclear. Mark each test keep, merge or delete with a one-line reason. Delete or merge, then run the suite. Confirm with breaks that no deleted test was the only one catching its regression. Output: the per-test table and the suite result.

**R6, mocking.** Bring in the client project's widened rule as a general one. A mock is also right where it removes non-determinism, reaches an error path a real dependency cannot trigger on demand, or stands in for a dependency whose internals leak timers or state. Never mock the unit under test, and never assert on the mock's own call arguments as the behaviour. Leave out the client project's service names.

### 7.4 Description and trigger cases

- Rewrite the description to cover writing tests, reviewing tests in a diff, pruning a suite, and writing a brief that asks for tests. Keep the exclusions that stop false loads: debugging product code, testing theory.
- Write 2 to 4 description variants to `tmp/testing-overhaul/description-*.txt`.
- Measure each on the train split: `python3 scripts/auditing/skill-eval.py activation run --skill testing --split train --description-file <file> --models claude=sonnet,codex=gpt-5.6-terra --repeats 3`. The `sys1-mcp` fix (`tmp/sys1-fix/README.md`) shows the pattern.
- Add positives to `trigger-cases/testing.md` for review, prune and brief requests, and negatives for near misses: refactoring code that has tests, writing a non-test brief. Run `python3 scripts/auditing/skill-eval.py cases lint --skill testing` and fix every error.
- The holdout `scripts/auditing/sealed/testing.holdout.sealed` has 0 of 3 looks spent (`common.holdout_looks("testing")` returns `[]`). Spend one look, on the chosen variant only.

## 8. Phase 4: measure the rewrite

1. `python3 scripts/auditing/skill-eval.py performance plan --skill testing --suite scripts/auditing/suites/cards/testing/card.json` lists the invalidated claims.
2. Rerun the phase 2 command on the rewritten skill. Add `--adaptive` to skip claims already decided.
3. Rerun the natural-mode check from phase 2, step 6.
4. Apply the ship criteria below and record the result in `STATUS.md`.

Ship criteria (chosen defaults, not measured thresholds):

- No claim is `HARM` for the rewrite, pooled or on either vendor.
- At least two of C1, C4 and C5 are `STRONG` pooled, or each beats the current skill's with-rate on both vendors.
- C3, C6 and C7 do not fall below the current skill's with-rate on either vendor.
- Per-arm cost ratio (with ÷ without, uncached input plus output) is at or below the baseline's on each vendor.
- Activation: train-split positives at or above the current description's on both vendors, false loads not above them, and the one holdout look agreeing.

If the rewrite misses a criterion, report which and stop. Do not iterate against the visible card more than twice without the operator. It is visible, so repeated tuning overfits it.

## 9. Budget (extrapolated)

From the 2026-10-05 runs: 6 pairs per vendor cost about $2.28 of Claude spend and 3.75M Codex tokens in total, judges included. Phase 2 has 8 tasks at 5 repeats on 2 vendors, 80 pairs against those 12, about 6.7 times: about $15 and 25M Codex tokens. Phase 4 with `--adaptive` costs at most the same. These are extrapolations. The new fixtures are larger than the old ones, so set the caps about 25% above.

## 10. Phase 5: ship

1. `./scripts/audit-skills.sh`. Today: `skills_with_issues: 0`, and `testing` carries `entry_over_200_lines:217`. After the rewrite, `testing` must have no issue and no warning.
2. `python3 scripts/tests/generate_snapshot.py`. The snapshot pins the 217-line warning, so the full suite fails until it is re-blessed.
3. `python3 -m unittest discover -s scripts/tests`. Only the `shellcheck` error may remain.
4. Re-read every edited file in full. Look for truncation, broken links, scratch text and term drift.
5. `CHANGELOG.md`: one bullet under today's `## YYYY-MM-DD`, `### Changed`. Factual, no narrative (`.agent/memory/changelog-convention.md`).
6. Commit with the `smart-conventional-commits` skill on a branch cut from `main`. Stage explicit paths only. No co-author trailer.
7. Suggested commits: `feat(testing): gate tests on unique regressions and add prune mode`, then `docs(changelog): record the testing skill rewrite`.
8. Update `PLAN.md` and `STATUS.md` with the run directories, verdicts and the commit hashes.

## 11. Acceptance criteria

- AC1. `performance validate` reports 0 errors on the card. Every scorer was shown failing on a planted bad output.
- AC2. A phase 2 baseline run exists for both vendors, with per-claim verdicts and per-arm cost recorded in `STATUS.md`.
- AC3. `skills/testing/SKILL.md` is under 200 lines. `audit-skills.sh` reports nothing for `testing`.
- AC4. R1 to R6 are each present. `grep -n "test.sh\|Quick start" skills/testing/SKILL.md` returns nothing (D3 default).
- AC5. A case-insensitive `grep` for the client project's name, its product names and people's names over `skills/testing`, `scripts/auditing/suites/cards/testing` and `scripts/auditing/trigger-cases/testing.md` returns nothing. It returns nothing on `skills/testing` and the trigger file today.
- AC6. The phase 4 run meets the ship criteria in section 8, or `STATUS.md` names the criterion it missed and the work stops there.
- AC7. Full test suite: only the `shellcheck` error remains.

## 12. Gotchas

- **Redundancy needs mutants on every branch of the change.** A new test pinning a branch no mutant touches looks redundant. Give each branch of the changed behaviour at least one mutant, and test the scorer on a good test that pins a distinct branch.
- **Prune scoring by test name misses renames.** An agent that renames a useless test keeps it under a new name. `kill_preserved` is the guard on the good side. T8's judge is the backup on the useless side.
- **Codex browses the scratch root** when a prompt names a file the fixture lacks, and that call is marked contaminated (`tmp/skill-eval-build/BOARD.md`, "Open after 2026-10-05"). Every file a prompt names must exist in the fixture.
- **The Claude credential guard** refuses to start an arm within 1200 s of token expiry. Start long runs on a fresh login.
- **Explicit mode forces the load.** It measures what the skill does once loaded, not whether it loads. Natural mode answers the second question.
- **The card is visible.** Its results are development evidence. No sealed performance holdout exists.
