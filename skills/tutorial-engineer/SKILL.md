---
name: tutorial-engineer
description: "Creates step-by-step technical tutorials and onboarding guides from code or system requirements when teams need progressive, hands-on learning paths for developers."
metadata:
  category: docs
---
## Use this skill when

- A tutorial, onboarding guide, or workshop is needed
- A progressive, hands-on walkthrough from code or requirements is required
- Complex concepts must be translated into teachable steps

## Do not use this skill when

- The task is unrelated to creating tutorials or learning materials
- A quick answer is enough and a guided learning path is unnecessary
- The request is for documentation types like API reference or changelog

## Required inputs

- Target audience and baseline knowledge
- Desired outcome and scope (feature, workflow, or system)
- Available code, repo path, or requirements to teach from
- Environment constraints or assumptions (tools, OS, access)

## Instructions

1. **Clarify the brief**
   - Capture audience, prerequisites, desired outcome, and available code/resources.
   - Output: a short scope summary and a list of missing inputs (if any).
2. **Define learning objectives**
   - Convert the brief into measurable outcomes and checkpoints.
   - Output: objective list + checkpoint list.
3. **Design the learning path**
   - Order concepts from simple to advanced; map each to a practical step.
   - Output: tutorial outline with section titles and verification points.
4. **Draft the tutorial content**
   - Write steps with commands, code, expected outputs, and explanations.
   - Output: full Markdown tutorial with runnable or explicitly marked pseudo steps.
5. **Add exercises and anticipate failures**
   - Include practice tasks. Place each common failure and its fix inline at the step where it occurs, never in a trailing troubleshooting section.
   - Output: exercises + an inline error-and-fix note on every step that commonly fails.
6. **Deliver with verification checklist**
   - Provide a final checklist and any assumptions.
   - Output: verification checklist + assumptions list.

**Decision points**

- If inputs are missing (code, repo path, target audience), ask focused questions before drafting.
- If the scope is too large for a single tutorial, propose splitting into modules.
- If examples are non-runnable, label them as pseudo and explain how to validate.

## Tutorial document template

A tutorial is learning-oriented: it takes a newcomer from zero to a working result. That is a distinct documentation quadrant in Diataxis, Daniele Procida's documentation framework (`diataxis.fr`), and the shape below is what keeps a document inside it.

```markdown
# [Tutorial title — names what the reader will build or learn]

[Opening paragraph: what they will build, why it is useful, and what they will
understand by the end. Keep it concrete — "You will build a working X that does Y",
not "This tutorial covers X".]

## What you'll need

[Prerequisites: tools, versions, prior knowledge. Link to installation guides.]

## Step 1: [Set up the foundation]

[Start from a clean state. Show every command. Explain what each does on first
encounter, briefly — not a lecture.]

[exact command]

[Brief explanation of what just happened.]

## Step 2: [Build the first working piece]

[Get to a working, visible result as fast as possible.]

...

## Step N: [Final step]

## What you built

[Recap: what the reader now has and what it can do. Link to reference docs for
deeper exploration. Suggest next steps.]
```

**Rules**

- Reach a working, visible result within the first few steps. If the reader has not seen something work early, the tutorial is too slow and they abandon it. (The originating source puts that cut-off at three steps; the figure is a chosen default with no measurement behind it, so treat it as a starting point rather than a gate.)
- Every step produces a visible change or output. No "now configure X" without showing what changed.
- Use the exact commands the reader will type. No "run the appropriate command" abstractions.
- Where a step commonly fails, show the error and its fix inline rather than deferring it to a troubleshooting section.
- End with "What you built", connecting the walkthrough back to the real use case.
- Carry no "Configuration" section. An exhaustive options or settings listing is reference material; a tutorial that grows one has stopped being a tutorial and should be split, with the tutorial linking out to the reference doc.

## Constraints

- Avoid assuming network access unless explicitly provided.
- Keep commands safe-by-default and warn about destructive steps.

## References
See `references/README.md` for detailed pedagogy, formats, and writing guidelines.

## Common pitfalls

- Skipping prerequisites or setup steps
- Introducing concepts before they are explained
- Including code that cannot run without context
- Missing verification steps for each section
- Overloading a step with too many changes

## Examples

**Example input**

"Create a step-by-step tutorial to add OAuth login to our Node.js app. The repo is in apps/web, and the audience knows Express but not OAuth."

**Example output excerpt**

"Step 2: Register the OAuth callback route. Update apps/web/src/auth.ts with the callback handler. Run `npm test auth` and confirm the test output includes `OAuth callback registered`."

## Output contract

Provide the following in order:

1. **Scope summary**: audience, goal, prerequisites.
2. **Objectives**: measurable outcomes and checkpoints.
3. **Tutorial Markdown**: the full walkthrough, including the practice exercises and the inline error-and-fix notes.
4. **Verification checklist**: how to validate each stage.
5. **Assumptions or open questions**.
