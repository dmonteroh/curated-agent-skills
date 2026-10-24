# Question design

Use these patterns to design questions for a System One backend. TypeSafe publishes this guidance for Jev at `docs.typesafe.ai`; it applies to Laya by analogy unless a point names a measurement.

- Ask one condition per `noul`. Split “is it urgent and about billing” into two questions. Phrase each so a high value means yes.
- Describe confusable `choice` options. Start with labels. When two options collide, say what each covers and what belongs to its neighbour. Include `other` or `none` so the model need not force-fit.
- Describe `score` levels as situations, such as “blocks a release”, rather than degrees. Keep one dimension per question, lowest level first, with at most 10 levels.
- Keep `state` relevant. The start survives truncation, so name structured parts such as `{"diff": …, "message": …}` instead of concatenating unrelated text.
- For a decision you will act on, compare a `noul` with a two-option `choice` using neutral keys. A `noul` exposes `false` and `true`, which can outweigh the text. On a reproduced Laya example, a clearly positive review read 0.000 as `noul` but 0.74–0.97 as a two-option choice. Keep option order fixed after selecting the better form.
- Compute arithmetic, date ordering, multi-step reasoning, and double negatives in code. Ask the model only for the closed judgment.
- Test wording against examples with known answers. Rewording changes the result.
