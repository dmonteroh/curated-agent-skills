---
name: shell-scripting
description: "Write safe, portable shell scripts (POSIX sh or Bash) for automation, CI helpers, and command-line glue: shell selection, strict-mode setup with known caveats, quoting and cleanup patterns, and shellcheck-based verification. Use for scripting, tooling, and DevOps glue code."
metadata:
  category: workflow
---
# Shell Scripting

Provides guidance for writing safe, portable shell scripts for automation, CI helpers, and command-line glue, and for reviewing or hardening existing scripts.

## Use this skill when

- Writing or modifying Bash or POSIX shell scripts for automation.
- Building CI/CD helpers, installers, wrappers, or local tooling.
- Debugging shell failures caused by quoting, strict mode, or portability.
- Reviewing an existing script for safety and portability issues.

## Do not use this skill when

- The task needs real data structures, JSON/YAML manipulation, floating-point math, or concurrency. Recommend Python or another language and say why.
- Building interactive TUI apps or rich UIs.
- The job is primarily configuration; use the native config format instead.

## Required inputs

- Target shell: `/bin/sh` (POSIX) or Bash. If unstated, infer from context: CI images, Alpine/BusyBox, and system scripts suggest POSIX; developer tooling on known Bash hosts may use Bash. State the choice.
- Target platforms (Linux, macOS, containers) — drives utility portability (GNU vs BSD).
- Expected inputs, outputs, and exit codes.
- Files or directories the script touches.

## Non-negotiable rules

- Quote every variable expansion (`"$var"`, `"$@"`) unless word-splitting is explicitly intended and commented.
- Fail loudly: strict mode at the top, errors to stderr, non-zero exit on failure.
- Clean up temp files and background processes with `trap`.
- Never parse `ls` output; never build commands via unquoted string concatenation.
- Keep scripts idempotent when practical: re-running must not corrupt state.

## Workflow

### 1) Choose the shell — or decline shell

Decisions:
- If the script needs arrays, associative maps, or `[[`-style tests and Bash is available on all targets: use Bash with `#!/usr/bin/env bash`.
- If it must run on minimal images (Alpine, BusyBox, dash) or as a system hook: write POSIX sh with `#!/bin/sh`.
- If the logic outgrows shell (roughly >150 lines, nested data, error-prone string parsing): recommend switching language instead of writing fragile shell.

Output: stated shell choice, platforms, and constraints.

### 2) Define the interface

Decisions:
- Options needed → `getopts` (portable) with a `usage()` function printed on `-h` and on bad input.
- Only positional arguments → validate count and emit usage on mismatch.

Output: usage block, argument validation, example invocation.

### 3) Apply the safety baseline

- Bash: `set -Eeuo pipefail` plus an `ERR`/`EXIT` trap. POSIX: `set -eu` (add `set -o pipefail` only if every target shell supports it).
- Know the strict-mode caveats before relying on `set -e` — see `references/bash-safety.md` for the cases where `set -e` silently does nothing.
- Temp files via `mktemp` with `trap 'rm -rf "$tmpdir"' EXIT`.
- `printf` instead of `echo` for any data-bearing output.

Minimal Bash skeleton:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

usage() { printf 'usage: %s [-v] <target>\n' "${0##*/}" >&2; }
die()   { printf 'error: %s\n' "$*" >&2; exit 1; }

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

main() {
  [ $# -ge 1 ] || { usage; exit 2; }
  # core logic here
}
main "$@"
```

For POSIX sh, drop `pipefail`/`-E`, use `#!/bin/sh`, and follow `references/posix-portability.md`.

### 4) Implement core logic

- Small functions with single responsibilities; `local` variables in Bash.
- Handle the failure path first: check inputs and preconditions, `die` early with actionable messages.
- Loop over files with globs or `find ... -exec`/`while IFS= read -r`, never `for f in $(ls ...)`.
- Diagnostics and progress to stderr; only machine-consumable output to stdout.

Output: script body with error handling and deterministic behavior.

### 5) Verify

- Run `shellcheck` (with `--shell=sh` for POSIX targets); fix or explicitly justify every finding. If shellcheck is unavailable, state that and fall back to `bash -n` / `sh -n` syntax checks.
- For POSIX claims, smoke-test under `dash` or `busybox sh` when available, not just Bash.
- Exercise at least: the happy path, a missing/invalid argument, and one failure path (missing file, failing command in a pipe).
- If tests are practical, include fixture commands or `bats` cases.

Output: verification commands run and their results.

## Common pitfalls

- Unquoted expansions causing word-splitting and glob surprises.
- Trusting `set -e` inside `if` conditions, `&&`/`||` chains, or command substitutions where it is disabled by design.
- Bash-only constructs (`[[`, arrays, `local`, process substitution) in scripts shebanged `#!/bin/sh`.
- GNU-only flags (`sed -i` without suffix, `readlink -f`, `date -d`) breaking on macOS/BSD.
- Missing `trap` cleanup, leaving temp files or background jobs behind.
- `echo` mangling `-n`, backslashes, or dashes in data; use `printf`.
- `cd` without `|| exit`, continuing in the wrong directory.

## Examples

**Input**: "Write a POSIX shell script that copies `.env.example` to `.env` if missing."

**Expected output**: a `#!/bin/sh` script with `set -eu`, a usage comment, an idempotent existence check (`[ -f .env ] || cp .env.example .env`), plus verification: `sh ./copy-env.sh && test -f .env`, re-run to confirm idempotency, and `shellcheck --shell=sh copy-env.sh`.

**Input**: "Our CI script needs to build, tag, and push an image; make it safe."

**Expected output**: a Bash script with strict mode, `getopts` for tag/registry, early validation of required env vars with clear `die` messages, and a verification list including a dry-run mode.

## Output contract

Report in this order:
- `Summary`: what the script does and the target shell.
- `Assumptions`: inferred paths, OS, or tools.
- `Script`: the full script content or file changes.
- `Usage`: example command-line invocation.
- `Verification`: commands run (shellcheck, syntax check, smoke tests) and their results; no network assumptions.

## References

- Index: `references/README.md`
- Bash strict mode, quoting, arrays, traps: `references/bash-safety.md`
- POSIX sh limits and portable alternatives: `references/posix-portability.md`
