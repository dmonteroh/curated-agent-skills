# Skill System

This repo is a curated set of independent skills.

Some skills act as an "operating system" for agent work (protocols, quality gates, indexing), while others are technology- or domain-specific. The operating system concept lives here (not inside individual skills) so skills remain drop-in and usable on their own.

## Mental model (3 layers)

1) Operating System skills
   - Workflow/protocol skills that organize work, decisions, review, and quality.
   - These should work even if no other skills are present.
   - Brainstorming fits here as an optional “pre-intake” step: clarify intent, explore options, then produce a design brief that can be promoted into a spec/track/ADR later.

2) Tech skills
   - Language/framework/tool specific skills (e.g. Go, TypeScript, PostgreSQL).

3) Domain skills
   - Product/domain specific skills (if present).

## How to compose skills

When multiple skills are available, a good default composition is:

- Use the OS skill to structure the work (brainstorm/clarify -> intake -> plan -> execute -> verify).
- Use a tech skill for implementation details if one exists for the stack.
- Use quality skills (testing, review, security, performance) to add guardrails.

If a tech skill is not available, proceed with best practices and make assumptions explicit rather than blocking.

## Multi-agent composition (optional)

If both are available, a good default is:

- `dispatching-parallel-agents` for partitioning the work into independent domains and generating scope-limited prompts.
- `subagent-driven-development` to execute each domain with verification + review gates.

## Verification culture (system-level)

Across all skills, prefer “evidence before claims”:

- Don’t claim “done”, “fixed”, or “tests pass” without fresh verification output.
- When working via multiple agents, require each agent to report: root cause, files changed, and how they verified.
