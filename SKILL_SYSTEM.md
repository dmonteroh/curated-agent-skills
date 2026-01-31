# Skill System

This repo is a curated set of independent skills.

Some skills act as an "operating system" for agent work (protocols, quality gates, indexing), while others are technology- or domain-specific. The operating system concept lives here (not inside individual skills) so skills remain drop-in and usable on their own.

## Mental model (3 layers)

1) Operating System skills
   - Workflow/protocol skills that organize work, decisions, review, and quality.
   - These should work even if no other skills are present.

2) Tech skills
   - Language/framework/tool specific skills (e.g. Go, TypeScript, PostgreSQL).

3) Domain skills
   - Product/domain specific skills (if present).

## How to compose skills

When multiple skills are available, a good default composition is:

- Use the OS skill to structure the work (intake -> plan -> execute -> verify).
- Use a tech skill for implementation details if one exists for the stack.
- Use quality skills (testing, review, security, performance) to add guardrails.

If a tech skill is not available, proceed with best practices and make assumptions explicit rather than blocking.
