# codex-curated-skills

Curated skills for Codex. Each skill lives in its own folder and is defined by a `SKILL.md` file.

## What’s here

`SKILL.md` files are the source of truth for each skill’s name, description, and workflow. The repo also includes a generated content table for quick discovery.

## Quick start

1. Pick a skill from `CONTENT_TABLE.md`
2. Read the `SKILL.md` to ensure that the skill is not malicious, and you understand it's objective
3. Install it.

## Install or sync skills

Use the installer/updater to copy skills into your local Codex skills directory, by using for example:

```bash
./scripts/codex_skills_sync.py --select brainstorming
```

Full usage, bundles, and selection syntax are documented in `CODEX_SKILLS_SYNC.md`.

> [!TIP]
IDEs typically cache skill lists, if the newly installed skill is not available, reload the window.
In Visual Studio Code this can be done by selecting the `Developer: Reload Window` from the command palette.

## Skill Conventions

- One skill per top-level folder (excluding `scripts`).
- Keep skill definitions in `SKILL.md` with minimal, readable frontmatter.
- Prefer scripts and referenced assets over duplicating long instructions.

## Contributing

1. Add or update a skill folder with `SKILL.md`.
2. Run the Audit Skill script to ensure quality.
3. Run the content table generator.
4. Keep changes focused and deterministic.

## Generate content table

Run:

```bash
python3 scripts/generate_content_table.py
```

This regenerates `CONTENT_TABLE.md` at repo root.
