# Per-quadrant document templates

One template per Diataxis quadrant, with the rules that govern it. Diataxis is Daniele Procida's documentation framework (`diataxis.fr`); the quadrant names are its terms. Use these when filling a gap found by the coverage pass in `SKILL.md`, and write them in dependency order: reference, explanation, how-to, tutorial.

The single rule that spans all four: one quadrant per file. A document that carries two quadrants serves neither reader, because the two readers arrive with different questions and skim past each other's material.

## Reference

Reference docs are the foundation and are written first, because they fix the vocabulary every other document reuses. They are factual, complete, and derived directly from code.

```markdown
# [Entity name]

[One paragraph: what it is, what it does, when you would use it.]

## API / Interface

[Complete listing of the public surface: functions, commands, config options,
parameters. Include types, defaults, and constraints. Pull directly from code —
do not paraphrase loosely.]

## Options / Configuration

[If applicable: every option with its type, default, and effect.]

## Examples

[Two or three concrete examples showing actual usage. Prefer real command output,
or code that would actually compile and run.]

## Related

[Links to the reference docs, how-tos, and explanations that provide context.]
```

Rules:

- Accuracy over elegance. Every claim must be traceable to code.
- Include types, defaults, and constraints. "Accepts a string" is insufficient; "accepts a string (max 256 characters, must match `^[a-z-]+$`)" is reference-grade.
- Show real examples that would work if copy-pasted.
- Do not explain *why*. Rationale belongs in an explanation doc, and importing it here is the most common way a reference doc stops being scannable.

## Explanation

Explanation docs answer "why does this work this way?" They carry the design rationale, and they are the quadrant that rots fastest because nobody writes one unprompted.

```markdown
# [Concept or design decision]

[Opening paragraph: the problem this design solves, stated in terms a smart reader
who has not seen the code would understand.]

## The problem

[Concrete description of what goes wrong without this design. Real failure modes,
not abstract risks.]

## The approach

[How the design solves the problem. Include a diagram for architectural concepts.]

## Trade-offs

[What was given up. Every design decision trades something — name it explicitly.]

## Alternatives considered

[What was tried or rejected, and why, where that is discoverable from code comments,
ADRs, or git history.]
```

Rules:

- Lead with the problem, not the solution.
- Name trade-offs explicitly. "We chose X over Y because Z" is the gold standard; a trade-offs section with no loss named in it has not found the trade-off yet.
- Mine code comments, ADRs, and git history for the alternatives that were rejected. The rejected option and its reason are the part a reader cannot reconstruct from the code, and the part that stops the same debate from reopening.
- Prefer diagram formats that are greppable and diff-friendly, so the diagram survives review like the rest of the doc.
- Do not repeat reference material; link to it.

## How-to

How-tos are task-oriented. They assume the reader knows the basics and wants to accomplish one specific thing.

```markdown
# How to [accomplish specific task]

[One sentence: what this achieves and the end result.]

## Prerequisites

[What the reader needs before starting. Be specific — versions, installed tools,
config state.]

## Steps

1. [Action verb] [specific instruction]

   [exact command]

   [Expected output or result, if non-obvious.]

2. [Next step...]

## Verification

[How to confirm it worked: a command, a URL to visit, a test to run.]

## Troubleshooting

[Common failure modes and their fixes. Pull these from tests and error-handling code.]
```

Rules:

- The title starts with "How to". It is the reader's entry point and the thing they scan a doc index for.
- Every step is actionable. Not "consider whether…", but "Run X" or "Add Y to Z".
- Verification is not optional. The reader should never be left wondering whether it worked.
- A troubleshooting section is mandatory whenever the task can fail.

## Tutorial

Tutorials are learning-oriented: they take a newcomer from zero to a working result. They are written last, and they are the hardest of the four to write well.

The structural constraints that keep a document inside this quadrant:

- It reaches a working, visible result in the first few steps. If the reader has not seen something work early, the tutorial is too slow and they leave. (The originating source sets that cut-off at three steps; that figure is a chosen default with no measurement behind it — treat it as a starting point, not a gate.)
- Every step produces a visible change or output.
- It carries no "Configuration" section. An exhaustive options list is reference material, and a tutorial that grows one has drifted out of its quadrant — split it.

## Cross-quadrant verification

Before landing a generated set, sweep for broken links between the quadrant files: match the markdown link shape across the docs tree and confirm every target resolves to a file that exists.

```bash
grep -rE '\]\([^)]*\.md\)' docs/
```

A quadrant split multiplies the links between documents, so this sweep catches the failure the split introduces.
