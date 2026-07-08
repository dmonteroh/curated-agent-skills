# Prompting Frontier Reasoning Models

Guidance for current-generation reasoning models — models with built-in (extended/adaptive) thinking and strong literal instruction-following, such as the Claude Opus 4.x / Sonnet 4.6+ / Claude 5 families and comparable OpenAI/Google reasoning models. For older or smaller instruction models, the classic techniques in the other references still apply.

> **Time-sensitive**: model behaviors and API parameters below were verified as of mid-2026 and drift with each release. When precision matters, verify against the provider's current documentation before shipping.

## The core shift: literal, precise instruction-following

Frontier models follow the prompt much more closely than earlier generations. Prompts written to *overcome* old-model reluctance are now too aggressive and cause overtriggering.

| Written for older models | Write for frontier models |
| --- | --- |
| `CRITICAL: You MUST use this tool when...` | `Use this tool when...` |
| `Default to using [tool]` | `Use [tool] when it would improve X` |
| `If in doubt, use [tool]` | *(delete — no longer needed)* |
| `NEVER do X. EVER. This is EXTREMELY important.` | `Do not do X.` (reserve MUST/NEVER for true invariants) |

Consequences of literalism:

- **State scope explicitly.** The model will not silently generalize an instruction from one item to another ("Apply this formatting to every section, not just the first one").
- **Holdover directives now apply at face value.** A "be concise" line added to tame an older chatty model may over-compress on a new one. Re-baseline style/tone/length directives when changing models instead of carrying them forward.
- **Over-filtering instructions suppress output.** A review prompt saying "only report high-severity issues" is followed faithfully — the model finds the issues, then declines to report them. When coverage matters, ask for everything with confidence/severity attached and filter downstream.
- **Positive shaping beats prohibition.** Examples of the desired behavior outperform lists of don'ts; when a don't is needed, pair it with the do ("Do not narrate routine actions; write one sentence when you find something or change direction").

## Reasoning: configure, don't scaffold

Reasoning models think before answering in a dedicated thinking phase controlled by API parameters, not by prompt text.

- **Skip manual chain-of-thought cues.** "Think step by step", forced numbered-reasoning sections, and tree-of-thought scaffolding are redundant on reasoning models and can reduce quality by constraining the model's own (better) reasoning process.
- **Control depth with the API knob, not prose.** If reasoning is too shallow, raise the setting before adding "think carefully" prose; if too slow or verbose, lower it before adding "be brief" prose. The knob is provider-specific (names as of mid-2026):

  | Provider | Reasoning control |
  | --- | --- |
  | Anthropic (Claude 4.6+ / 5) | `thinking: {"type": "adaptive"}` + `output_config.effort` (`low`…`max`); fixed `budget_tokens` removed on Opus 4.7+ / Sonnet 5 |
  | OpenAI (o-series / GPT-5 era, incl. Codex) | `reasoning` effort setting (minimal…high); separate verbosity control for output length |
  | Google (Gemini 2.5+) | thinking budget / dynamic thinking config |

- **Keep CoT scaffolding when it still earns its place**: non-reasoning or small models, or when the visible response itself must contain auditable intermediate steps (compliance, education, grading). See `chain-of-thought-basics.md`.
- **Sampling parameters may not exist.** `temperature`/`top_p`/`top_k` are rejected on the newest Claude models. For output variety, prompt for it explicitly — e.g. have the model propose 3–4 distinct directions and pick one — rather than relying on sampling randomness.

## Output format: enforce, don't beg

- **Prefer platform-level structured outputs** (JSON-schema-constrained responses, strict tool schemas) over prose like "Return only valid JSON, no markdown". Schema enforcement is guaranteed; prose pleading is not. Keep the prompt about the task; put the format in the schema.
- **Assistant prefills are gone on current Claude models** (last-assistant-turn prefill returns an error on Claude 4.6+). Replace: forced JSON → structured outputs; forced label → enum-typed tool/schema field; skipped preamble → system-prompt instruction ("Respond directly without preamble"); continuation → move into the user turn.
- Only encode format rules in prose when no enforcement mechanism exists — then include one format-perfect example.

## Agentic and tool-use prompting

- **Put invariants in the operator layer.** Anthropic calls it the `system` prompt; OpenAI-style APIs call it the `developer` message. Same hierarchy either way — system/developer > user > tool output. Rules that must survive the whole conversation belong there, not in a user turn.
- **Tool descriptions are prompts.** Prescriptive trigger conditions ("Call this when the user asks about current prices or recent events") measurably raise correct tool use over descriptions that only state what the tool does. Current models are conservative about reaching for tools, subagents, and memory — say *when* each capability applies, in the tool's own description and in the system prompt.
- **Full task spec up front.** One well-specified opening turn (task, intent, constraints, what "done" looks like) outperforms drip-feeding requirements across turns on both quality and token efficiency.
- **Calibrate autonomy explicitly.** "For minor choices (naming, defaults, equivalent approaches), pick a reasonable option and note it rather than asking. For scope changes or destructive actions, ask first." Uncalibrated frontier models either ask too often or overreach.
- **Remove forced-progress scaffolding.** "After every 3 tool calls, summarize progress" was needed on older models; current models narrate well by default. If narration is too chatty, set a silence-default ("Only write text when you find something, change direction, or hit a blocker — one sentence each").
- **Scope the work.** To prevent unrequested refactors/cleanup at high reasoning effort: "Don't add features, abstractions, or error handling beyond what the task requires. Do the simplest thing that works."
- **Give the reason, not just the request.** "I'm working on [larger task] for [who]. They need [what the output enables]. With that in mind: [request]." Models connect the task to relevant context instead of guessing intent.

## Migrating prompts between model generations

1. **De-prescribe first.** Step-by-step scaffolding written for older models often *reduces* output quality on frontier models. A/B the workload with the scaffolding removed; prefer stating goal + constraints over enumerating steps.
2. **Dial back emphasis** per the table above; fix overtriggering by softening language, not by adding counter-rules.
3. **Re-run the eval suite** (see `prompt-optimization-workflow.md`) — never assume a prompt ports cleanly. Change one instruction at a time and re-test.
4. **Distinguish required from tuned.** API-breaking changes (removed parameters, prefill removal) must change; style/behavior prompt edits are judgment calls to be validated, not blindly applied.

## Claude-specific quick notes (dated: mid-2026 — verify before relying on)

- Adaptive thinking (`{"type": "adaptive"}`) is the only thinking mode on Opus 4.7/4.8 and Sonnet 5; on Sonnet 5 it is on by default when the parameter is omitted.
- `effort: "high"` is the general default; `"xhigh"` is recommended for the hardest coding/agentic work; sweep levels on an eval set rather than assuming more is better.
- Mid-conversation `role: "system"` messages (Opus 4.8) inject operator instructions without invalidating the cached prefix — phrase them as context, not overrides.
- Long single turns are normal at high effort — plan timeouts, streaming, and progress UX accordingly.
