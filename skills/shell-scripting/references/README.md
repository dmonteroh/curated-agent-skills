# Shell Scripting References

- `bash-safety.md`: Bash strict mode and its blind spots, quoting rules, arrays for command construction, script self-location via `BASH_SOURCE`, trap-based cleanup, output discipline, shellcheck verification.
- `posix-portability.md`: POSIX sh limits with a Bash-ism → portable-replacement table, test-expression safety, GNU vs BSD utility divergences, and how to smoke-test under dash/BusyBox.

Read `bash-safety.md` when writing Bash; read `posix-portability.md` when the shebang is `#!/bin/sh` or targets include Alpine/BusyBox/dash.
