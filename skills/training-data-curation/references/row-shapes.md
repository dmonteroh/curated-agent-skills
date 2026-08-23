# Row shapes by training method

The shape each method expects, written as data rather than as any one library's API. Field names are copied exactly; an approximation is either a silent no-op or a mis-parse depending on the trainer, and neither reports itself.

Base models are never named here. Where a checkpoint matters, it is a parameter of the run, not a value in this file.

## Supervised, single-turn

One row per example. Either key pair works — pick one and hold it across the whole set.

```json
{"instruction": "Summarize the following text in one sentence.", "input": "Q3 revenue grew 14% year-over-year, driven primarily by...", "output": "Q3 revenue grew 14% YoY on strong core-segment demand."}
```

```json
{"prompt": "Summarize the following text in one sentence: Q3 revenue grew 14%...", "completion": "Q3 revenue grew 14% YoY on strong core-segment demand."}
```

## Supervised, multi-turn

A message list per row. This is the shape a loss mask can be computed against, because the turn boundaries are still present.

```json
{"messages": [
  {"role": "system", "content": "Answer technical questions concisely."},
  {"role": "user", "content": "What does a key-value cache do?"},
  {"role": "assistant", "content": "It stores attention keys and values from prior tokens so decoding does not recompute them each step."},
  {"role": "user", "content": "Does it grow with context length?"},
  {"role": "assistant", "content": "Yes, linearly — which is why long-context serving is bound by cache memory rather than compute."}
]}
```

Only the two assistant turns' content tokens carry loss after masking.

## Preference pair

```json
{"prompt": "Explain why the sky is blue.", "chosen": "Sunlight scatters off air molecules; shorter wavelengths scatter more, so blue dominates what reaches your eyes from every direction.", "rejected": "Because the sky reflects the ocean."}
```

`chosen` and `rejected` are both complete responses to the same `prompt` — not a diff, not a ranking score, and not responses to two different prompts.

## Unpaired binary feedback

```json
{"prompt": "Draft a one-line commit message for a null-check fix.", "completion": "Fix null pointer exception in user lookup", "label": true}
```

```json
{"prompt": "Draft a one-line commit message for a null-check fix.", "completion": "misc changes", "label": false}
```

No relationship between rows is required or expected. A usable set needs both labels represented.

## Prompt-only, for a checked-reward run

```json
{"prompt": "Solve: 17 * 24 = ?", "answer": "408", "verifier": "exact_match"}
```

No response is stored. The policy generates completions during the run and the named checker scores them against `answer`.

## Applying the template, and the trap under it

Keep the data in message-list shape and let the trainer apply the conversation template per example, before any concatenation. Two properties follow from that and from nothing else:

- Turn boundaries survive, so loss can be masked to response spans.
- The template is applied per example rather than to a concatenated blob, so role markers land where the example boundaries actually are.

**The flat-text path does not mask.** Pre-rendering each conversation into a single text field and pointing the trainer at that field still runs — and computes loss over the *entire* sequence, prompt tokens and role markers included. Nothing errors. It is correct only where full-sequence loss is genuinely intended, such as continued pretraining over raw text, and it is never correct for conversational supervised training.

Rendering the template to a string is still the right tool for *inspecting* what the template produces. That is the decode-and-read check, not the way to build the set.

Where a trainer offers a response-only masking switch, it usually needs the template itself to mark where response spans begin. A template without that marking either raises or trains on everything — find out which before the run, because the second failure is invisible.

## Converting an older conversation format

Older sets often ship with different key and role names for the same structure — a `conversations` list of `from`/`value` objects rather than `messages` of `role`/`content`. Convert to the target shape **before** templating, not during:

```python
ROLE_MAP = {"human": "user", "gpt": "assistant", "system": "system"}

def to_messages(example):
    return {"messages": [
        {"role": ROLE_MAP[turn["from"]], "content": turn["value"]}
        for turn in example["conversations"]
    ]}
```

Then read a handful of converted rows before going further. A set that reaches templating or concatenation still in the old shape produces malformed turns that the template call will not object to.
