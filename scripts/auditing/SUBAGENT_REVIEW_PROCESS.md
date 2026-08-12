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
- Optional: shared references (e.g., `scripts/auditing/resources/agent_skills_pdf.txt`, background only — the checklist outranks it)

## Workflow Overview

1. **Select a batch** of skills to review (default batch size is 10).
2. **Spawn subagents in parallel** (one per skill) in workspace-write mode.
3. Each subagent:
   - reads `scripts/auditing/SKILL_REVIEW_CHECKLIST.md` and `scripts/auditing/OPEN_ITEMS.md`
   - reads the target `<skill>/SKILL.md`
   - applies changes under that skill directory only, subtraction included
   - writes results to `scripts/auditing/logs/<skill>.log`, ending in one status line
4. Runner runs `scripts/audit_skills.py` unconditionally once all subagents complete.
5. Controller (you or main agent):
   - checks success/failure summary from the runner

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

- **Delete autonomously**: sentences restating their own heading, restatements of the frontmatter description, duplicate statements of a rule already made in the same file, vacuous heading qualifiers, and steps whose only output is "report per the output contract".
- Propose, never execute: removing a whole section, a file under `references/` or `scripts/`, the skill itself, or activation cues found in `SKILL.md`. A proposal carries the evidence and what would be lost; the operator rules on it. For activation cues, the reviewer writes the cue content directly into `trigger-cases/<skill>.md` - the one scoped exception to dispatch scope - and files a removal proposal for the `SKILL.md`-side text. Filing that proposal discharges the §1 obligation for that skill; the review proceeds to a normal verdict.

Kept in sync with `SKILL_REVIEW_CHECKLIST.md` §4 and the dispatch prompt in `run_parallel_skill_reviews.sh` — see the parity register in `OPEN_ITEMS.md`.

## Quality Gates

A review is acceptable when all seven hold. Gate 1 can only be satisfied by a subtraction or by an explicit finding that there was nothing to cut — an addition-only review fails it.

1. **Pruning pass ran.** The log names every sentence, step, and qualifier deleted from the closed five-item list in `SKILL_REVIEW_CHECKLIST.md` §4, or states that the pass found nothing to cut. This gate is a reporting requirement over that closed set, not an independent grant to delete beyond it. Silence is a failure.
2. **Differentiation reported.** One `DIFFERENTIATION: STRONG|WEAK` line with evidence. Never acted on.
3. **Boundary intact.** Frontmatter contract complete; both `Use this skill when` and `Do not use this skill when` present.
4. **Independence preserved.** No skill requires or checks for another skill; activation cues stay out of `SKILL.md`. A skill whose in-`SKILL.md` cues were surfaced as a removal proposal and written into `trigger-cases/<skill>.md` does not fail this gate.
5. **Steps are executable.** Every step yields an artifact, a decision, or a command run — not an instruction to report. Decision points are explicit.
6. **Budgets held.** Frontmatter and `SKILL.md` token limits respected; `references/` one level deep with an index at two or more files.
7. **Nothing settled was re-opened.** No change argues against a call recorded in `OPEN_ITEMS.md`.

## Verdicts

Every log ends with exactly one status line:

- `REVIEW_STATUS: NO-CHANGE` — the skill already meets the bar. A successful outcome, not a reason to find something to add.
- `REVIEW_STATUS: CHANGED` — edits applied, subtraction included.
- `QUESTIONS` — blocked on ambiguity; the runner marks the skill failed and the operator resolves it.

Alongside `REVIEW_STATUS: NO-CHANGE` or `REVIEW_STATUS: CHANGED`, always: the `DIFFERENTIATION:` line from §3 and a `REMOVAL PROPOSALS:` block from §4, written as `none` when there are none. `QUESTIONS` ends the review immediately; it carries neither.

The runner collects the `DIFFERENTIATION:` lines and any non-empty `REMOVAL PROPOSALS:` blocks into an operator-decisions summary at the end of the run. Neither fails the run; both require a ruling.

## Notes

- For large or complex skills, route reference material into `references/` and add a short index — when a reader does not need it in line, not because a token count was crossed.
- Keep subagent scopes **tight** to avoid accidental cross-file changes.
- Keep activation test prompts in `scripts/auditing/trigger-cases/`, not in `SKILL.md`.
