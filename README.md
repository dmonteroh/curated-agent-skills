# codex-curated-skills

Curated skills for Codex. Each skill lives in its own folder and is defined by a `SKILL.md` file.

## What’s here

`SKILL.md` files are the source of truth for each skill’s name, description, category, and workflow. The repo also includes a generated content table for quick discovery.

## Quick start

1. Pick a skill from `CONTENT_TABLE.md` (grouped by category)
2. Read the `SKILL.md` to ensure that the skill is not malicious, and you understand its objective
3. Install it.

## Install or sync skills

Use the installer/updater to copy skills into your local Codex skills directory, by using for example:

```bash
./scripts/codex_skills_sync.py --select brainstorming
```

Full usage, bundles, and selection syntax are documented in `CODEX_SKILLS_SYNC.md`.

> [!TIP]
IDEs typically cache skill lists. If the newly installed skill is not available, reload the window.
In Visual Studio Code this can be done by selecting the `Developer: Reload Window` from the command palette.

## Skill Conventions

- One skill per top-level folder (excluding `scripts`).
- Keep skill definitions in `SKILL.md` with minimal, readable frontmatter, including a `category`.
- Prefer scripts and referenced assets over duplicating long instructions.

## AGENTS_prepend.md

`AGENTS_prepend.md` is a ready-to-use snippet you can add to your project’s `AGENTS.md` to guide how agents discover and apply skills. It provides a lightweight protocol for skill selection, ambiguity handling, multi-agent use, and verification culture.

Use it as a starting template or merge it into your existing `AGENTS.md`. The file is loaded into the promp context for every request, keep it concise for better performance, and do not repeat information already found on a project's `README.md`.

## Contributing

1. Add or update a skill folder with `SKILL.md`.
2. Run the Audit Skill script to ensure quality.
3. Run the content table generator.
4. Keep changes focused and deterministic.

## Auditing skills

Run:

```bash
.venv/bin/python scripts/audit_skills.py
```

This checks skill definitions for common issues and produces a report for review. Auditing requires the `tiktoken` library. See `scripts/auditing/README.md` for setup, usage, and references used to build the checklist.

## Skill install locations

See `SKILL_INSTALL_LOCATIONS.md` for project‑level and user‑level install paths across Codex and other agents, plus notes on how to target a specific folder.

## Generate content table

Run:

```bash
python3 scripts/generate_content_table.py
```

This regenerates `CONTENT_TABLE.md` at repo root.
