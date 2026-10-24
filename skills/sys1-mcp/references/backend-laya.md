# Laya backend

Read this when `sys1_health` names a Laya backend (`laya-mlx` or an in-process Laya). Every number is from one deployment's Laya checkpoints with small hand-labelled sets: enough to pick a route, not to set a threshold. Another backend does not inherit them.

## Checkpoints

Laya, from Convai Innovations, is an open-weight, non-autoregressive classifier: one forward pass in tens of milliseconds, no generated text (laya.convaiinnovations.com, huggingface.co/convaiinnovations/laya). Three checkpoints ship: a 421M ModernBERT-large English root, a 322M mmBERT-base multilingual variant, and 421M `laya-typed-decisions`, tuned for agent traces, customer service, invoices, and security incidents. They answer the same questions differently.

| The question is about | Use | Why |
| --- | --- | --- |
| the content of a text in hand: what it says, what it is, what it asks for | the English root | Screening, topical routing and claim-shaped checks are what it was trained on. |
| an agent's own state or trace: did it do the thing, does this match the request | `laya-typed-decisions` | Agent-trace observability is one of its four training workflows, and it carries twice the token budget. |
| text that is not English | the multilingual variant | The English root does not switch by itself. |

On Laya, `base` is accepted for the English root. On 52 hand-labelled screening examples the English root ranked attacks above clean text with AUC 0.83 against 0.80 for `laya-typed-decisions`, and beat it on every question wording tried. On a 12-probe exfiltration check the order reversed, and neither separated true from false. Single-call comparisons made before these sets existed did not hold up: one example says nothing about the next.

## Label count

From 11 `choice` labels, the probabilities stop meaning anything. Both checkpoints' calibration table (`rl_agent_config.json`, `temperature_by_options`) applies temperature 0.1006 to any `choice` with 11 or more options, a tenfold sharpening. Adding one irrelevant 11th label took a soft 0.65 answer to exactly 1.000. The same ambiguous ticket held 0.93/0.06 at 6 labels and 0.86/0.12 at 10, then an exact 1/0 at 20 and 25. The server attaches a `warning` to such answers. Keep `choice` to 10 labels or fewer, bucket into top-level labels first, or trust only the label.

Wrong-sized call: a 20-label routing call on "app crashed at checkout again, third time this week, thinking about cancelling" returned `confidence 1.0`, probability exactly `1` on one label and `0` on the other 19, though the text plausibly touches bug report, churn risk and performance issue. Nothing in the response separates this from an unambiguous case.

## Token budgets and truncation

- Options share the checkpoint's `head_max_len`. Once they overflow it, every option is cut to an equal share and the question text to as few as 8 tokens, with no error. Described labels hit this at 12 options on a 512-token checkpoint and 16 on a 1024-token one. `truncation.prefix_truncated` reports it.
- Input is cut from the end, and the budget is per question: `max_len` minus what that question's own instructions and rendered options consume. A `choice` with 20 long labels truncates a state that the `noul` beside it reads in full, in the same call.
- `usage.input_tokens` sums one item per question, so three questions over a short state routinely pass `max_len` with nothing cut. Comparing that sum against `max_len` reports truncation that did not happen; read the per-question `truncation` report.
- A 1107-token transcript whose decisive line sat at the end scored 0.500 on "did the tests pass" against 0.751 for the same line alone.

## Screening

`sys1_screen` figures on the English root (`truncation_checked: false` means chunks were sized on an estimate):

- On the 52-example set, `directed` was right 42 times in 52 at 0.5 (AUC 0.83); `injection` AUC 0.84. It missed quiet attacks (an issue telling "the assistant" to close other issues, a footnote addressed to LLMs, a polite request to skip review) and fired on clean text that discusses AI or gives a human install steps.
- On 116 public prompts (deepset/prompt-injections), `directed` and `injection` ranked injections above clean prompts well (AUC 0.91 and 0.96), yet at 0.5 each caught fewer than half.
- A 1,428-token page with an attack in its last sentence scored 0.084 through `sys1_ask`, which cut it to 512 tokens, and 0.969 through `sys1_screen`.
- `harm` runs high on clean text, about 1.4 of 3.
- Text over about 28k tokens is refused.

## Reference answers

The English root on the billing example in `SKILL.md`, identical across calls and a server restart: `department` billing 0.938 (confidence 0.757); `severity` 1.508, probabilities trivial 0.114, minor 0.358, major 0.432, critical 0.095; `refund` 0.867. `laya-typed-decisions` gives billing 0.793, severity 2.048, refund 0.704. Both pick the same department; a threshold fitted on one checkpoint does not carry to the other.

On Laya, every checkpoint needs calibration for a new domain. Convai's card reports the English root at 0.362 on the typed-decisions benchmark, near chance, against 0.766 for `laya-typed-decisions`.
