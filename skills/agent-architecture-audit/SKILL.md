---
name: agent-architecture-audit
description: "Diagnoses an agent or LLM application whose behavior degraded when the failing layer is unknown: triages the stack layer by layer, records every finding against exactly one layer with a resolvable evidence reference and an evidence grade, ranks by severity, and orders fixes so enforcement moves into code before any prompt is rewritten. Use when the symptom is reported and the cause is not located."
metadata:
  category: ai
---

# Agent Architecture Audit

Provides a layer-triage procedure for an agent or LLM application that used to behave and now does not, where nobody can say which part of the stack broke it. The same model answers correctly when called directly and badly inside the wrapper. The answer in the log is right and the answer the user saw is wrong. A tool the prompt calls mandatory was never invoked. Those are three different layers with three different fixes, and the symptom does not distinguish them.

The audit exists because the default reaction to all three is to rewrite the prompt. That is the cheapest thing to try and the least likely thing to hold: an instruction the model may ignore is not a constraint. So the load-bearing output here is not the finding list — it is the fix order, which puts enforcement in code first and prompt text last.

## Use this skill when

- A shipped agent's behavior degraded, the symptom is describable, and which layer produced it is unknown.
- The same model behaves differently called directly than it does inside the application.
- A tool is declared required in prompt text and the model answers without calling it.
- Logs show a correct answer and the user reports a broken one, or output differs between two delivery surfaces.
- Corrected facts do not stick, or old topics reappear in unrelated sessions, and it is unclear whether history, retrieval, or a compaction artifact is carrying them.
- A prompt layer, tool, memory system, or wrapper was added and previously stable behavior regressed.
- Several agents in one system behave inconsistently on the same underlying model.

## Do not use this skill when

- The failing layer is already identified and the job is to fix it. Each named layer has an owner elsewhere: the trust rules for a store the agent writes and reloads belong to memory governance; pricing and pruning the always-loaded instruction surface belongs to context budgeting; the design of a layer that rewrites tool output on its way into context belongs to output-middleware design; ingress trust boundaries for attacker-controllable content belong to injection defense. This audit's job is to name the layer, not to re-teach any of them.
- One run failed with one error and the task is to find out why. That is debugging a run, not auditing an architecture — a single trace does not establish that a layer is implicated.
- The question is whether a change helped, or which of two agents is better. Measuring an agent from the outside is a matched-pair design with a control arm, blind grading, and a recomputed rollup; it answers a different question and this procedure is not a substitute for it.
- The loop has not been built yet, and the question is whether an unattended repeating run deserves to exist, whether its goal can be settled by a machine, and what stops it running away. That is design-time judgment over a specification. This audit reads a running system — its source, its configuration, and its logs — and produces nothing without them.
- Nothing is readable but the model's output. With no source, no configuration, and no traces there is no layer to assign a finding to, and the report degrades into speculation about a black box. Report the access gap instead.
- It would run as a release checklist. An audit triggered by every release fires on no symptom, has no time window to bound its evidence, and trains readers to skip it.

## Required inputs

- The target system, its entrypoints, and how users reach it.
- The model stack: which models, which providers, and where each is called.
- The symptom stated as a contrast — what the user saw beside what was expected. "It got worse" is not yet a symptom.
- A time window, and what changed inside it: deploys, prompt edits, model or provider changes, new tools, new memory or retrieval paths.
- Read access to source, configuration, logs or traces, and any store the agent writes and later reads back. Name every one of these that is unavailable; an unreadable layer is reported as unaudited, never as clean.

## The layer map

Triage runs over layers, because a symptom is a property of the output and a fix is a property of a layer. Rows marked *routes out* still get named in the diagnosis — the audit says which layer, and the owning discipline says what to do about it.

| # | Layer | What it produces when it fails | Disposition |
| --- | --- | --- | --- |
| 1 | Standing instructions | Conflicting or accreted rules the model silently trades off | Routes out — instruction-surface budgeting |
| 2 | Session history | Turns from earlier in the session re-injected where they do not apply | Audited here |
| 3 | Long-term memory | Cross-session pollution; user corrections overwritten by older assertions | Routes out — memory-store governance |
| 4 | Compaction and distillation | Compressed artifacts re-entering later prompts as if they were facts | Routes out — memory-store governance |
| 5 | Active recall | Re-summarization layers restating context already present | Routes out — instruction-surface budgeting |
| 6 | Tool selection | Wrong tool routed, or a required tool skipped entirely | Audited here |
| 7 | Tool execution | Execution claimed in the answer that never happened | Audited here |
| 8 | Tool interpretation | Correct tool output misread, partially read, or ignored | Audited here |
| 9 | Answer shaping | Structure or format corrupted while composing the final response | Audited here |
| 10 | Delivery and rendering | A valid answer mutated in transport, streaming, or the display surface | Audited here |
| 11 | Hidden repair loops | An undeclared second model pass rewriting the answer before delivery | Audited here |
| 12 | Persistence | Expired state or a cached artifact served back as live evidence | Audited here |

The count is a chosen taxonomy, not a measurement, and the source it comes from makes no claim otherwise. Merge rows a system does not have and add rows it does; what matters is that every finding lands on exactly one of them.

## Workflow

### 1. Scope

Record the target, entrypoints, model stack, symptom contrast, time window, and which layers are in play at all. A system with no persistent store does not get audited for layers 3, 4, and 12; say so rather than reporting them clean.

- Check: every layer in the map is marked in scope, out of scope, or unauditable-for-lack-of-access. A layer with no marking is an omission the report will read as a pass.
- Output: a scope record naming the symptom contrast and the per-layer disposition.

### 2. Collect evidence

Read source, configuration, logs, and any store the agent reads back, looking for a fixed set of shapes. These are stated as search *intents*, not as commands: file layouts, languages, and search tooling differ per system, and a literal command carried from another codebase searches the wrong files and reports a clean result. *(Authored: the source shipped literal commands with hardwired language filters.)*

- Where is a tool requirement expressed? In prompt text only, or is there code that refuses to produce an answer when the call is absent?
- Which model calls happen outside the main agent loop — in fallback handlers, retry paths, formatters, or middleware?
- What admits a fact into a store the agent later reads back, and does a user correction outrank an earlier agent assertion, or merely arrive after it?
- Which paths run a second generation on failure: fallback, retry, repair, re-prompt, "auto-fix"?
- What transforms the answer between generation and delivery, and is any of it lossy?
- Which artifacts are read back as evidence with no freshness or expiry check?

Collect historical traces as well as current state. A defect fixed by a restart is still a defect, and a clean present does not retire a dirty incident inside the time window.

- Check: every shape above is either matched to a location in the system or recorded as searched-and-absent.
- Output: an evidence set, each item addressable as a file and line or a log record.

### 3. Map each finding to exactly one layer

Per finding, record: the symptom as the user experiences it; the mechanism, in one sentence, from cause to observable effect; the single layer where it *originates* — not where it becomes visible; the root cause; an evidence reference that resolves to a file and line or a log record; and an evidence grade.

**Evidence grade** — three values, and the grade decides what the finding is allowed to receive:

| Grade | Meaning | What the finding earns |
| --- | --- | --- |
| `reproduced` | The failure was triggered deliberately and observed | A fix in the plan |
| `traced` | The path is read end to end in source or logs, but not triggered | A fix, with the reproduction named as its first step |
| `suspected` | A pattern matched and nothing confirms it | A reproduction step only — never a fix |

*(Authored. The source declared a `confidence` float from 0.0 to 1.0 that attached no meaning to any value and no threshold at which a finding's disposition changed; a declared field nothing branches on is not evidence handling. The grade replaces it because it branches.)*

A finding that cannot be assigned one layer is two findings, or the evidence for it is not there yet. Both outcomes are better than a finding whose layer is a guess, because the layer is what selects the fix.

- Check: every finding carries all six fields, and the evidence reference resolves when followed. A reference nobody can open is not evidence.
- Output: the finding set, each on exactly one layer.

### 4. Order the fixes, code first

The ladder is fixed. Work down it, and place each finding's remedy at the highest rung that addresses its mechanism.

1. **Code-gate every requirement currently stated only in prompt text.** Enforcement means the path cannot produce an answer without the required call, not that the instruction is more emphatic.
2. **Make hidden repair, retry, and fallback passes explicit, or remove them.** An undeclared second generation is a layer nobody is reviewing.
3. **Remove duplicated context** — the same fact arriving through standing instructions and history and retrieval and a summary. Duplication is what lets stale copies outvote fresh ones.
4. **Fix admission and precedence in any store read back**, so a user correction outranks the assertion it corrects.
5. **Narrow what triggers compaction or summarization**, so material that must survive verbatim is not compressed into an approximation.
6. **Make the delivery path pass-through.** A transport that may rewrite a valid answer is a defect even when it usually does not.
7. **Replace freeform prose between internal stages with a typed structure.** Prose is not a protocol; parsing it is guesswork with a good success rate.
8. **Only now, change prompt text.**

A prompt rewrite is never the whole remedy for a finding whose mechanism is missing enforcement — that restates the defect in bolder type. Where a prompt change is the correct fix (an instruction that genuinely contradicts another), say what makes it correct.

- Check: no finding whose mechanism names an unenforced requirement has a prompt change as its only fix.
- Output: an ordered fix plan, each entry naming its finding, its rung, and the expected effect.

## Severity

| Level | Meaning |
| --- | --- |
| `critical` | The system can confidently produce wrong operational behavior |
| `high` | Correctness or stability degrades often enough to be relied on wrongly |
| `medium` | Correctness usually survives; the path is fragile or wasteful |
| `low` | Cosmetic or maintainability only |

Severity states consequence, not schedule. The source paired each level with a fixed deadline; that mapping is a house convention with no derivation behind it and is not carried. Attach the receiving team's own release cadence instead, and say in the report which cadence was used.

## Decision points

Seven questions that convert a vague report into a layer. Answer them before opening any code; each yes selects where evidence collection starts.

| # | Question | If yes |
| --- | --- | --- |
| 1 | Can the model skip a required tool and still emit an answer? | Layer 6 — the requirement is not code-gated |
| 2 | Does content from an earlier session appear in an unrelated one? | Layer 3 — cross-session pollution |
| 3 | Is the same fact present in standing instructions *and* retrieval *and* history? | Layer 5 — context duplication |
| 4 | Does anything run a second model pass between generation and delivery? | Layer 11 — hidden repair loop |
| 5 | Does the delivered output differ from what the log recorded? | Layer 10 — delivery mutation |
| 6 | Does the answer contradict a tool result present in the same turn? | Layer 8 — tool output misread or ignored |
| 7 | Can the agent's own intermediate reasoning become persistent memory? | Layer 3 — self-poisoning admission path |

## Examples

**The same finding, fixed twice. Symptom:** The assistant answers pricing questions without calling the pricing tool, and the numbers it gives are sometimes stale.

**Wrong — prompt-first.** Finding: "the model ignores the pricing tool." Fix: change the system prompt to state, more emphatically, that the pricing tool must be called first. This restates the defect. The mechanism *is* that a requirement lives only in text the model may weigh against other text; a stronger sentence is the same unenforced requirement.

**Right — code-first.** Finding: symptom, the user receives an unsourced price; mechanism, the pricing route composes its answer from model output alone and never inspects whether the tool result is present in the turn; layer 6, tool selection; root cause, the requirement is expressed in prompt text and no code path depends on the call; evidence, the handler that builds the response, at its file and line, with no reference to the tool result; grade, `reproduced` — the same prompt answered with no tool call on repeated replays. Fix at rung 1: the route returns no answer unless the tool result is present in the turn, and the prompt sentence stays as documentation of a constraint the code now holds. Severity `critical`, because a confidently wrong price is operational behavior.

The difference between the two is not the wording of the finding. It is that the second one cannot silently stop working.

## Output contract

Returned in this order, and no other:

1. **Severity-ranked findings**, highest first, each carrying its six fields.
2. **The layer diagnosis** — which layers are implicated, which are clean, and which were unauditable and why.
3. **The ordered fix plan**, code-first, each entry naming its rung and its expected effect.
4. **What was not covered** — layers out of scope, evidence sources unavailable, and every `suspected` finding listed as open rather than folded into the count.

Do not open with a summary of what is working. If the system is broken, the first line says so.

A machine-readable form of the same report:

```json
{
  "verdict": { "overall_health": "string", "primary_failure_mode": "string", "most_urgent_fix": "string" },
  "scope": { "target": "string", "model_stack": ["string"], "layers": [{ "id": 1, "disposition": "in_scope|out_of_scope|unauditable" }] },
  "findings": [
    {
      "severity": "critical|high|medium|low",
      "symptom": "string",
      "mechanism": "string",
      "layer": 1,
      "root_cause": "string",
      "evidence_refs": ["file:line"],
      "evidence_grade": "reproduced|traced|suspected",
      "recommended_fix": "string",
      "fix_rung": 1
    }
  ],
  "ordered_fix_plan": [{ "order": 1, "finding": "string", "rung": 1, "expected_effect": "string" }]
}
```

## Common pitfalls

- Blaming the model before falsifying the wrapper. The wrapper is the part that changed.
- Blaming memory without showing the contamination path from write to read-back.
- Fixing the layer where the symptom appears rather than the layer it originates in — patching the delivery surface for a hidden repair loop makes the corruption intermittent instead of removing it, and the finding then looks fixed.
- Treating prose passed between internal stages as a protocol, then reporting the parse failure as a model failure.

## Provenance

- **Sourced:** the layer taxonomy, the five wrapper-failure shapes behind the layer table, the four-phase workflow, six of the seven decision-point questions with their consequents, the code-first fix ladder, the severity vocabulary, the report shape, and the rule that a broken system is reported bluntly rather than prefaced with compliments.
- **Authored, marked where they appear:** the evidence grade that replaces the source's uncalibrated confidence float, and its rule that a `suspected` finding earns a reproduction step and never a fix; the one-layer-per-finding rule; search intents in place of literal search commands; the requirement to mark unauditable layers rather than omit them. Decision point 6 is also authored: the source's sixth question restated its first from the other side, and it is replaced here with the only question covering misread tool output. Every `Check:` and `Output:` line under a workflow step is authored — the source names each phase's output in prose and gives nothing that can fail.
- **Not carried:** the source's activation as mandatory on every release, which fires on no symptom; a wall-clock threshold on debugging time, which an agent cannot observe about itself; the fixed severity-to-deadline schedule, which had no derivation; a report-schema namespace private to the source project; and its pointers to tools that do not exist here.
- **Numbers:** none in this procedure is measured. The layer count is a chosen taxonomy and the severity levels are labels, not quantities.
