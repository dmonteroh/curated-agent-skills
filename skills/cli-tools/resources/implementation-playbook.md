# CLI Developer - Implementation Playbook

Provides a playbook to produce a usable CLI design + implementation plan (and to avoid common CLI footguns).

## Inputs (Ask First)

- Primary users: humans, CI, other programs.
- OS targets: macOS/Linux/Windows.
- Output contract: human-readable vs machine-readable.
- Configuration needs: flags only vs env vars vs config file.
- Stability requirements: are command signatures already public?

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
