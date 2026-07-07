# Prompt Optimization for Efficiency

## Token reduction tactics

- Remove redundant phrases and filler words.
- Consolidate instructions into short bullet lists.
- Use reusable labels (e.g., "Output Format" section).

## Latency reduction tactics

- Minimize prompt length before adding constraints.
- Avoid unnecessary examples when the task is stable.
- Set explicit output length limits when appropriate.

## Cost control checklist

- Track tokens per request and per response.
- Prefer short, high-signal examples.
- Avoid large chains of tool calls unless required.
- Lay repeated prompts out for prefix caching — stable content first, volatile content last; see `prompt-caching-layout.md`. For high-volume prompts this outweighs every phrase-trimming tactic above.
- On reasoning models, tune the API effort/thinking setting before trimming prompt text — reasoning tokens usually dominate cost, and the setting controls them directly.
