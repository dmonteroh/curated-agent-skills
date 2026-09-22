---
name: laya-mcp
description: "Calls the local Laya System One model over MCP for a fast, typed, calibrated decision about a piece of text — a label from a fixed set, a level on a fixed ladder, or a yes/no probability — instead of spending an LLM judgment call on it. Use when a classification, routing, or scoring decision needs a probability distribution to act on and the same closed question runs often."
metadata:
  category: ai
---

# Laya decisions over MCP

System One models are a class built to make fast, structured decisions that software can use directly: give one a state and a typed question, and it returns a typed answer and a probability, not prose (TypeSafe AI, "System One" docs, docs.typesafe.ai/concepts/system-one). Laya, from Convai Innovations, is an open-weight entry in that class: a non-autoregressive classifier that runs a single forward pass in tens of milliseconds and generates no text at all (laya.convaiinnovations.com; huggingface.co/convaiinnovations/laya). Three checkpoints ship — a 421M ModernBERT-large English root, a 322M mmBERT-base multilingual variant, and `laya-typed-decisions`, 421M and tuned for agent traces, customer service, invoices and security incidents — and they answer the same questions differently. This skill covers using the `laya_decide` MCP tool an MCP server exposes over Laya, once that tool is already available: `laya_decide(state: str, questions: dict, checkpoint: str | None) -> dict`. There is no other tool and no preset shape — every use of Laya is one `laya_decide` call with a particular `questions` schema.

Reach for it instead of a second LLM call whose only job is to pick a label, grade a level, or answer yes/no about text already in hand.

## Use this skill when

- The answers can be enumerated before asking: routing to one of a few queues, grading severity on a fixed ladder, testing one yes/no claim.
- A number is needed to act on, not an opinion: the probability distribution lets you route above a threshold, escalate below one, or abstain when two options sit close together.
- The question is about a specific piece of text in hand, not about the agent's own reasoning or the wider conversation.
- The same shape of question runs often enough that a warm, sub-second, token-free call beats paying for an LLM's judgment every time.

## Do not use this skill when

- The answer needs generated words: a summary, an explanation, extracted fields, a rewrite. Laya emits no text; `output_tokens` is `0` on every call.
- The options can't be listed in advance. There is no open-ended mode and no invented label.
- Being wrong is expensive and nobody reviews the answer, especially at high option cardinality (see Common pitfalls) — treat a flat or suspiciously spiky distribution as "ask instead of act," not as a resolved question.
- Only one decision will ever be made, and a person or the calling agent can just make the call directly. A cold-loaded call carries real setup overhead (opening a connection, warming the model) that a single one-off judgment doesn't need to pay.
- The input is long free text with no natural closed question inside it — reshape the ask into a stated criteria list first, or don't use Laya for that record.
- The task is deciding whether a model belongs in a text-extraction pipeline at all, or building the deterministic-parser-plus-escalation seam around one — that is a distinct, larger design problem (`deterministic-extraction-gate`).
- The `laya_decide` MCP tool isn't reachable yet, or needs installing, starting, or debugging. This skill assumes the tool is already available and covers using it well — standing up or operating the server behind it is an environment/ops concern outside its scope.

## The tool contract

`state` is the text to judge, in plain natural language. `questions` maps a field name you choose to one question spec; every spec carries `type` and `instructions`, written as the question itself in a short phrase. Put every question a decision needs into one call — they run as one batch, so three questions cost far less than three separate calls. `checkpoint` is optional and names which weights answer. See **Choosing a checkpoint**.

| `type` | `criteria` | Answer fields |
| --- | --- | --- |
| `choice` | required — unique label strings, or a label-to-description map | `choice` (winning label), `probabilities` (label → probability) |
| `score` | required — level labels, lowest first | `score` (expected level index, a fraction from `0` to `len(criteria) - 1`), `legend` (index → label), `probabilities` (index → probability) |
| `noul` | optional — a `{false, true}` description pair | `noul` (probability the statement is true) |

A `choice` or `score` spec with no `criteria` is rejected before any model call runs.

Alongside `answers`, a well-built server returns the facts a caller needs to trust the result: `checkpoint` (which weights answered), `limits` (that checkpoint's `max_len` and `head_max_len`), `route` and `route_reason`, and a `truncation` report. Read `checkpoint`, never `model` — `model` can report a constant such as `laya-rl-agent` across every checkpoint and does not identify the weights. Never hardcode a token budget: read `limits` from the response, because it changes with the checkpoint.

## Choosing a checkpoint

The checkpoints are good at different things, so a server may host several and let the caller pick. Match the checkpoint to the kind of judgment, not to the wording of the question.

| The question is about | Use | Why |
| --- | --- | --- |
| the content of a text in hand — what it says, what it is, what it asks for | the English root | Screening, topical routing and claim-shaped checks are what it was trained on. |
| an agent's own state or trace — did it do the thing, does this match the request | `laya-typed-decisions` | Agent-trace observability is one of its four training workflows, and it carries twice the token budget. |
| text that is not English | the multilingual variant | The English root does not switch by itself. |

Ask the server which names it accepts rather than guessing: a `/health` route or the tool's own schema lists them. When no `checkpoint` is passed the server default answers, and a good server says so in `route_reason` and `route_note` — read those rather than assuming the argument took effect.

Measured on this deployment, one call per question. The English root answered a prompt-injection screen at 0.988 where `laya-typed-decisions` gave 0.674. It scored an exfiltration check at 0.862 where the other gave 0.486, on the wrong side of a half. On agent-trace questions the ordering reversed: the English root asserted that a user had requested a command they had not, at 0.883, while `laya-typed-decisions` returned 0.535 and tripped no gate. Treat the direction as real and the magnitudes as unconfirmed — single calls are reproducible here to four decimals, but one example says nothing about the next.

## Reading the answer

`confidence` is not the winning option's probability. For `choice` and `score` it is normalized entropy over the whole distribution — an even spread reads low even when one option clearly leads. For `noul` it is `max(noul, 1 - noul)` and adds no information beyond `noul` itself. Read `probabilities` (or the `score`/`legend` pair) whenever the decision matters; use `confidence` only as a rough spread indicator.

## Common pitfalls

- **High cardinality collapses the distribution.** Verified in this session: the identical ambiguous ticket text held soft, plausible probabilities at 6 and 10 `choice` options (0.93/0.06 and 0.86/0.12 for the top two labels) but returned an exact `1`/`0` split — full certainty on one label, zero on every other — at 20 and 25 options, on wording a human would call genuinely ambiguous. Convai's own model card reports the same failure mode starting past roughly 20 options (Banking77 benchmark, 0.425 accuracy). Past that range, treat any reported confidence as uninformative rather than as evidence, and bucket into fewer top-level labels before asking, or fall back to escalation.
- **A single-option `choice` always reports confidence `1.0`.** With only one label there is nothing to be uncertain about; the number is an artifact of the format, not a signal — this is what a one-criterion sanity call reproduces every time.
- **Every checkpoint needs calibration for a new domain**, not just a well-worded question, and picking the right one is not a substitute. Convai's own card reports the English root at 0.362 on the typed-decisions benchmark, near chance, against 0.766 for `laya-typed-decisions` — so the checkpoint moves the starting point and never removes the step. Fit a threshold per question against a labelled sample from the real domain, and expect to need roughly 100 labelled rows per question before one holds. Read a distribution near even as "ask instead of act" until a threshold is fitted.
- **Long input is truncated from the end, and the budget is per question.** Each question gets its own budget: `max_len` minus whatever that question's own instructions and rendered options consume. A `choice` with 20 long labels therefore truncates a state that the `noul` beside it reads in full, in the same call. Put what matters first, and do not judge an agent transcript on a checkpoint whose `max_len` it exceeds.
- **A summed token count cannot detect that truncation.** `usage.input_tokens` sums one item per question, so three questions over a short state routinely pass `max_len` with nothing cut. Comparing that sum against `max_len` reports truncation that did not happen. Read the server's per-question `truncation` report instead, which names which fields lost input. Where a server offers no such report, shorten the state rather than inferring from token counts.
- **Truncation changes the answer without looking wrong.** A 1107-token transcript whose decisive line sat at the end scored 0.500 on "did the tests pass" against 0.751 for the same line alone. Nothing in the distribution marks the difference. When a `truncation` report says a field was cut, reorder so the decisive material leads, split the state across calls, or reduce it before asking — do not read the number.

## Examples

**Right-sized call — three questions, ≤4 options each, batched in one call:**

```
state: "I was billed twice this month. Please refund the duplicate charge."
questions: {
  "department": {"type": "choice", "instructions": "Who should handle this?",
                 "criteria": ["billing", "technical", "sales"]},
  "severity":   {"type": "score", "instructions": "How severe is this for the customer?",
                 "criteria": ["trivial", "minor", "major", "critical"]},
  "refund":     {"type": "noul", "instructions": "Does the customer ask for money back?"}
}
```

Verified response from the English root, reproduced identically across separate calls and across a server restart:

```
department → choice "billing", confidence 0.757, probabilities {billing 0.938, technical 0.048, sales 0.015}
severity   → score 1.508 (between "minor" and "major"), confidence 0.133,
             probabilities {trivial 0.114, minor 0.358, major 0.432, critical 0.095}
refund     → noul 0.867, confidence 0.867
```

Read `severity` as the model declining to separate "minor" from "major," not as `1.508` being an answer in itself — a low `confidence` on a `score` question is telling you that directly.

The same call on `laya-typed-decisions` answers `billing` at 0.793 rather than 0.938, `severity` 2.048 rather than 1.508, and `refund` 0.704 rather than 0.867. Both pick the same department. A threshold fitted against one checkpoint does not carry to the other, which is the practical reason to record which checkpoint answered alongside any number you keep.

**Wrong-sized call — the same kind of question, oversized, on the same underlying ambiguity:**

A 20-label routing call over an equally ambiguous support ticket ("app crashed at checkout again, third time this week, thinking about cancelling") returned `confidence 1.0` and a probability of exactly `1` on one label, `0` on the other 19 — even though the text plausibly touches at least three of those labels (a bug report, a churn risk, and a performance issue). Nothing in the response distinguishes this from a genuinely unambiguous case; only knowing the cardinality trap does.

## References

- Laya: laya.convaiinnovations.com, huggingface.co/convaiinnovations/laya, huggingface.co/convaiinnovations/laya-typed-decisions
- System One models: docs.typesafe.ai/concepts/system-one
