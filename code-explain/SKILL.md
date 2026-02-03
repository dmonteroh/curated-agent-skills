---
name: code-explain
description: Explain complex code clearly for humans and agents. Produce a structured walkthrough (high-level intent -> data/control flow -> key invariants -> edge cases) with optional Mermaid diagrams and actionable next steps. Use for onboarding, debugging understanding, and “how it works” docs.
category: docs
---

# code-explain

Explain code through clear narratives, diagrams, and step-by-step breakdowns.

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

## Default output (deterministic)

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

## Instructions

- Assess structure, dependencies, and complexity hotspots.
- Explain the high-level flow, then drill into key components.
- Use diagrams, pseudocode, or examples when useful.
- Call out pitfalls, edge cases, and key terminology.
- If you need templates, open:
  - `resources/explainer-template.md`
  - `resources/implementation-playbook.md` (deeper patterns)

If Mermaid diagrams are needed and the `mermaid-expert` skill is available, prefer it for diagram syntax/pattern quality.

## Output Format

- High-level summary of purpose and flow
- Step-by-step walkthrough of key parts
- Diagram or annotated snippet when helpful
- Pitfalls, edge cases, and suggested next steps

## Resources

- `resources/implementation-playbook.md` for detailed examples and templates.
