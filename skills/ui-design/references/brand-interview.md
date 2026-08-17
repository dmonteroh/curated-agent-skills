# Brand Interview (Eliciting a Direction That Does Not Exist Yet)

Use this when the requester has a product but no brand, no tokens, and no reference material — the case where "what should it look like?" returns either silence or a link. The missing input is not a preference, it is a vocabulary: the requester can judge a direction on sight but cannot author one. This file carries the question set, the follow-up for each way an answer fails, the translation from fuzzy answers into design-system parameters, and the rules for the revision loop that follows.

Skip it when a direction already exists — approved tokens, a live product to match, or a direction approved earlier in the same project. Apply that direction instead; re-running the interview invites a second, conflicting answer.

## How to run it

- One question at a time. Stacked questions get one answer covering the easiest of them.
- Keep it short enough that it is finished rather than abandoned. The number of questions is not the constraint; the number of questions the requester has to *think* about is.
- When the requester volunteers material — a README, a product description, an existing site — extract the answers it already contains and ask only the gaps. Asking a question whose answer was just supplied reads as not listening.
- When an answer stalls, offer two or three concrete alternatives to react to instead of waiting for articulation. Recognition is easier than recall, and this is a recall problem.
- Short answers are complete answers. If the answer covers the question, move on.
- Expect the requester to try to skip the whole thing. Push back once, with the reason: with no stated direction, the output converges on the category template.

## Part A — product and purpose

Ask for: the exact name (spelling and capitalisation included), what the product does in terms a non-user would follow, who it is for, and the single action a visitor should take.

Follow-ups for the ways this fails:

- **Answer is too technical** — ask them to explain it to someone who would use it but does not build it: what problem does it solve for that person?
- **Answer is too broad** — ask for the one thing that makes it worth looking at.
- **"Everyone" is the audience** — ask who has shown the most interest so far, or who they would pitch first. If there are no users yet, ask whose problem they were solving when they built it.
- **Several actions are named** — ask which one goes on the biggest button. Multiple primary actions means no primary action.

**Gate:** name, plain-language description, audience, single primary action. Do not advance without all four; every later decision is derived from them.

## Part B — brand feel

Ask for: a small set of adjectives for the impression the product should leave, an admired reference (optional), and a light or dark direction.

Three adjectives is a chosen default — enough to triangulate a feel, few enough to force a choice. Offer a menu when the requester hesitates (bold, clean, minimal, technical, friendly, trustworthy, modern, playful, precise, approachable, sophisticated, sharp, reliable, premium, serious), and accept words that are not on it.

For the admired reference, always ask the second question: *what specifically* about it — the colour, the layout, the density, the copy? An unqualified reference is not actionable, and inferring the answer from the artifact itself carries everything indiscriminately, including the parts they do not want.

Follow-ups for the ways this fails:

- **Contradictory adjectives** ("playful" and "serious") — name the tension and ask which one wins. A contradiction resolved now is a direction; resolved later it is a rewrite.
- **All the adjectives describe the product, not the impression** ("fast", "reliable", "scalable") — ask what impression the surface itself should leave on first sight.
- **"Just make it look professional"** — professional spans opposite systems. Ask for the discriminator: spacious or dense, quiet or assertive.
- **Unsure about light or dark** — name the tradeoff for this audience and let them choose. Do not settle it by assuming what their category "usually" does.

**Gate:** the adjective set and a light/dark direction. The admired reference is a bonus signal, never a blocker.

## Part C — visual preferences

Ask for: existing colours, type character, and shape language.

- **Colour.** Ask first whether colours already exist anywhere — the product UI, docs, a repo, a logo. Existing colours outrank invented ones. If none exist, ask what feeling the colour should carry and translate that to a hue direction rather than asking for a hex. When the answer is a colour name, resolve it to a concrete value against a palette rather than leaving it as a word. When the answer is "black", use a near-black; pure black reads as an unfinished default and crushes every surface level above it.
- **Type.** Ask for character, not names: clean and geometric, or something with more weight and contrast. If they name a monospace for body copy, say what it costs on a marketing surface and offer the alternative — but do not substitute a typeface that design tooling already reaches for by default, since that is convergence with an extra step.
- **Shape.** Sharp or rounded, checked against whatever they already ship.

**Gate:** colour direction, type character, shape language. Then read the entire direction back — name, description, audience, primary action, adjectives, light/dark, colour, type, shape — and get it confirmed before anything downstream depends on it. Corrections are cheap at this point and expensive after.

## Translating answers into parameters

| Interview answer | Becomes |
| --- | --- |
| Adjective set | The overall palette temperature and contrast level, and the aesthetic direction the type and layout are chosen against |
| Light or dark | The base colour mode, and the surface stack that has to be legible in it |
| Existing colour, or a hue direction | The accent token, plus its hover and active steps |
| Type character | The heading and body families, and how much contrast is allowed between them |
| Shape language | The radius scale, applied consistently rather than per component |
| Primary action | What the highest-emphasis component in the system has to be, and where the emphasis ladder starts |

## When the requester insists on skipping

Worked form of the stated-defaults rule — after asking only for the primary action and the intended impression: "Going with a dark theme, a clean sans, rounded corners and a blue accent, since you didn't have a preference. Any of it is changeable once you've seen it."

## Reviewing each round with the requester

Ask for reaction before asking for edits:

1. First reaction, before reading any body copy.
2. Does this read as *their* product?
3. Is anything wrong, missing, or off?

Never ask "do you like it?" — it returns a yes or a no and no information either way.

Someone who does not evaluate visual design for a living needs the dimensions named for them. Point at: whether a visitor can tell what the product does without reading past the first screen; how quickly the primary action was found; whether the colour matches the adjectives they chose; whether the section order makes sense to someone meeting the product for the first time; and whether it looks like a real, maintained product.

## Diagnosing vague feedback

Vague feedback is not a missing opinion; it is an opinion without the vocabulary to place it. Each symptom below has a follow-up that converts it into an axis, which is what the feedback classification in `SKILL.md` needs as input. Ask the follow-up, then act — never act on the symptom.

| Symptom | Likely cause | Follow-up that locates it |
| --- | --- | --- |
| "I don't like it" | Overall mismatch | Is it the colour, the layout, or the mood that feels off? |
| "It's boring" / "too plain" | Low visual energy | More contrast, a bolder layout, or both? |
| "It's too busy" | Visual clutter | Which part — one section, or everywhere? |
| "It looks like a template" | No specificity | What would make it feel like this product — layout, colour, or type? |
| "It's too marketing-y" | Over-decorated for the surface | Strip decoration and raise density? |
| "The colours are off" | Palette mismatch | Too bright, too dull, or the wrong hue? |
| "Make it pop" | Weak hierarchy | What should be seen first — the headline, the action, or the whole page? |
| "Too cramped" / "needs more padding" | Density, reported as CSS | Which region feels tight, and is it between sections or inside them? |

A rollback request ("the earlier one was better") is not vague and needs no diagnosis — retrieve that round rather than reconstructing it.
