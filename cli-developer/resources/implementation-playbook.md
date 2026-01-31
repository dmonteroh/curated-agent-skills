# CLI Developer - Implementation Playbook

Use this playbook to produce a usable CLI design + implementation plan (and to avoid common CLI footguns).

## Inputs (Ask First)

- Primary users: humans, CI, other programs.
- OS targets: macOS/Linux/Windows.
- Output contract: human-readable vs machine-readable.
- Configuration needs: flags only vs env vars vs config file.
- Stability requirements: are command signatures already public?

## Deterministic Workflow

1) Define the command surface
- Root command name
- Subcommands and verbs
- Flags and positional args
- Examples (copy-pasteable)

2) Define the output contract
- Default: stdout is the primary output.
- stderr is for logs/errors.
- Decide JSON mode:
  - `--json` or `--format json` for programmatic usage.

3) Define configuration precedence
- Flags > env vars > project config > user config > defaults.

4) Define exit codes
- `0` success
- `2` misuse/invalid args
- `1` general error
- `130` SIGINT (Ctrl+C)

5) Implement
- Parse args
- Validate early
- Execute
- Print output

6) Polish
- `--help`, `--version`
- Consistent error messages
- Completions (optional)
- TTY-aware colors and progress

7) Test
- Golden tests for `--help` and key commands
- Snapshot tests for JSON output
- Cross-platform smoke test

## CLI Spec Template

```md
# CLI Spec: <tool>

## Goals

- 

## Non-goals

- 

## Command Overview

- `<tool> <command> [flags] [args]`

## Commands

### <tool> <command>

Purpose: <what it does>

Args:
- 

Flags:
- 

Examples:
- 

Exit codes:
- 

Output:
- stdout:
- stderr:

## Global Flags

- `--help`
- `--version`
- `--json` (if applicable)

## Configuration

Precedence: flags > env > config > defaults

Config locations (if applicable):
- project: `./<tool>.config.*`
- user: `~/.config/<tool>/config.*`

## Observability

- Structured logs to stderr (optional)
- `--verbose` increases detail

## Compatibility & Breaking Changes

- 

## Verification Plan

- 
```

## Common Footguns (Avoid)

- Printing logs to stdout (breaks piping).
- Colors/progress on non-TTY output.
- Inconsistent flag naming across subcommands.
- Interactive prompts in CI.
- Silent changes to command signatures.
