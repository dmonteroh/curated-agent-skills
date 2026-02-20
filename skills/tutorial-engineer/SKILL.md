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

## Required Inputs

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
5. **Add exercises and troubleshooting**
   - Include practice tasks and common failure modes with fixes.
   - Output: exercises + troubleshooting section.
6. **Deliver with verification checklist**
   - Provide a final checklist and any assumptions.
   - Output: verification checklist + assumptions list.

**Decision points**

- If inputs are missing (code, repo path, target audience), ask focused questions before drafting.
- If the scope is too large for a single tutorial, propose splitting into modules.
- If examples are non-runnable, label them as pseudo and explain how to validate.

## Constraints

- Avoid assuming network access unless explicitly provided.
- Keep commands safe-by-default and warn about destructive steps.
- Ensure every tutorial step has a verification or expected output.

## References
See `references/README.md` for detailed pedagogy, formats, and writing guidelines.

## Common Pitfalls

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

## Output Contract

Provide the following in order:

1. **Scope summary**: audience, goal, prerequisites.
2. **Objectives**: measurable outcomes and checkpoints.
3. **Tutorial Markdown**: the full walkthrough.
4. **Verification checklist**: how to validate each stage.
5. **Assumptions or open questions**.

## Reporting Format

- Scope:
- Objectives:
- Tutorial:
- Verification:
- Assumptions/Questions:
