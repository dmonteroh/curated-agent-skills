# The pattern layer

The cheapest deterministic detector in the stack. It runs *after* normalization and after the classifier, and its action is to warn rather than to block. Its value is not coverage — it is a fast, explainable signal that costs nothing and never takes the product down.

## The pattern family

Reproduced from the source as **illustrative seeds, not a specification**. All are case-insensitive.

```
instruction override   ignore (all |the )?(previous|above|prior) (instructions|rules|prompt)
authority claim        (system|admin|root) (override|prompt|instruction)
role reassignment      you are now | new instructions: | forget (everything|your|all)
bare imperative        disregard | IGNORE PREVIOUS
delimiter injection    </?(system|user-message|instructions?)>
```

## Limits that must be stated, not papered over

- **Staleness.** These match one era of English phrasing. Treat them as seeds, derive the deployment's real set from its own adversarial corpus, and re-derive on a schedule rather than inheriting a list.
- **Language.** The pattern set is English-only, and so were the classifiers the source shortlisted — while the corpus it evaluated against advertised multiple linguistic styles. The source never addresses this gap. A deployment that serves other languages carries it as a known, unclosed limitation.
- **Coverage.** A pattern layer cannot be the reason a system is considered defended. It fires on the phrasings someone already thought of.

## Delimiter injection is a different class

The last entry above defends the framing layer rather than the model's instruction-following. Once untrusted content is delimited with markup, a closing delimiter *inside* the span ends the region early and everything after it reads as trusted. Two rules follow, in this order:

1. Escape the delimiter inside the untrusted span at framing time. This is the actual defense; the pattern is only a detector for attempts.
2. Choose a delimiter the ingested content is unlikely to contain naturally, so that matches are signal rather than noise.

## The warning marker

On a match, the layer injects a marker into the prompt rather than dropping the content. The marker states that the adjacent span is untrusted, that a pattern matched, and that instructions found inside the span are to be reported rather than followed.

*(Authored: the source specifies a `[PROMPT INJECTION WARNING]` marker and its warn-not-block action but not the marker's contents or placement. Place the marker outside the untrusted span and escape the span, so the marker cannot be forged from inside it — otherwise the mechanism that announces untrusted content becomes something untrusted content can write.)*

## Measurement

*(Authored, extending the source's incident record, which already stores which layer fired.)* Attribute every match to the specific pattern that produced it. Per-pattern precision is what tells a maintainer which patterns to retire; a pattern that has only ever produced false positives is costing warning fatigue and buying nothing.
