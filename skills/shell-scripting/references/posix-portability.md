# POSIX Portability

Rules for scripts shebanged `#!/bin/sh`. On Debian/Ubuntu `/bin/sh` is dash, on Alpine it is BusyBox ash — Bash-isms fail there even when Bash exists on the box.

## Not available in POSIX sh

| Bash-ism | Portable replacement |
| --- | --- |
| `[[ ... ]]` | `[ ... ]` with quoted operands; `case` for pattern matching |
| Arrays | `set -- item1 item2` (positional params) or newline-delimited data |
| `${var,,}` `${var^^}` | `tr '[:upper:]' '[:lower:]'` |
| `${var/pat/rep}` | `sed` or `case`-based prefix/suffix trims (`${var#pat}`, `${var%pat}` are POSIX) |
| `<(cmd)` process substitution | temp files or pipes |
| `<<< "string"` herestrings | `printf '%s\n' "$string" \| cmd` or a heredoc |
| `source file` | `. ./file` (note the explicit path) |
| `function name {` | `name() {` |
| `$'\n'` | literal newline in quotes, or `printf` |
| `echo -n` / `echo -e` | `printf '%s' ...` / `printf '%b\n' ...` |
| `$RANDOM`, `$SECONDS` | `awk 'BEGIN{srand();...}'`, `date +%s` arithmetic |
| `local` | Not in POSIX, but supported by dash, ash, and BusyBox — acceptable when those are the declared targets; state the assumption. |
| `set -o pipefail` | Added in POSIX.1-2024; older dash/ash lack it (time-sensitive: recheck target shells). Otherwise check each stage or restructure to avoid pipelines. |

## Test expression safety

- `[ "$a" = "$b" ]` — single `=`, both sides quoted.
- Prefer `[ -n "$var" ]` / `[ -z "$var" ]` over bare `[ "$var" ]`.
- No `-a`/`-o` inside `[ ]` (unreliable); chain instead: `[ cond1 ] && [ cond2 ]`.
- Pattern matching via `case`, which is POSIX and fast:

```sh
case $file in
  *.tar.gz|*.tgz) extract_targz "$file" ;;
  *.zip)          extract_zip "$file" ;;
  *)              die "unsupported archive: $file" ;;
esac
```

## GNU vs BSD/macOS utilities

The shell is only half of portability; flags differ per utility:

- `sed -i` needs a suffix argument on BSD: `sed -i '' -e ...` (macOS) vs `sed -i -e ...` (GNU). Portable: write to a temp file and `mv`.
- `readlink -f`, `realpath`, `date -d`, `grep -P`, `cp --parents`, `mktemp` without a template: GNU-only or divergent. Portable temp file: `mktemp "${TMPDIR:-/tmp}/name.XXXXXX"`.
- `xargs -d` is GNU-only; use `xargs -0` with `find -print0` — but `-print0`/`-0` themselves are widespread extensions (POSIX.1-2024 adds `find -print0`); the fully portable form is `find ... -exec cmd {} +`.
- `awk` and `sed` POSIX subsets are rich enough for most tasks; when a one-liner needs GNU extensions, prefer rewriting in portable `awk`.

## Arithmetic and strings

- Arithmetic: `$(( ... ))` is POSIX (integers only). Increment: `i=$((i + 1))` — `((i++))` is Bash.
- String length: `${#var}` is POSIX. Substrings `${var:0:3}` are NOT; use `${var%...}`/`${var#...}` trims or `cut`.
- Command existence: `command -v tool >/dev/null 2>&1 || die "tool required"` (`which` is not POSIX).

## Verification

- `shellcheck --shell=sh script.sh` flags Bash-isms against the declared shell.
- Smoke-test with an actual minimal shell: `dash script.sh` or `busybox sh script.sh`. Passing under Bash proves nothing about `/bin/sh` targets.
- CI matrix tip: run the script once under `dash` and once under `bash --posix` if dash is unavailable.
