# Cache-Friendly Prompt Layout

Production prompts are cacheable artifacts. Major providers cache prompt prefixes (Anthropic prompt caching, OpenAI/Google equivalents), cutting cost and latency dramatically — but only when the prompt is laid out for it. This reference covers designing the prompt so caching works; it is provider-neutral with provider specifics labeled.

## The invariant

**Prefix caching is an exact match. Any byte change anywhere in the prefix invalidates everything after it.** A timestamp interpolated into the system prompt, a reordered JSON key, or a tool added mid-conversation re-processes the entire prompt at full price.

## Order content by stability

Lay the prompt out so the most stable content renders first:

1. **Static, shared across all requests**: role, rules, tool definitions, canonical examples.
2. **Per-session**: user profile, retrieved documents, session config.
3. **Per-turn / volatile**: conversation turns, the current question, dynamic state.

On Anthropic's API the render order is `tools` → `system` → `messages`, so a cache breakpoint on the last system block caches tools and system together.

## Design rules

- **Freeze the system prompt.** Never interpolate "current date: X", "mode: Y", or user names into it. Inject dynamic context late — in a message near the end of the conversation, where it invalidates nothing before it.
- **Serialize deterministically.** Sort JSON keys, sort tool lists by name, never iterate unordered sets into the prompt.
- **Don't swap tools or models mid-conversation.** Tool definitions render first; changing them rebuilds the whole cache. Pass a "mode" as message content instead of swapping the toolset.
- **Templates should separate stable from volatile slots.** A template whose variables all land in the final section caches its entire preamble; one with a variable in the header caches nothing.

## Silent invalidators to grep for

| Pattern | Why it breaks caching |
| --- | --- |
| `datetime.now()` / `Date.now()` in the system prompt | Prefix changes every request |
| Request IDs / UUIDs early in the prompt | Every request is a unique prefix |
| Unsorted dict/set serialization | Non-deterministic bytes |
| Conditional system sections (`if flag: system += ...`) | Every flag combination is a distinct prefix |
| Per-user IDs interpolated into shared instructions | No cross-user cache sharing |

## Verify, don't assume

Check the provider's usage metadata (e.g. Anthropic's `cache_read_input_tokens` / `cache_creation_input_tokens`). Zero cache reads across repeated requests with an identical prefix means a silent invalidator is at work — diff the rendered prompt bytes between two requests to find it.

## Interaction with prompt design

Cache layout is a constraint on *where* content goes, not on *what* the prompt says. Apply it after the prompt works: get correctness first, then reorder for stability without changing semantics, then re-run the eval suite to confirm nothing shifted.
