---
name: cli-tools
description: Build fast, user-friendly CLI tools with stable command surfaces, predictable output contracts (stdout vs stderr), and cross-platform behavior. Covers subcommands/flags, config precedence, interactive prompts, progress indicators, and shell completions. Use when designing or implementing CLI tools.
category: workflow
---

# CLI Tools Skill

Provides guidance for designing and implementing command-line tools that are safe to script, pleasant for humans, and stable over time.

## Use this skill when

- Designing a CLI command surface (subcommands/flags/args)
- Implementing argument parsing and validation
- Adding interactive prompts (with non-interactive fallbacks)
- Adding progress indicators, spinners, and TTY-aware colors
- Adding shell completions

## Do not use this skill when

- The task is not a CLI/terminal tool
- You are designing a GUI/web UX

## Trigger phrases

- "design a CLI"
- "add flags" / "subcommands"
- "command line interface"
- "add --help" / "--version"
- "make this script a CLI tool"

## Required inputs

- Target language/runtime and packaging constraints
- User personas (human, automation, or both)
- Expected output formats (human text, JSON, files)
- Platform constraints (OS, shell, terminal limitations)

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
   - Output: command/flag matrix draft with brief intent.
2. Define output contract (human vs machine; consider `--json`).
   - Output: stdout/stderr expectations and exit code table.
3. Define config precedence (flags > env > config > defaults).
   - Output: precedence list and config locations.
4. Implement parsing + validation.
   - Output: validation rules and error messages.
5. Implement core behavior.
   - Output: primary command behaviors with success/failure paths.
6. Polish: help text, errors, completions, TTY behavior.
   - Output: updated help/usage strings and TTY checks.
7. Test: golden `--help`, JSON schema/snapshots, cross-platform smoke test.
   - Output: test list with owners and expected results.

## Decision points

- If the CLI is used in automation, default to machine-readable output and add `--format`.
- If the command can be destructive, require confirmation or `--yes` for non-interactive runs.
- If interactive prompts are needed, always provide flag/env fallbacks.

## Common pitfalls

- Mixing logs with primary output (breaks piping).
- Inconsistent flags across subcommands.
- Prompting in CI or non-TTY environments.
- Non-deterministic output ordering (breaks tests).

## Output Contract (Always)

- A command/flag matrix (what exists and why).
- Output behavior (stdout/stderr + exit codes).
- Validation and error-handling approach.
- Test plan (at least for help and primary commands).

## Examples

**Example: add a new subcommand**

Input
```
Add a "list" subcommand that outputs JSON for automation.
```

Output
```
- Command matrix: list [--json] [--limit]
- stdout: JSON array when --json, table otherwise
- stderr: validation/errors only
- exit codes: 0 success, 2 validation, 1 runtime
```

## Reporting format

```
Summary:
- Command/flag matrix
- Output behavior and exit codes
- Validation rules
- Test plan
Notes:
- Pitfalls avoided
- Decision points applied
```

## Trigger test

- "Please add a --json flag to this CLI command."

## Resources (Optional)

- End-to-end playbook + CLI spec template: `resources/implementation-playbook.md`
- Reference index: `references/README.md`
- Command surface patterns: `references/command-hierarchy-and-flags.md`
- UX help text patterns: `references/ux-help-text.md`
- Language notes:
  - Node: `references/node-frameworks.md`
  - Python: `references/python-frameworks.md`
  - Go: `references/go-frameworks.md`
