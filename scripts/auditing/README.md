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

## What Each File Does

- `SKILL_REVIEW_CHECKLIST.md`
  - The canonical quality gate for skill content.
  - Enforces tool-style language, trigger phrases/tests, structured instructions, outputs, and reference decomposition.

- `run_parallel_skill_reviews.sh`
  - Spawns parallel subagent reviews (5–6 per batch by default).
  - Applies changes directly under each skill folder.
  - Measures reference size via `tiktoken` to decide when to split/index references.

- `agent_skills_pdf.txt`
  - Extracted text from the reference PDF for offline use during reviews.

- `logs/`
  - Subagent execution logs per skill.

## Decisions (Rationale)

### Checklist rules

- **Tool-style language**: Skills are a knowledge/method layer, not an agent persona.
- **Trigger phrases + trigger tests**: Ensures activation is predictable and repeatable.
- **Structured workflow**: Step outputs + decision points prevent ambiguous execution.
- **Reference decomposition**: Long or multi-topic references are split and indexed to keep SKILL.md concise and navigable.

### Reference indexing threshold

- Index when there are **2+ reference files**, or a single reference is **large** (roughly >1200 tokens) or clearly multi-topic.
- Token count is used instead of line count to match model context cost more closely.

### Token checks

- Token measurement is mandatory by default. Use `--no-token-checks` only when you need a fast, dependency-free run.

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
