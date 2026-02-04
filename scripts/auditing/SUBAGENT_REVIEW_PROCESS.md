# Parallel Subagent Skill Review Process

This document describes the repeatable workflow for running **parallelized subagent reviews** of skills against `scripts/auditing/SKILL_REVIEW_CHECKLIST.md`, and optionally producing **ready-to-apply patches**.

## Goals

- Review many skills quickly and consistently.
- Keep reviews **independent** (no cross-skill dependencies inside skill definitions).
- Produce **actionable output** (findings + patch) with minimal back-and-forth.

## Inputs

- `scripts/auditing/SKILL_REVIEW_CHECKLIST.md`
- One or more skill entry points: `<skill>/SKILL.md`
- Optional: shared references (e.g., `pdf-files/resources/agent-skills-universal-standard.md`)

## Output Options

1. **Review-only**: Findings + Proposed edits (no patch)
2. **Patch-ready**: Findings + Unified diff patch

Default for speed: **patch-ready**.

## Workflow Overview

1. **Select a batch** of skills to review (3–6 at a time is a good default).
2. **Spawn subagents in parallel** (one per skill) with strict read-only scope.
3. Each subagent:
   - reads `scripts/auditing/SKILL_REVIEW_CHECKLIST.md`
   - reads the target `<skill>/SKILL.md`
   - outputs findings + a unified diff patch
4. Controller (you or main agent):
   - reviews patches for consistency and independence
   - applies patches (if approved)
   - runs `scripts/audit_skills.py`

## Subagent Prompt Template (Patch-Ready)

```text
Task: Evaluate <skill>/SKILL.md against scripts/auditing/SKILL_REVIEW_CHECKLIST.md and output a unified diff that would bring it into compliance. Do not edit files.
Scope: Only read <repo>/scripts/auditing/SKILL_REVIEW_CHECKLIST.md and <repo>/<skill>/SKILL.md.
Rules:
- If anything is ambiguous, STOP and output QUESTIONS.
Output:
- Findings (brief)
- Proposed patch (unified diff).
```

## Parallel Execution (Example)

```bash
codex exec --sandbox read-only "...<skill A prompt>..." &
codex exec --sandbox read-only "...<skill B prompt>..." &
codex exec --sandbox read-only "...<skill C prompt>..." &
wait
```

## Patch Application Process

1. Review each patch for:
   - skill independence (no required references to other skills)
   - checklist compliance
   - clarity + concision
2. Apply patches one-by-one.
3. Run:

```bash
.venv/bin/python scripts/audit_skills.py
```

## Quality Gates

A patch is acceptable if it:

- Adds trigger phrases and trigger tests
- Includes step-by-step instructions with outputs
- Adds decision points and pitfalls where relevant
- Defines required inputs and constraints
- Adds an output contract + reporting format
- Keeps skill content under token limits
- Preserves independence from other skills

## Notes

- If a skill is already compliant, subagents should return “no changes needed” and an empty patch.
- For large or complex skills, split reference material into `references/` and add a short index.
- Keep subagent scopes **tight** to avoid accidental cross-file changes.
