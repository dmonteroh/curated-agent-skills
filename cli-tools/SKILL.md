---
name: cli-tools
description: Build fast, user-friendly CLI tools with stable command surfaces, predictable output contracts (stdout vs stderr), and cross-platform behavior. Covers subcommands/flags, config precedence, interactive prompts, progress indicators, and shell completions. Use when designing or implementing CLI tools.
category: workflow
---

# CLI Developer

This skill is for designing and implementing command-line tools that are safe to script, pleasant for humans, and stable over time.

## Use this skill when

- Designing a CLI command surface (subcommands/flags/args)
- Implementing argument parsing and validation
- Adding interactive prompts (with non-interactive fallbacks)
- Adding progress indicators, spinners, and TTY-aware colors
- Adding shell completions

## Do not use this skill when

- The task is not a CLI/terminal tool
- You are designing a GUI/web UX

## Non-Negotiable Rules

- **stdout is for primary output** (pipe-friendly). Logs/errors go to **stderr**.
- Always support `--help` and `--version`.
- Make flags consistent across subcommands.
- Validate inputs early; fail fast with actionable errors.
- Never require interactivity in CI: provide flags/env alternatives.
- Disable color/progress when output is not a TTY.
- Handle SIGINT (Ctrl+C) gracefully and exit with standard codes.

## Workflow (Deterministic)

1. Define the command surface and examples.
2. Define output contract (human vs machine; consider `--json`).
3. Define config precedence (flags > env > config > defaults).
4. Implement parsing + validation.
5. Implement core behavior.
6. Polish: help text, errors, completions, TTY behavior.
7. Test: golden `--help`, JSON schema/snapshots, cross-platform smoke test.

## Output Contract (Always)

- A command/flag matrix (what exists and why).
- Output behavior (stdout/stderr + exit codes).
- Validation and error-handling approach.
- Test plan (at least for help and primary commands).

## Resources (Optional)

- End-to-end playbook + CLI spec template: `resources/implementation-playbook.md`
- Design patterns: `references/design-patterns.md`
- UX patterns: `references/ux-patterns.md`
- Language notes:
  - Node: `references/node-cli.md`
  - Python: `references/python-cli.md`
  - Go: `references/go-cli.md`
