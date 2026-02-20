---
name: code-explain
description: "Explain complex code clearly for humans and agents. Produce a structured walkthrough (high-level intent -> data/control flow -> key invariants -> edge cases) with optional Mermaid diagrams and actionable next steps. Use for onboarding, debugging understanding, and “how it works” docs."
metadata:
  category: docs
---
# code-explain

Provides code explanations through clear narratives, diagrams, and step-by-step breakdowns.

This skill is intentionally different from `doc-generate`:
- `code-explain` = explain one subsystem/module/flow extremely well
- `doc-generate` = generate/maintain a documentation set (indexes, runbooks, onboarding, reverse-specs)

## Use this skill when

- Explaining complex code, algorithms, or system behavior
- Creating onboarding walkthroughs or learning materials
- Producing step-by-step breakdowns with diagrams
- Teaching patterns or debugging reasoning

## Do not use this skill when

- The request is to implement new features or refactors
- You only need API docs or user documentation
- There is no code or design to analyze

## Instructions

### Required inputs

- Code scope (file paths, modules, or snippet)
- Goal and audience (onboarding, debugging, review)
- Any constraints (length, diagram preference)

### Workflow (with outputs)

1) **Confirm scope and artifacts**
   - If code references are missing, request them before proceeding.
   - Output: a scoped list of files/components to explain.
2) **Build a high-level mental model**
   - Identify responsibilities, dependencies, and primary entry points.
   - Output: a short outline of components and interactions.
3) **Trace control flow**
   - Walk through the critical execution path step-by-step.
   - Output: ordered flow narrative with key branches.
4) **Trace data flow and invariants**
   - Track data transformations, state changes, and invariants.
   - Output: data movement summary and invariants list.
5) **Surface pitfalls and edges**
   - Note failure modes, tricky conditions, and non-obvious behavior.
   - Output: edge case list with impact notes.
6) **Identify safe change points**
   - Call out extension points, seams, and high-risk areas.
   - Output: change guidance tied to components.
7) **Optional diagram decision**
   - If the flow is multi-step or non-linear, include a Mermaid diagram.
   - Output: a diagram section or a brief note explaining omission.

### Decision points

- If the scope is too broad, propose a narrower focus and wait for confirmation.
- If the user asks for changes or refactors, switch to guidance-only and ask for confirmation before implementation.
- If there is no runnable code, provide a design-level explanation and state assumptions.

### Common pitfalls to avoid

- Mixing explanation with implementation changes.
- Skipping inputs/outputs or invariants.
- Overusing diagrams when a short narrative is clearer.

### Templates (optional)

- `references/explainer-template.md`
- `references/diagram-patterns.md`

## Output Format

### Output contract (deterministic)

Produce a single explainer in this structure:
1) **What it is** (1–3 sentences)
2) **Key inputs/outputs** (APIs, types, DB tables, messages)
3) **Control flow** (step-by-step)
4) **Data flow** (what data moves where; include invariants)
5) **Edge cases and failure modes**
6) **Where to change it safely** (seams / extension points)
7) **Suggested tests** (what would prove behavior)
8) **Next steps** (if the user wants changes)

When useful, include a Mermaid diagram (sequence or flowchart).

### Reporting format

- Scope: `<files/modules>`
- Assumptions: `<if any>`
- Explainer: `<sections 1-8>`
- Diagram: `<mermaid or omitted>`

## Examples

### Example request

"Explain how the auth middleware and session refresh flow work in `src/auth` and `src/session`."

### Example output (abbrev.)

- Scope: `src/auth`, `src/session`
- Assumptions: None
- Explainer:
  1) What it is: ...
  2) Key inputs/outputs: ...
  3) Control flow: ...
  4) Data flow: ...
  5) Edge cases and failure modes: ...
  6) Where to change it safely: ...
  7) Suggested tests: ...
  8) Next steps: ...
- Diagram: Omitted (linear flow)

## Resources

- `references/README.md` for detailed examples and templates.
