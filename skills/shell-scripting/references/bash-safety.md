# Bash Safety

Practical rules for robust Bash. Assumes `#!/usr/bin/env bash` and Bash 4+.

## Strict mode and its limits

Baseline:

```bash
set -Eeuo pipefail
trap 'printf "error: %s failed at line %d\n" "$BASH_COMMAND" "$LINENO" >&2' ERR
```

- `-e` exit on command failure, `-u` error on unset variables, `-o pipefail` fail a pipeline if any stage fails, `-E` make the `ERR` trap fire inside functions and subshells.

`set -e` is NOT active in these positions — do not rely on it there:

- Commands in `if`/`while`/`until` conditions, or left of `&&`/`||`.
- Any command whose result feeds a condition, including function calls: a function called in an `if` runs its entire body with `-e` suspended.
- Command substitution in some contexts: `local out=$(cmd)` always succeeds because `local` is the command; declare first, then assign: `local out; out=$(cmd)`.
- Pipelines without `pipefail`: only the last stage's status counts.

Handle expected failures explicitly instead of fighting `-e`:

```bash
if ! output=$(some_cmd 2>&1); then
  die "some_cmd failed: $output"
fi
count=$(grep -c pattern file || true)   # grep exits 1 on zero matches by design
```

## Quoting

- Quote every expansion: `"$var"`, `"$@"`, `"${arr[@]}"`. Unquoted `$var` word-splits and glob-expands.
- `"$@"` preserves argument boundaries; `$*` and `$@` unquoted do not. Never loop `for x in $list` over data that can contain spaces.
- Use `--` before variable operands so leading-dash values are not read as flags: `rm -- "$file"`, `grep -e "$pattern"`.
- Prefer `[[ ... ]]` over `[ ... ]` in Bash: no word-splitting of unquoted variables, supports `==` globs and `=~` regex.

## Arrays for command construction

Never build command lines by string concatenation; use arrays:

```bash
args=(--output "$dest" --level 3)
[[ -n $verbose ]] && args+=(--verbose)
tool "${args[@]}"
```

Read lines into an array safely: `mapfile -t lines < <(cmd)`.

## Locating the script's own directory

A script that sources a sibling library or reads a bundled config must resolve those paths from its own location, not from whatever directory the caller happened to be in:

```bash
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
script_name=$(basename -- "${BASH_SOURCE[0]}")
. "$script_dir/lib/common.sh"
```

- `${BASH_SOURCE[0]}` is the path of the file currently being executed *or sourced*. `$0` is the invoking shell's name, so a `$0`-based lookup silently resolves to the caller's script the moment this file is sourced rather than executed.
- `--` after `dirname` and `cd` stops a path beginning with `-` from being read as an option.
- `pwd -P` returns the physical path, resolving symlinked directories in the chain, so the answer is stable when the script is reached through a symlinked `bin` directory. It resolves the *directory* only: if the script file itself is a symlink pointing elsewhere, follow it with `readlink` first (`readlink -f` is GNU-only — see `references/posix-portability.md`).
- POSIX sh has no `BASH_SOURCE`. Under `#!/bin/sh` the closest form is `dirname -- "$0"`, which is correct for an executed script but not for a sourced one.

## Temp files and cleanup

```bash
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
```

- One `EXIT` trap covers success, failure, and Ctrl-C (with `set -E`, ERR reporting stays separate).
- To chain cleanups, append: `trap 'first; second' EXIT` — a new `trap` replaces the old one, so compose deliberately.
- Kill background jobs you started: `trap 'kill $(jobs -p) 2>/dev/null' EXIT`.

## Output discipline

- `printf` over `echo`, always for data: `echo` mangles `-n`, `-e`, and backslashes inconsistently across shells. `printf '%s\n' "$data"`.
- Errors and progress to stderr (`>&2`); reserve stdout for the script's actual product so it stays pipeable.
- Standard helper:

```bash
die() { printf 'error: %s\n' "$*" >&2; exit 1; }
```

## Variables and functions

- `local` for every function variable; top-level constants `readonly`.
- `${var:?message}` to assert required env vars at startup.
- Parameter expansion beats `sed`/`awk` subprocesses for simple cases: `${path##*/}` (basename), `${path%/*}` (dirname), `${var/-/_}`, `${var,,}` (lowercase).

## Reading input

```bash
while IFS= read -r line; do
  process "$line"
done < "$file"
```

- `IFS=` preserves leading/trailing whitespace; `-r` stops backslash mangling.
- Iterating filenames: use globs with `shopt -s nullglob` so a non-matching glob yields nothing instead of the literal pattern, or `find ... -print0 | while IFS= read -r -d '' f`.

## Verification

- `shellcheck script.sh` — treat every finding as a bug until justified; suppress individually with `# shellcheck disable=SCnnnn` plus a reason comment, never file-wide.
- `bash -n script.sh` for a fast syntax gate; `bash -x` to trace a failing run.
