---
name: cli-tools
description: "Build fast, user-friendly CLI tools with stable command surfaces, predictable output contracts (stdout vs stderr), and cross-platform behavior. Covers subcommands/flags, config precedence, interactive prompts, progress indicators, and shell completions. Use when designing or implementing CLI tools."
metadata:
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
- The task is designing a GUI/web UX

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

## Workflow

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

## Numeric flag validation

For a flag that must resolve to a bounded integer (`--retries`, `--concurrency`, `--iterations`), resolve it through a pure decision function — no `process.exit`, no I/O — wrapped by a thin CLI-side layer that is the only place allowed to print and exit. The function takes the raw value plus a spec (`{name, default, min, max?}`) and returns either the resolved value or an error; keeping it pure is what makes the cases below unit-testable without spawning a process.

The cases resolve differently on purpose; the asymmetry is the point (reject low, clamp high):

- **Absent** → the declared default. Silent, no warning.
- **Bare flag, no value** → hard error naming the flag and the expected shape. Never fall back to the default: a bare flag is very likely operator error, not "use the default."
- **Non-numeric or non-integer** (`"3.7"`, `"abc"`) → hard error via a strict integer pattern. Never truncate or coerce; silent coercion hides that the operator typed something the tool didn't ask for.
- **Below the declared minimum** → hard error naming the value and the floor.
- **Above the declared maximum** → clamp to the maximum and warn on stderr. Recoverable, unlike below-minimum.
- **Repeated flag** → not this function's job. Document explicitly that the upstream flag parser is last-wins rather than re-implementing resolution here.

Motivating failure: a lenient parse (`parseInt(val)`) turns non-numeric input into `NaN`. Nothing throws — a loop bounded by `i < NaN` evaluates false immediately and runs zero iterations. On a flag that gates paid API calls, the command exits 0 having silently made none of them; the bug is invisible until someone notices no calls happened.

## Common pitfalls

- Non-deterministic output ordering (breaks tests).
- Coercing invalid numeric flag input into a default or a truncated value (`parseInt(x) || default`) instead of hard-erroring — see Numeric flag validation.

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

**Example: numeric flag validation, wrong vs right**

Wrong
```
const count = parseInt(flags.count) || DEFAULT_COUNT;
```
`--count abc` silently becomes `DEFAULT_COUNT` (masking a typo), and there is no upper bound: `--count 999999` runs unbounded.

Right
```
const result = normalizeIntFlag(flags.count, { name: "count", default: DEFAULT_COUNT, min: 1, max: MAX_COUNT });
// absent -> default; bare/non-numeric/below-min -> hard error; above-max -> clamped value + stderr warning
```

## Resources

- End-to-end playbook + CLI spec template: `resources/implementation-playbook.md`
- Reference index: `references/README.md`
- Command surface patterns: `references/command-hierarchy-and-flags.md`
- UX help text patterns: `references/ux-help-text.md`
- Language notes:
  - Node: `references/node-frameworks.md`
  - Python: `references/python-frameworks.md`
  - Go: `references/go-frameworks.md`
