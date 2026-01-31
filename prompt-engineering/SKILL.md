---
name: prompt-engineering
description: Design, test, and ship production prompts fast (patterns + applied workflows). Includes prompt-as-code conventions, reusable templates, evaluation guidance, and scripts/assets for prompt iteration. Always outputs copy-pastable full prompt text. Use PROACTIVELY when building AI features, improving agent performance, or standardizing system prompts.
---

# prompt-engineering

One canonical skill that combines:
- **Patterns** (few-shot, structured outputs, safety, evaluation)
- **Applied workflows** (draft -> test -> iterate -> deploy/monitor)

## Non-negotiable rule

When creating or updating a prompt, ALWAYS include the complete prompt text in a single copy/paste block. Do not describe a prompt without showing it.

## Use this skill when

- Building AI features and agent behaviors (system prompts, tool-use prompts, routing).
- Improving output quality, consistency, safety, or cost/latency.
- Creating prompt templates and versioned prompt libraries.
- Setting up prompt evaluation / regression tests (prompt-as-code).

## Do not use this skill when

- The user only wants an ad-hoc explanation of prompting concepts.
- No LLM interaction is involved.

## Fast workflow (best performance, best results)

1) Define success
- Task definition, user impact, failure modes, required format.
- Metrics: correctness, consistency, latency, token cost, safety.

2) Draft the smallest prompt that could work
- Clear role + task + constraints + output format.
- Add examples only if needed.

3) Add structure
- Use explicit sections (Context, Task, Constraints, Output Format).
- Prefer machine-parseable output when integration requires it.

4) Evaluate (cheap, then real)
- Start with a small test set (10-30 cases).
- Add adversarial cases (edge, ambiguous, policy boundaries).

5) Iterate in small deltas
- Change one thing at a time; keep a changelog in commit messages or prompt headers.

6) Deploy with guardrails
- Monitor drift; add regression tests and rollback strategy.

## Patterns (high leverage)

- **Instruction hierarchy**: System > Developer > User > Tool outputs.
- **Progressive disclosure**: start simple, add constraints/examples only when needed.
- **Self-check**: require a short verification pass against constraints.
- **Uncertainty handling**: require explicit “missing info” and questions.
- **Tool use**: define when to call tools and what inputs/outputs look like.

## Assets / scripts

- Templates and examples: `assets/`
- Reference guides: `references/`
- Optional optimizer: `scripts/optimize-prompt.py`
- Wrapper: `scripts/prompt.sh`

## References

- `references/prompt-templates.md`
- `references/prompt-optimization.md`
- `references/few-shot-learning.md`
- `references/system-prompts.md`
- `references/chain-of-thought.md`
