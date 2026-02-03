# Skill Review Checklist

Use this checklist to keep skills consistent with AGENTS_prepend.md, the provided PDF guidance, and common best practices.

**Discovery**
- YAML frontmatter includes `name`, `description`, and `category`.
- `name` matches folder name and uses lowercase with hyphens.
- `description` states what the skill does and when to use it, with key terms.
- Token budget for `name` + `description` stays within soft/hard limits.

**When To Use**
- Includes a clear “Use this skill when” section.
- Includes a “Do not use this skill when” boundary.
- Lists trigger phrases or explicit activation cues.

**Instructions**
- Step-by-step workflow with outputs for each step.
- Decision points are explicit (if X, do Y).
- Covers common mistakes or pitfalls.
- Avoids time-sensitive guidance unless clearly labeled as such.

**Examples & Output**
- Concrete examples or input/output pairs.
- Output contract section describing what the agent must report.
- Consistent reporting format when the skill runs.

**Multi-Agent + SDD Alignment**
- Mentions spec-driven development artifacts when relevant.
- Includes cross-linking guidance (spec/track/task ↔ outputs).
- Encourages `dispatching-parallel-agents` + `subagent-driven-development` when tasks can be partitioned.
- If ambiguous or high-risk, calls for the brainstorming loop.

**Scripts & References**
- References are local and one level deep.
- Scripts have explicit usage and verification steps.
- Required packages are listed if scripts need them.
- No network assumptions unless explicitly required.

**Size & Progressive Disclosure**
- SKILL.md stays concise (prefer < 500 lines).
- Deep reference material is moved to `references/`.
