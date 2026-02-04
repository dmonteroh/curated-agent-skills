---
name: shell-scripting
description: Write safe, portable shell scripts (POSIX/Bash) for automation and CI. Use for scripting, tooling, and DevOps glue code.
category: workflow
---

# Shell Scripting

## Use this skill when

- Writing Bash or POSIX shell scripts for automation
- Building CI/CD helpers, installers, or local tooling
- Need portable, reliable command-line glue

## Do not use this skill when

- The task requires another language runtime or SDK
- Building interactive TUI apps or rich UIs
- The job is primarily configuration (use native config instead)

## Trigger phrases

- "write a bash script"
- "shell script for automation"
- "portable /bin/sh script"
- "CI helper script"

## Required inputs

- Target shell (`/bin/sh` POSIX vs. Bash)
- Target platforms (Linux/macOS/containers)
- Expected inputs/outputs and exit codes
- Files or directories the script should touch

## Workflow (Deterministic)

1. Provide scope and portability confirmation.
   - Decision: if the script must run under `/bin/sh`, choose POSIX; otherwise use Bash.
   - Output: a short checklist of constraints (shell, OS, inputs, outputs).
2. Define interface and usage.
   - Decision: if arguments are required, add `getopts` or simple positional parsing.
   - Output: a usage block and example invocation.
3. Apply safety baseline.
   - Decision: use `set -Eeuo pipefail` for Bash; use `set -eu` for POSIX.
   - Output: strict mode, `IFS` handling where needed, and safe quoting patterns.
4. Implement core logic with clear functions/sections.
   - Output: script body with error handling and deterministic behavior.
5. Add verification guidance.
   - Decision: if tests are practical, include simple fixture commands or `bats` examples.
   - Output: a minimal test or verification command list.

## Common pitfalls

- Unquoted variables causing globbing or word-splitting
- Relying on Bash-only features in `/bin/sh`
- Missing cleanup for temporary files
- Using `echo` for data with escapes or `-n` ambiguity

## Examples

**Input**
- "Write a POSIX shell script that copies `.env.example` to `.env` if missing."

**Expected output**
- Provide the script with a usage block and a short verification command:
  - `sh ./copy-env.sh` then `test -f .env`

## Output contract

- Report in the following order:
  - `Summary`: what the script does and target shell.
  - `Assumptions`: any inferred paths, OS, or tools.
  - `Script`: the full script content or file changes.
  - `Usage`: example command line invocation.
  - `Verification`: commands to validate behavior (no network assumptions).

## Trigger test

- "Create a bash script to rotate logs and keep the last 5 files."
- "Need a portable /bin/sh script to normalize line endings."

## References (Optional)

- Index: `references/README.md`
