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
- Includes activation cues in `scripts/auditing/trigger-cases/<skill>.md` (not in `SKILL.md`).

**Instructions**
- Step-by-step workflow with outputs for each step.
- Decision points are explicit (if X, do Y).
- Covers common mistakes or pitfalls.
- Avoids time-sensitive guidance unless clearly labeled as such.
- Keeps the skill **independent**: do not require other skills to be installed to follow the instructions.
- Avoid persona/voice shifts. Skills are tools, not agent identities.
- Use third-person, tool-style descriptions (e.g., “Provides…”, “Produces…”, “Use this skill to…”), not “You are…” or “I can…”.

**Examples & Output**
- Concrete examples or input/output pairs.
- Output contract section describing what the agent must report.
- Consistent reporting format when the skill runs.

**Multi-Agent + SDD Alignment**
- Optional: If a skill inherently spans multiple domains, it **may** mention partitioning or parallelization, but only if it remains self-contained.
- Do **not** require other skills (e.g., brainstorming) as prerequisites inside a skill. Cross-skill workflow belongs in higher-level agent instructions (e.g., AGENTS.md).

**Scripts & References**
- References are local and one level deep.
- Scripts have explicit usage and verification steps.
- Required packages are listed if scripts need them.
- No network assumptions unless explicitly required.

**References & Decomposition**
- If any reference/playbook is long, split it into smaller, purpose‑built files (by phase, role, or task).
- Add a short `references/README.md` (or equivalent index) when:
  - There are **2+ reference files**, or
  - A single reference is **large** (roughly >1200 tokens) or clearly multi‑topic.
- Keep `SKILL.md` concise; move deep detail into `references/` and point to the index.
- Ensure references are scoped to the skill and don’t duplicate other skills’ instructions.
- References should be tool‑style and neutral (no persona/voice shifts, no project‑specific flair).

**Size & Progressive Disclosure**
- SKILL.md stays concise (prefer < 500 lines).
- SKILL.md stays under ~5000 tokens (soft target), with warnings above 4500 and a hard limit at 5000.
- Deep reference material is moved to `references/`.

**Operational Quality**
- Assume no prior context: include required inputs, constraints, and the expected output.
- Prefer instructions over scripts unless automation is necessary.
- Keep trigger test prompts outside `SKILL.md`. Use `scripts/auditing/trigger-cases/<skill>.md` for positive/negative activation tests.
