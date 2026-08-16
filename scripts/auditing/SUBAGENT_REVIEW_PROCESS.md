# Parallel Subagent Skill Review Process

This document describes the repeatable workflow for running **parallelized subagent reviews** of skills against `scripts/auditing/SKILL_REVIEW_CHECKLIST.md` using the project runner.

## Goals

- Review many skills quickly and consistently.
- Keep reviews **independent** (no cross-skill dependencies inside skill definitions).
- Produce direct, auditable updates with per-skill logs.

## Inputs

- `scripts/auditing/SKILL_REVIEW_CHECKLIST.md` — the binding bar
- `scripts/auditing/references/authoring-guidance.md` — depth behind the bar, read on demand
- `scripts/auditing/OPEN_ITEMS.md` — settled calls a reviewer must not re-open, plus the parity register
- One or more skill entry points: `<skill>/SKILL.md`

## Workflow Overview

1. **Select a batch** of skills to review (default batch size is 10).
2. **Spawn subagents in parallel** (one per skill). The runner's subagent sandbox defaults to `danger-full-access` (`--subagent-sandbox`); that flag governs single-model mode's write-capable codex dispatch only. The default multi-arm reviewer arms are read-only by prompt instruction, not by sandbox: bubblewrap cannot create a user namespace in this container, so every codex sandbox mode is a silent no-op (devcontainer ruling, operator, 2026-08-16), and the codex reviewer arm is dispatched with `--sandbox danger-full-access`, same as single mode.
3. Each subagent:
   - reads `scripts/auditing/SKILL_REVIEW_CHECKLIST.md` and `scripts/auditing/OPEN_ITEMS.md`
   - reads the target `<skill>/SKILL.md`
   - applies changes under that skill directory only, subtraction included
   - writes results to `scripts/auditing/logs/<skill>.log`, ending in one status line
4. Runner runs `scripts/audit_skills.py` unconditionally once all subagents complete.
5. Controller (you or main agent):
   - checks success/failure summary from the runner

## Multi-model review

**Pipeline shape.** Each skill review dispatches N reviewer arms — one read-only call per arm — then one synthesis call that reads every arm's review and produces the skill's verdict. There is no third stage. The arm set is read from the runner's `REVIEWER_ARMS` declaration; today it holds codex and claude (N = 2), for N+1 = 3 calls per skill.

**Mechanical default.** The runner's `usage()` states the default and the opt-out, transcribed verbatim:

```
Default: dual mode. Per skill, dispatch one read-only reviewer per declared
arm (REVIEWER_ARMS, currently codex and claude), then one synthesis call
over every arm's review, and report the synthesis outcome as the skill's
verdict: N+1 calls per skill.
```

```
  --single-model        Opt out of the dual default: dispatch one codex
                        reviewer per skill, as before dual mode existed
```

No flag runs this default pipeline. `--single-model` (or `SINGLE_MODEL=1`) opts out to the single-reviewer path that predates it.

**Operational default.** Multi-arm review is the standard review pass for every skill in the library; the single-arm mode is an exception a human selects deliberately (operator decision, 2026-08-12).

**Authority split.** Every reviewer arm is read-only and advisory: it reads the skill and the bar and reports a review, applying no edit. The synthesis agent is the only writer in a multi-arm run, holding exactly the existing single reviewer's authority under `SKILL_REVIEW_CHECKLIST.md` §4 and this document's own `Removal authority` section below: it deletes autonomously only the closed five-item list, and whole sections, files under `references/` or `scripts/`, and whole skills stay propose-never-execute, ruled on by the operator.

**Tie-break rule.** The synthesis call resolves disagreement between arms using `synthesis-prompt.md`'s `Tie-break chain`, quoted here in the source's own words for the steps that decide a skill's verdict:

> a. A finding is actionable only if it cites a specific checklist section and the cited condition is verifiable in the skill file. A finding no review can ground in the checklist is not applied.
>
> b. Where two or more positions are grounded in the checklist and conflict, subtraction wins. […] One narrowing applies to the union, and only one: it never deletes the last statement of a rule.
>
> c. Only a conflict surviving steps a and b […] ends the run with QUESTIONS instead of a change.

The grouping mechanics behind step b's narrowing, and step c's required output format for surviving positions, are not restated here — read them in the asset.

**Model tier and vendor per call site**, transcribed from `./scripts/auditing/run_parallel_skill_reviews.sh --print-model-policy` (`resolved=` values are never repeated in this document — see `--print-model-policy` for the live resolution):

| Site | Tier | Vendor |
| --- | --- | --- |
| `reviewer-arm-codex` | terra | codex |
| `reviewer-arm-claude` | terra | claude |
| `synthesis` | terra | claude |

**No anonymization stage.** The pipeline anonymizes nothing. The synthesis agent may be able to tell which arm wrote which review, and nothing tries to prevent that. What anchors acceptance instead is the vendor-agnostic framing block and the requirement that every applied finding cite the checklist section it rests on — both carried by `synthesis-prompt.md`, not restated here — and that framing is not a debiasing or concealment mechanism.

## Runner Commands

```bash
./scripts/auditing/run_parallel_skill_reviews.sh

# Narrow scope
./scripts/auditing/run_parallel_skill_reviews.sh --skill testing --skill deps-audit

# Custom concurrency
./scripts/auditing/run_parallel_skill_reviews.sh --batch-size 4
```

## Review Process

1. Review each changed skill for:
   - skill independence (no required references to other skills)
   - checklist compliance
   - clarity + concision
2. Review logs in `scripts/auditing/logs/` for any QUESTIONS or failures.
3. Run:

```bash
.venv/bin/python scripts/audit_skills.py
```

## Removal authority

Reviews may subtract. This reverses the previous rule, which forbade removal outright and made growth the only sanctioned outcome.

<!-- parity:removal-authority:start -->
- **Delete autonomously**: sentences restating their own heading, restatements of the frontmatter description, duplicate statements of a rule already made in the same file, vacuous heading qualifiers, and steps whose only output is "report per the output contract".
- Propose, never execute: removing a whole section, a file under `references/` or `scripts/`, the skill itself, or activation cues found in `SKILL.md`. A proposal carries the evidence and what would be lost; the operator rules on it. For activation cues, the reviewer writes the cue content directly into `trigger-cases/<skill>.md` - the one scoped exception to dispatch scope - and files a removal proposal for the `SKILL.md`-side text. Filing that proposal discharges the §1 obligation for that skill; the review proceeds to a normal verdict.
<!-- parity:removal-authority:end -->

Kept in sync with `SKILL_REVIEW_CHECKLIST.md` §4 and `scripts/auditing/reviewer-prompt.md` — see the parity register in `OPEN_ITEMS.md`.

## Quality Gates

A review is acceptable when all seven hold. Gate 1 can only be satisfied by a subtraction or by an explicit finding that there was nothing to cut — an addition-only review fails it. In a multi-arm run, all seven gates apply to the synthesis output; the reviewer arms' artifacts are inputs to that call, not reviews evaluated separately against Gate 1.

1. **Pruning pass ran.** The log names every sentence, step, and qualifier deleted from the closed five-item list in `SKILL_REVIEW_CHECKLIST.md` §4, or states that the pass found nothing to cut. This gate is a reporting requirement over that closed set, not an independent grant to delete beyond it. Silence is a failure.
2. **Differentiation reported.** One `DIFFERENTIATION: STRONG|WEAK` line with evidence. Never acted on.
3. **Boundary intact.** Frontmatter contract complete; both `Use this skill when` and `Do not use this skill when` present.
4. **Independence preserved.** No skill requires or checks for another skill; activation cues stay out of `SKILL.md`. A skill whose in-`SKILL.md` cues were surfaced as a removal proposal and written into `trigger-cases/<skill>.md` does not fail this gate.
5. **Steps are executable.** Every step yields an artifact, a decision, or a command run — not an instruction to report. Decision points are explicit.
6. **Budgets held.** Frontmatter and `SKILL.md` token limits respected; `references/` one level deep with an index at two or more files.
7. **Nothing settled was re-opened.** No change argues against a call recorded in `OPEN_ITEMS.md`.

## Verdicts

A verdict is recorded by executing `scripts/auditing/review-result.sh` with `--status` set to the outcome, once, when the review (or the synthesis pass) is finished. That execution is what files the result and writes the call's verdict file; the matching prose status line below is commentary for the reader, not the record — a call that only writes prose leaves no result on record and the runner falls back to classifying that prose, landing safety for that path only.

- `--status no-change` (stated in prose as `REVIEW_STATUS: NO-CHANGE`) — the skill already meets the bar. A successful outcome, not a reason to find something to add.
- `--status changed` (stated in prose as `REVIEW_STATUS: CHANGED`) — edits applied, subtraction included.
- `--status questions` (stated in prose as `QUESTIONS`) — blocked on ambiguity; the runner marks the skill failed and the operator resolves it.

Alongside `--status no-change` or `--status changed`, the call always carries `--differentiation` and `--removals`, matching the `DIFFERENTIATION:` line from §3 and a `REMOVAL PROPOSALS:` block from §4 stated in prose, written as `none`/no removals when there are none. `--status questions` forbids both flags; `QUESTIONS` ends the review immediately and its prose carries neither `DIFFERENTIATION` nor `REMOVAL PROPOSALS`.

`READ_PROOF` travels as `review-result.sh`'s `--read-proof` argument, not as a prose line. The runner selects one challenge line per skill from `SKILL.md` before dispatching any arm, writes it to `$LOGDIR/<skill>.readproof`, and requires each reviewer arm's call to carry that line verbatim as the `--read-proof` value, proving the file was actually read rather than assumed. An arm whose verdict file carries no `READ_PROOF` key, or whose value does not match, is recorded as a failed arm (`read-proof absent` / `read-proof mismatch`) and blocks the skill before synthesis, regardless of what outcome its verdict file or prose says. The synthesis call passes no `--read-proof`; it reads reviewer artifacts, not `SKILL.md`.

The runner collects the `DIFFERENTIATION:` lines and any non-empty `REMOVAL PROPOSALS:` blocks into an operator-decisions summary at the end of the run. Neither fails the run; both require a ruling.

In a multi-arm run, the synthesis call's execution of `review-result.sh` is the sole source of the skill's verdict; each reviewer arm's own tool call and status line are part of its artifact and are read as input, not tallied or averaged into the run's verdict.

A verdict is read from a call's verdict file when the file is non-empty. Only when it is absent or empty does the runner fall back to classifying the call's final-message artifact, and on that fallback path an artifact that quotes another agent's `REVIEW_STATUS` line as a line of its own is classified as that quoted verdict rather than its own — so where a verdict is disputed, check it against the verdict file path the runner prints on the per-skill result line.

## Notes

- For large or complex skills, route reference material into `references/` and add a short index — when a reader does not need it in line, not because a token count was crossed.
- Keep subagent scopes **tight** to avoid accidental cross-file changes.
- Keep activation test prompts in `scripts/auditing/trigger-cases/`, not in `SKILL.md`.
