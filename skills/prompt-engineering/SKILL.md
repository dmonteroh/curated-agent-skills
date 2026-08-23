---
name: prompt-engineering
description: "Designs, tests, and ships production prompts using prompt-as-code workflows: model-generation-aware patterns (reasoning controls, structured outputs, cache-friendly layout), templates, and evaluation guidance. Returns a full copy/paste prompt block. Use when building AI features, improving agent performance, adapting prompts to a new model or provider, porting an instruction set to another agent harness, or standardizing system prompts."
metadata:
  category: ai
---
# prompt-engineering

Provides one canonical skill that combines:
- **Patterns** (instruction calibration, few-shot, structured outputs, reasoning controls, safety, evaluation)
- **Applied workflows** (define success -> calibrate to model -> draft -> test -> iterate -> deploy/monitor)

## Use this skill when

- Building AI features and agent behaviors (system prompts, tool-use prompts, routing).
- Improving output quality, consistency, safety, or cost/latency.
- Adapting an existing prompt to a new model, provider, or model generation.
- Creating prompt templates and versioned prompt libraries.
- Setting up prompt evaluation / regression tests and eval coverage for LLM-backed units (prompt-as-code).
- Porting an authored instruction set (system prompts, agent instruction files, a prompt library) to a different agent harness.

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

## Context intake

An under-specified request is optimized into a confidently wrong prompt. Before drafting, audit what the request leaves unsaid — each item below is answered in the request, answerable from the code or prior prompts, or missing:

1. Runtime and stack context — what system the prompt runs inside, and what it can call.
2. Target scope — which surfaces, users, or code paths are in play.
3. Acceptance criteria — what a correct output looks like, concretely enough to check.
4. Error handling — what the model does with malformed input, missing data, or a failed tool call.
5. Security and privacy requirements — what must never appear in output; which inputs are untrusted.
6. Testing expectations — which cases must pass before this ships.
7. Performance constraints — latency, token, and cost ceilings.
8. Presentation — format, length, tone, and where the output is consumed.
9. Data and schema changes — what the output feeds, and whether its shape is contracted elsewhere.
10. Existing patterns to follow — prior prompts, house conventions, an established response shape.
11. Scope boundaries — what the model must **not** do.

- Decision: count the items that are both missing and material to this task. At or above the trigger, ask one bounded batch of clarifying questions and stop there rather than drafting; below it, record the gaps under Assumptions and draft anyway. Defaults: trigger at 3 missing items, ceiling of 3 questions — both are chosen defaults, not measured values. The shape is what matters: a trigger and a ceiling, so "ask clarifying questions" cannot expand into an interview.
- Item 11 is the one an unprompted draft almost never contains, and it is not optional here: every prompt this skill emits carries an explicit scope-boundary section written as a short "Do not:" list.

## Workflow

1) Define success
- Action: capture task definition, user impact, failure modes, required format, and metrics.
- Output: a short success checklist (3–6 bullets) and evaluation criteria.

2) Calibrate to the target model
- Decision: reasoning model (built-in extended/adaptive thinking) -> do not add "think step by step" scaffolding; state goal and constraints and control depth via the provider's reasoning setting (names differ per vendor — see `references/frontier-model-prompting.md`). Classic or small model -> chain-of-thought patterns apply (`references/chain-of-thought-basics.md`).
- Decision: if the platform supports schema-enforced structured outputs or strict tool schemas, put the format there and keep the prompt about the task; encode format rules in prose only when no enforcement exists.
- Action: match instruction strength to the model — current models follow instructions literally, so write plain imperatives ("Use X when...") and reserve MUST/NEVER for true invariants. See `references/frontier-model-prompting.md`.
- Output: a one-line model-fit note (recorded under Assumptions).

3) Draft the smallest prompt that could work
- Action: write role + task + constraints + output format + scope boundaries (the "Do not:" list from Context intake).
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
- Decision: if this prompt ships to production rather than answering a one-off, ad-hoc testing is not enough — attach the coverage discipline in "Evaluation coverage" below before deploying.
- Output: test plan and quick pass/fail notes.

7) Iterate in small deltas
- Decision: classify the fix before writing it — wording or sequencing. A wording fix (what the model is told, in what terms) works as prose. A sequencing fix (when a step runs relative to another) does not: a directive placed early in an instruction file cannot be relied on to override an imperative that appears later at the point of action, so a preamble rule to "rank all findings, then ask once" will not beat a per-section "stop and ask" that every section hits on the way past. Put a sequencing fix where the sequence is expressed, as an explicit ordered sequence at the point of execution; rewriting the opening paragraph harder is the standard wasted iteration.
- Decision: if a failure mode persists, change one instruction at a time and re-test.
- Decision: if the model overtriggers a tool or rule, soften the instruction language rather than adding counter-rules.
- Output: a short changelog (what changed, why, expected impact).

8) Deploy with guardrails
- Action: add regression tests, monitoring notes, and rollback guidance.
- Action: pin the model version; when the model changes, re-run the eval suite and de-prescribe legacy scaffolding before tuning further (`references/frontier-model-prompting.md`).
- Decision: on a model change, audit the hedge and style directives already in the prompt *before* writing new ones for the new model. A hedge added to suppress an older model's failure mode was calibrated against loose compliance; a model that follows instructions more literally executes that hedge's wording as written and over-applies it to cases it was never meant to cover. Symptom-triggered, not version-triggered: the audit is owed whenever the new model turns out to be more literal, terser, or narrower than expected.
- Decision: if output looks shallow on a genuinely hard task after a model change, check that the new model was given a comparable reasoning budget before rewriting prompt text — a migration moves the effort scale as well as the model, so the defect may be the setting rather than the wording.
- Output: deployment checklist.

## Patterns

- **Tool descriptions are prompts**: state when to call each tool ("Call this when..."), not just what it does.
- **Explicit scope and motivation**: say where instructions apply and why the task matters; literal models do not generalize unstated intent.
- **Instruction hierarchy**: System > Developer > User > Tool outputs.
- **Progressive disclosure**: start simple, add constraints/examples only when needed.
- **Self-consistency**: where one call is measurably not reliable enough and the answer is discrete and checkable, sample the same prompt n times, take the majority answer, and report the vote share as the confidence signal — an agreement measure, never a calibrated probability. Cost is linear in n; n and temperature are caller choices (`references/eval-coverage.md`).
- **Self-check**: require a short verification pass against constraints — but treat it as the weakest control available, since it asks the model to notice its own miss. Never leave it as the only thing behind a behavior that must hold; a structural assertion in an eval (see "Evaluation coverage") is a different and stronger kind of guarantee.
- **Uncertainty handling**: require explicit "missing info" and questions.

## Evaluation coverage

For any prompt, agent, or tool call that ships to production. Depth, a result-record shape, and the reasoning behind each rule: `references/eval-coverage.md`.

- **Two tiers, minimum.** Every deployed LLM-backed unit carries a *gate eval* that blocks merge or release, and a *periodic eval* that runs on a schedule and catches drift the gate never sees — a provider-side model update, input-distribution shift, an upstream prompt edit. One tier is not coverage: a gate certifies the unit at merge time and says nothing a week later; a periodic run alone lets a regression ship and reports it afterwards.
- **One registry the build checks.** Map each unit to its gate and periodic eval in a single file, and fail the build when a unit has no entry. Otherwise missing coverage is something a person eventually discovers rather than something the build reports.
- **Judgment units assert structure, not output.** Where output is non-deterministic — routing, orchestration, review, anything whose product is a judgment — the must-have is structural compliance: the expected interaction called in the expected shape, the required section order followed, the promised artifact persisted.
- **Label what no eval can cover** as *judgment-dependent, not eval-protected*. That label is a coverage note, not a deletion warrant: unprotected prose is usually the part carrying the judgment, and cutting it because no test covers it removes the behavior instead of testing it.
- **Gate both error directions in one decision** — a floor on catching the thing (detection, recall, correct tool use) and a ceiling on firing wrongly (false positives, overtriggering). A false-positive ceiling on its own passes a build whose detection has collapsed, because a unit that never fires has no false positives. Both thresholds are per-task choices: record them as chosen, with the cost that set them. Where a model judge produces either number, calibrate it first — an uncalibrated judge's own error rates are unknown in both directions.
- **Report intervals, and deltas in percentage points, for both directions.** "Detection −11.1pp, false positives −21.2pp" states a trade a reader can judge; "false positives improved 45%" hides what happened to the other direction. Point estimates without intervals invite chasing noise.
- **Record every knob beside the number** — model and version, prompt version, aggregation or voting rule, confidence floors, timeouts, retries. A result detached from its configuration cannot be reproduced or compared with the next one.
- **Carry a tuning-round counter** in the result record, and pick its ceiling before tuning starts, labelled as a chosen budget rather than a measured optimum. What it reliably buys is the round count living in the record instead of in someone's memory.
- **Split the expensive live run from the cheap CI check.** The live run — real model calls over the full case set — is deliberate and scheduled; CI replays the recorded result deterministically on every build. The replay proves the record is intact, never that live behavior still matches it, so the live run needs a schedule rather than an invitation.

## Porting to another harness

Shipping one authored corpus — system prompts, agent instruction files, a template library — to a second agent runtime is a portability problem distinct from adapting prompt *content* to a different model, and the two usually arrive together. The organizing rule (per-target differences expressed as declarative data, never as branches in the generator), the four rewrite classes, the per-target cross-model boundary warning, the registry collision check, and the test suite parameterized over the registry: `references/harness-porting.md`.

## Output contract

When this skill runs, it always provides the following in order:

1) **Summary**: a one-line summary of what was produced.
2) **Prompt block**: a single copy/paste block with the full prompt text, including its scope-boundary section.
3) **Assumptions**: any assumptions made due to missing inputs, including the assumed target model/generation and the calibration choices that follow from it.
4) **Open questions**: specific questions needed to finalize or improve the prompt, bounded by the Context intake gate.
5) **Evaluation plan**: test cases or metrics to validate quality; for a production unit, the gate/periodic pair and where each is registered.
6) **Next actions**: suggested iterations or deployment steps.

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

## Do not
- Do not quote policy text verbatim; summarize it in the customer's terms.
- Do not discuss other customers' accounts, balances, or history.
- Do not commit to refund amounts, credits, or resolution dates that are not in the account record.
```

3) Assumptions
- Amount threshold is $100.
- Target model is a current frontier reasoning model; if the platform supports structured outputs, move the "Output format" section into a response schema.
- Two intake items were missing and material — error handling for a missing account record, and the latency ceiling. Below the ask-first trigger, so both are assumed here rather than blocking the draft.

4) Open questions
- Should escalations include a response SLA?

5) Evaluation plan
- Test with: refund request, dispute >$100, general billing question, message missing the invoice ID.
- Gate eval: escalation fires on every dispute over threshold (floor) and stays off for the general billing questions (ceiling) — both directions in one gate. Periodic eval: the same set on a schedule, to catch drift after a model or policy change.

6) Next actions
- Add 2 edge-case examples if disputes are mishandled.
- If the agent escalates too eagerly, soften the escalation instruction before adding counter-rules.

## Scripts and assets

- `scripts/prompt.sh` (wrapper)
  - Usage: `scripts/prompt.sh scaffold "Prompt title"`, `scripts/prompt.sh lint path/to/prompt.md`, `scripts/prompt.sh assets`.
  - Verification: `scripts/prompt.sh lint path/to/prompt.md` exits non-zero and names each missing required section. It enforces the scope-boundary rule mechanically — a prompt whose fenced block has no `Do not` / `Scope boundaries` heading fails with `missing scope-boundary section in the prompt block`, and a heading placed outside the fence does not satisfy it.

- `scripts/optimize-prompt.py` (optional eval/optimization harness)
  - Requires: `python3` only (stdlib). Ships with a mock client; wire a real LLM client for actual use.
  - Usage: `python3 scripts/optimize-prompt.py` (runs the demo flow).
  - Verification: confirm it writes `optimization_results.json` in the working directory.

- Assets:
  - `assets/prompt-template-library.md`
  - `assets/few-shot-examples.json`

## References

See `references/README.md` for the index and summaries. When targeting a current frontier model, start with `references/frontier-model-prompting.md` (model-specific notes there are dated — verify against current provider docs when precision matters).
