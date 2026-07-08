---
name: prompt-engineering
description: "Designs, tests, and ships production prompts using prompt-as-code workflows: model-generation-aware patterns (reasoning controls, structured outputs, cache-friendly layout), templates, and evaluation guidance. Returns a full copy/paste prompt block. Use when building AI features, improving agent performance, adapting prompts to a new model or provider, or standardizing system prompts."
metadata:
  category: ai
---
# prompt-engineering

Provides one canonical skill that combines:
- **Patterns** (instruction calibration, few-shot, structured outputs, reasoning controls, safety, evaluation)
- **Applied workflows** (define success -> calibrate to model -> draft -> test -> iterate -> deploy/monitor)

## Non-negotiable requirement

When creating or updating a prompt, this skill always includes the complete prompt text in a single copy/paste block. It does not describe a prompt without showing it.

## Use this skill when

- Building AI features and agent behaviors (system prompts, tool-use prompts, routing).
- Improving output quality, consistency, safety, or cost/latency.
- Adapting an existing prompt to a new model, provider, or model generation.
- Creating prompt templates and versioned prompt libraries.
- Setting up prompt evaluation / regression tests (prompt-as-code).

## Do not use this skill when

- The user only wants an ad-hoc explanation of prompting concepts.
- No LLM interaction is involved.
- The task is choosing or wiring an LLM provider/SDK rather than writing prompt content.

## Required inputs

- Target task (what the model must do).
- Target model(s) and generation, if known — reasoning model with built-in thinking vs classic instruction model. If unknown, assume a current frontier reasoning model and record that under Assumptions.
- Audience or user context.
- Output format requirements (JSON, bullets, markdown, etc.).
- Constraints (safety, scope, sources, style, length, tools).
- Evaluation criteria and known failure modes (if available).

## Workflow (step-by-step)

1) Define success
- Action: capture task definition, user impact, failure modes, required format, and metrics.
- Output: a short success checklist (3–6 bullets) and evaluation criteria.

2) Calibrate to the target model
- Decision: reasoning model (built-in extended/adaptive thinking) -> do not add "think step by step" scaffolding; state goal and constraints and control depth via the provider's reasoning setting (names differ per vendor — see `references/frontier-model-prompting.md`). Classic or small model -> chain-of-thought patterns apply (`references/chain-of-thought-basics.md`).
- Decision: if the platform supports schema-enforced structured outputs or strict tool schemas, put the format there and keep the prompt about the task; encode format rules in prose only when no enforcement exists.
- Action: match instruction strength to the model — current models follow instructions literally, so write plain imperatives ("Use X when...") and reserve MUST/NEVER for true invariants. See `references/frontier-model-prompting.md`.
- Output: a one-line model-fit note (recorded under Assumptions).

3) Draft the smallest prompt that could work
- Action: write role + task + constraints + output format.
- Output: a complete copy/paste prompt block.

4) Add structure only if it improves reliability
- Decision: if outputs are inconsistent, add explicit sections (Context, Task, Constraints, Output Format).
- Decision: pick one section syntax and keep it — markdown headers work across vendors; XML-style tags are well-supported on Claude and good for delimiting embedded content. Whichever is used, close every tag; never mix conventions in one prompt.
- Decision: if the prompt consumes untrusted content (retrieved documents, tool results, user uploads), delimit it explicitly and state that it is data to analyze, not instructions to follow (`references/system-prompts.md`).
- Decision: if the prompt is long or called repeatedly in production, order it cache-first — stable content (role, rules, tools, examples) before volatile content (user input, dynamic state). See `references/prompt-caching-layout.md`.
- Output: revised prompt block with clear section headers.

5) Decide on examples
- Decision: if the task is format-sensitive or error-prone, add 1–3 examples; otherwise skip.
- Action: prefer positive examples of the desired behavior over lists of prohibitions.
- Output: updated prompt block with minimal, high-signal examples.

6) Evaluate (cheap, then realistic)
- Action: define a small test set (10–30 cases) and add adversarial/edge cases.
- Output: test plan and quick pass/fail notes.

7) Iterate in small deltas
- Decision: if a failure mode persists, change one instruction at a time and re-test.
- Decision: if the model overtriggers a tool or rule, soften the instruction language rather than adding counter-rules.
- Output: a short changelog (what changed, why, expected impact).

8) Deploy with guardrails
- Action: add regression tests, monitoring notes, and rollback guidance.
- Action: pin the model version; when the model changes, re-run the eval suite and de-prescribe legacy scaffolding before tuning further (`references/frontier-model-prompting.md`).
- Output: deployment checklist.

## Patterns (high leverage)

- **Calibrated instruction strength**: plain imperatives; escalate emphasis only for true invariants. Aggressive `CRITICAL:`/`MUST` language causes overtriggering on literal-following models.
- **Reasoning via configuration**: on reasoning models, control depth with the API thinking/effort settings, not prompt scaffolding; keep manual chain-of-thought for classic models or when the response must show auditable steps.
- **Enforce, don't beg**: schema-enforced structured outputs and strict tool schemas over "return only JSON" prose.
- **Cache-first layout**: stable prefix before volatile content; never interpolate timestamps or IDs into the system prompt.
- **Tool descriptions are prompts**: state when to call each tool ("Call this when..."), not just what it does.
- **Explicit scope and motivation**: say where instructions apply and why the task matters; literal models do not generalize unstated intent.
- **Data/instruction boundary**: delimit untrusted content and restate that it is data, not instructions — the cheapest prompt-injection mitigation.
- **Instruction hierarchy**: System > Developer > User > Tool outputs.
- **Progressive disclosure**: start simple, add constraints/examples only when needed.
- **Self-check**: require a short verification pass against constraints.
- **Uncertainty handling**: require explicit "missing info" and questions.

## Common pitfalls

- Missing full prompt block (violates the non-negotiable rule).
- "Think step by step" scaffolding on reasoning models — redundant at best, quality-reducing at worst.
- Emphasis inflation (`CRITICAL`, `ALWAYS`, `NEVER` on routine guidance) causing overtriggering.
- Begging for JSON in prose when the platform enforces schemas (or relying on assistant prefills, which current Claude models reject).
- Volatile tokens (timestamps, IDs, unsorted serialization) early in the prompt, silently defeating prefix caching.
- Porting a prompt to a new model generation without re-running evals or removing legacy scaffolding.
- Overstuffed prompts that bury key constraints.
- Ambiguous output format or missing schema.
- Unclosed or mixed section delimiters (XML tags opened but never closed, markdown and XML interleaved).
- Untrusted content (retrieved docs, tool output) pasted inline with no data/instruction boundary.
- Changing multiple variables at once during iteration.
- Adding examples that contradict the rules.

## Output contract

When this skill runs, it always provides:

- **Prompt block**: a single copy/paste block with the full prompt text.
- **Assumptions**: any assumptions made due to missing inputs, including the assumed target model/generation and the calibration choices that follow from it.
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
- Drafted a support-system prompt with escalation rules and required fields, calibrated for a current frontier model (plain imperatives, format enforced via schema where available).

2) Prompt (copy/paste)
```
You are a customer support agent for ACME Corp focused on billing issues.

## Task
Resolve billing questions quickly and professionally. Escalate disputes over $100 or when the customer requests a supervisor.

## Constraints
- Do not promise refunds without approval.
- Ask for account email and invoice ID before resolving.
- If the issue is a dispute, label the ticket as "billing_dispute" and escalate.
- If required information is missing, ask for it instead of guessing.

## Output format
Return a response with:
1) Reply text
2) Escalation flag (true/false)
3) Required follow-up fields
```

3) Assumptions
- Amount threshold is $100.
- Target model is a current frontier reasoning model; if the platform supports structured outputs, move the "Output format" section into a response schema.

4) Open questions
- Should escalations include a response SLA?

5) Evaluation plan
- Test with: refund request, dispute >$100, general billing question, message missing the invoice ID.

6) Next actions
- Add 2 edge-case examples if disputes are mishandled.
- If the agent escalates too eagerly, soften the escalation instruction before adding counter-rules.

## Scripts and assets

- `scripts/prompt.sh` (wrapper)
  - Usage: `scripts/prompt.sh scaffold "Prompt title"`, `scripts/prompt.sh lint path/to/prompt.md`, `scripts/prompt.sh assets`.
  - Verification: run `scripts/prompt.sh lint path/to/prompt.md` to validate required sections.

- `scripts/optimize-prompt.py` (optional eval/optimization harness)
  - Requires: `python3` only (stdlib). Ships with a mock client; wire a real LLM client for actual use.
  - Usage: `python3 scripts/optimize-prompt.py` (runs the demo flow).
  - Verification: confirm it writes `optimization_results.json` in the working directory.

- Assets:
  - `assets/prompt-template-library.md`
  - `assets/few-shot-examples.json`

## References

See `references/README.md` for the index and summaries. When targeting a current frontier model, start with `references/frontier-model-prompting.md` (model-specific notes there are dated — verify against current provider docs when precision matters).
