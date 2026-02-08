---
name: prompt-engineering
description: "Designs, tests, and ships production prompts using prompt-as-code workflows, templates, evaluation guidance, and optional scripts/assets. Returns a full copy/paste prompt block. Use when building AI features, improving agent performance, or standardizing system prompts."
category: ai
---
# prompt-engineering

Provides one canonical skill that combines:
- **Patterns** (few-shot, structured outputs, safety, evaluation)
- **Applied workflows** (draft -> test -> iterate -> deploy/monitor)

## Non-negotiable requirement

When creating or updating a prompt, this skill always includes the complete prompt text in a single copy/paste block. It does not describe a prompt without showing it.

## Use this skill when

- Building AI features and agent behaviors (system prompts, tool-use prompts, routing).
- Improving output quality, consistency, safety, or cost/latency.
- Creating prompt templates and versioned prompt libraries.
- Setting up prompt evaluation / regression tests (prompt-as-code).

## Do not use this skill when

- The user only wants an ad-hoc explanation of prompting concepts.
- No LLM interaction is involved.

## Required inputs

- Target task (what the model must do).
- Audience or user context.
- Output format requirements (JSON, bullets, markdown, etc.).
- Constraints (safety, scope, sources, style, length, tools).
- Evaluation criteria and known failure modes (if available).

## Workflow (step-by-step)

1) Define success
- Action: capture task definition, user impact, failure modes, required format, and metrics.
- Output: a short success checklist (3–6 bullets) and evaluation criteria.

2) Draft the smallest prompt that could work
- Action: write role + task + constraints + output format.
- Output: a complete copy/paste prompt block.

3) Add structure only if it improves reliability
- Decision: if outputs are inconsistent, add explicit sections (Context, Task, Constraints, Output Format).
- Output: revised prompt block with clear section headers.

4) Decide on examples
- Decision: if the task is format-sensitive or error-prone, add 1–3 examples; otherwise skip.
- Output: updated prompt block with minimal, high-signal examples.

5) Evaluate (cheap, then realistic)
- Action: define a small test set (10–30 cases) and add adversarial/edge cases.
- Output: test plan and quick pass/fail notes.

6) Iterate in small deltas
- Decision: if a failure mode persists, change one instruction at a time and re-test.
- Output: a short changelog (what changed, why, expected impact).

7) Deploy with guardrails
- Action: add regression tests, monitoring notes, and rollback guidance.
- Output: deployment checklist.

## Patterns (high leverage)

- **Instruction hierarchy**: System > Developer > User > Tool outputs.
- **Progressive disclosure**: start simple, add constraints/examples only when needed.
- **Self-check**: require a short verification pass against constraints.
- **Uncertainty handling**: require explicit “missing info” and questions.
- **Tool use**: define when to call tools and what inputs/outputs look like.

## Common pitfalls

- Missing full prompt block (violates the non-negotiable rule).
- Overstuffed prompts that bury key constraints.
- Ambiguous output format or missing schema.
- Changing multiple variables at once during iteration.
- Adding examples that contradict the rules.

## Output contract

When this skill runs, it always provides:

- **Prompt block**: a single copy/paste block with the full prompt text.
- **Assumptions**: any assumptions made due to missing inputs.
- **Open questions**: specific questions needed to finalize or improve the prompt.
- **Evaluation plan**: test cases or metrics to validate quality.
- **Next actions**: suggested iterations or deployment steps.

## Reporting format

Use this exact structure in the response:

1) Summary
2) Prompt (copy/paste)
3) Assumptions
4) Open questions
5) Evaluation plan
6) Next actions

## Examples

**User request**: "Create a system prompt for a customer support agent that escalates billing disputes."

**Assistant response (excerpt)**:

1) Summary
- Drafted a support-system prompt with escalation rules and required fields.

2) Prompt (copy/paste)
```
<SYSTEM>
You are a customer support agent for ACME Corp focused on billing issues.

<TASK>
Resolve billing questions quickly and professionally. Escalate disputes over $100 or when the customer requests a supervisor.

<CONSTRAINTS>
- Never promise refunds without approval.
- Ask for account email and invoice ID before resolving.
- If the issue is a dispute, label the ticket as "billing_dispute" and escalate.

<OUTPUT FORMAT>
Return a response with:
1) Reply text
2) Escalation flag (true/false)
3) Required follow-up fields
```

3) Assumptions
- Amount threshold is $100.

4) Open questions
- Should escalations include a response SLA?

5) Evaluation plan
- Test with: refund request, dispute >$100, general billing question.

6) Next actions
- Add 2 edge-case examples if disputes are mishandled.

## Scripts and assets

- `scripts/prompt.sh` (wrapper)
  - Usage: `scripts/prompt.sh scaffold "Prompt title"`, `scripts/prompt.sh lint path/to/prompt.md`, `scripts/prompt.sh assets`.
  - Verification: run `scripts/prompt.sh lint path/to/prompt.md` to validate required sections.

- `scripts/optimize-prompt.py` (optional optimizer)
  - Requires: `python3`, `numpy` (local install).
  - Usage: `python3 scripts/optimize-prompt.py` (runs the demo flow).
  - Verification: confirm it writes `optimization_results.json` in the working directory.

- Assets:
  - `assets/prompt-template-library.md`
  - `assets/few-shot-examples.json`

## References

See `references/README.md` for the index and summaries.
