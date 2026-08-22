---
name: shell-scripting
description: "Write safe, portable shell scripts (POSIX sh or Bash) for automation, CI helpers, and command-line glue: shell selection, strict-mode setup with known caveats, quoting and cleanup patterns, and shellcheck-based verification. Use for scripting, tooling, and DevOps glue code."
metadata:
  category: workflow
---
# Shell Scripting

Provides guidance for reviewing or hardening existing shell scripts.

## Use this skill when

- Writing or modifying Bash or POSIX shell scripts for automation.
- Building CI/CD helpers, installers, wrappers, or local tooling.
- Debugging shell failures caused by quoting, strict mode, or portability.
- Reviewing an existing script for safety and portability issues.
- Testing a script that shells out to external commands (network clients, VCS, package managers).

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
- Always guard `cd` with `|| exit` (or a `die` call); an unchecked `cd` that fails leaves the rest of the script running in the wrong directory.
- Diagnostics and progress to stderr; only machine-consumable output to stdout.
- Resolve sibling files (libraries, config, fixtures) against the script's own location, never the caller's working directory. In Bash that means deriving the directory from `${BASH_SOURCE[0]}`, not `$0` — full idiom and the reasons in `references/bash-safety.md`.
- Never rewrite a file in place that another process may be reading. Write the new content to a temp file in the target's own directory, then rename over the target:

```bash
tmp=$(mktemp -- "$(dirname -- "$target")/.tmp.XXXXXX")
trap 'rm -f -- "$tmp"' EXIT
build_content > "$tmp"
chmod 644 -- "$tmp"        # mktemp creates 0600 and the rename carries that mode over; set what the target needs
mv -- "$tmp" "$target"     # rename within one filesystem is atomic
```

The temp file must sit on the same filesystem as the target — that is what makes the replacement a rename rather than a copy. `mktemp` in `/tmp` followed by a `mv` across a filesystem boundary is a copy plus a delete, and can leave a truncated target if the script dies mid-write. Readers then see either the whole old file or the whole new one, never a partial one.

Output: script body with error handling and deterministic behavior.

### 5) Verify

- Run `shellcheck` (with `--shell=sh` for POSIX targets); fix or explicitly justify every finding. If shellcheck is unavailable, state that and fall back to `bash -n` / `sh -n` syntax checks.
- For POSIX claims, smoke-test under `dash` or `busybox sh` when available, not just Bash.
- Exercise at least: the happy path, a missing/invalid argument, and one failure path (missing file, failing command in a pipe).
- If tests are practical, include fixture commands or `bats` cases.

Declare the project's shellcheck settings once in a `.shellcheckrc` at the repository root instead of repeating `--shell=`/`--enable=`/`--exclude=` at every call site. shellcheck discovers the file by walking up the directory tree from the script it is checking, so a local run, a pre-commit hook, and CI all apply the same rule set without any caller having to know the flags:

```
shell=bash                      # dialect to analyze against
enable=require-variable-braces  # opt-in checks; list them with `shellcheck --list-optional`
external-sources=true           # follow `source`d siblings instead of guessing at them
# SC1091: sourced paths only resolve at runtime in this repo
disable=SC1091
```

Project-level `disable=` is for checks that are false positives everywhere in the project — one per line, each with a reason comment. A finding that is only wrong in one place stays a per-line suppression at that line (`references/bash-safety.md`). Confirm the file is actually in effect before trusting it: the same command run with `--norc` should report differently; if the output is identical, shellcheck never read the file.

Output: verification commands run and their results.

## Stubbing external commands in tests

A script that shells out to `curl`, `git`, a cloud CLI, or a package manager cannot be exercised against the real command without a network, credentials, or real side effects. Rather than reworking the script to accept injectable command names, put fakes ahead of the real commands on `PATH`:

1. In test setup, create a temp directory and prepend it to `PATH`.
2. Write one executable file per faked command, named exactly as the real command, printing canned output and exiting with a chosen status.
3. Run the script under test unchanged — its ordinary `PATH` lookup finds the stub first.
4. In teardown, restore the previous `PATH` and remove the directory so stubs cannot leak into later tests.

```bash
setup_stubs() {
  stub_dir=$(mktemp -d)
  saved_path=$PATH
  PATH="$stub_dir:$PATH"
}

teardown_stubs() {           # call from the runner's teardown hook, or from the one EXIT trap
  PATH=$saved_path
  rm -rf -- "$stub_dir"
}

# stub <command> <stdout> [exit-status]
stub() {
  cat > "$stub_dir/$1" <<EOF
#!/bin/sh
printf '%s\n' "\$@" >> "$stub_dir/$1.calls"   # record the arguments for later assertions
printf '%s\n' '$2'
exit ${3:-0}
EOF
  chmod +x "$stub_dir/$1"
}

setup_stubs
stub curl '{"status":"ok"}' 0
stub git 'abc123' 0
./deploy.sh --dry-run
grep -q -- '--fail' "$stub_dir/curl.calls"    # assert how the script called out
```

- The canned output is interpolated into single quotes, so output containing a single quote needs escaping or a file-based fixture instead.
- Only `PATH` lookups are intercepted. A script calling `/usr/bin/curl` by absolute path, or a shell builtin, bypasses the stub entirely — which is a reason for scripts to invoke bare command names.
- Verify the stub is actually being hit rather than assuming it: check that `command -v <cmd>` resolves inside the stub directory, or that the call log is non-empty. A test that passes because the real command happened to succeed is exactly the failure this guards against.

## Examples

**Input**: "Write a POSIX shell script that copies `.env.example` to `.env` if missing."

**Expected output**: a `#!/bin/sh` script with `set -eu`, a usage comment, an idempotent existence check (`[ -f .env ] || cp .env.example .env`), plus verification: `sh ./copy-env.sh && test -f .env`, re-run to confirm idempotency, and `shellcheck --shell=sh copy-env.sh`.

**Input**: "Our CI script needs to build, tag, and push an image; make it safe."

**Expected output**: a Bash script with strict mode, `getopts` for tag/registry, early validation of required env vars with clear `die` messages, and a verification list including a dry-run mode.

## References

- Index: `references/README.md`
- Bash strict mode, quoting, arrays, traps: `references/bash-safety.md`
- POSIX sh limits and portable alternatives: `references/posix-portability.md`
