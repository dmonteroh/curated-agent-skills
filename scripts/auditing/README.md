# Auditing Scripts

This folder contains the skill review checklist, the parallel review runner, and supporting artifacts.

## Setup: tiktoken required for token checks

Token checks require `tiktoken`. The recommended way to run the audit installs it automatically:

```bash
./scripts/audit-skills.sh
```

If you want to run the audit directly:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements-audit.txt
.venv/bin/python scripts/audit_skills.py
```

To explicitly skip token checks:

```bash
./scripts/audit-skills.sh --no-token-checks
```

## Parallel skill reviews

The parallel reviewer installs the same audit dependencies automatically and uses the repo `.venv`:

```bash
./scripts/auditing/run_parallel_skill_reviews.sh
```

Pipeline behavior:

1. Review subagent updates each selected `skills/<skill>/SKILL.md`.
2. Runner runs `scripts/audit_skills.py` unconditionally once all subagents complete.

Useful options:

```bash
# Preview selected work without running subagents
./scripts/auditing/run_parallel_skill_reviews.sh --dry-run

# Run a smaller custom batch
./scripts/auditing/run_parallel_skill_reviews.sh --batch-size 4

# Target a subset
./scripts/auditing/run_parallel_skill_reviews.sh --skill testing --skill deps-audit

# List discovered skills
./scripts/auditing/run_parallel_skill_reviews.sh --list-skills
```

## What Each File Does

- `SKILL_REVIEW_CHECKLIST.md`
  - The binding quality bar for skill content; always loaded by reviewers, and it outranks the resources below.
  - Covers the frontmatter contract, the use/do-not-use boundary, differentiation, mandatory subtraction, earned structure, voice, executable instructions, references, budgets, and independence.

- `references/authoring-guidance.md`
  - Depth behind the bar, read on demand: the pruning taxonomy, a worked differentiation contrast, over-constraint, leading words, teach-by-contrast, behavioral gates, and the patterns this library rejects on purpose.

- `OPEN_ITEMS.md`
  - Settled calls a reviewer must not re-open, the parity register for deliberately duplicated blocks, deferred lints, and trial-gated removal candidates.

- `run_parallel_skill_reviews.sh`
  - Spawns parallel subagent reviews (10 per batch by default).
  - Applies changes directly under each skill folder, subtraction included.
  - Collects per-skill `REVIEW_STATUS`, `DIFFERENTIATION`, and `REMOVAL PROPOSALS` into an operator-decisions summary.
  - Runs `scripts/audit_skills.py` unconditionally after all subagents complete.
  - Supports targeting specific skills and dry-run planning.
  - Reports per-skill success/failure with log paths.
  - Measures reference size via `tiktoken` to decide when to split/index references.

- `resources/agent_skills_pdf.txt`
  - Extracted text from the reference PDF for offline use during reviews.

- `logs/`
  - Subagent execution logs per skill.

- `trigger-cases/`
  - Per-skill activation test prompts.
  - Not referenced from `SKILL.md` to avoid runtime token overhead.

## Decisions (Rationale)

### Checklist rules

- **Tool-style language**: Skills are a knowledge/method layer, not an agent persona. Since 2026-08-11 the framing stays third person while procedure steps may use the imperative.
- **Trigger cases**: Keeps activation test prompts out of `SKILL.md`, in `trigger-cases/`, for predictable and repeatable activation behavior.
- **Structured workflow**: Step outputs + decision points prevent ambiguous execution. Structure beyond the frontmatter contract and the use/do-not-use boundary is earned by the skill's job, not imposed by a template.
- **Reference decomposition**: Long or multi-topic references are split and indexed to keep SKILL.md concise and navigable.
- **Subtraction**: Reviews must prune. Removing text is a first-class outcome, bounded by the closed five-item list in `SKILL_REVIEW_CHECKLIST.md` §4; whole sections, reference files, and whole skills are proposed for the operator rather than removed.

### Reference indexing threshold

- Index when there are **2+ reference files**. Route material into `references/` when a reader does not need it in line — not because a token count was crossed.

### Token checks

- Token measurement is mandatory by default. Use `--no-token-checks` only when you need a fast, dependency-free run.

### Runner defaults

- Batch size defaults to `10`.
- The runner auto-discovers skills under `skills/*/SKILL.md`.
- Pass `--skill <name>` one or more times to restrict scope.
- `scripts/audit_skills.py` runs unconditionally after subagent updates complete.

## Logs and Gitignore

If you add `scripts/auditing/logs/` to `.gitignore`, local tools and agents will still be able to read and use the logs; they simply won’t be committed to git.

## When to Regenerate agent_skills_pdf.txt

`agent_skills_pdf.txt` is derived from the reference PDF (Richard Hightower's article referenced below). Keep it if you want offline, deterministic access to the reference text. It can be regenerated at any time from the PDF if needed.

## References

These sources informed the checklist and review process:

```
https://medium.com/@richardhightower/agent-skills-the-universal-standard-transforming-how-ai-agents-work-fc7397406e2e
https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
https://cursor.com/docs/context/skills
https://agentskills.io/what-are-skills
https://developers.openai.com/codex/skills/
```
