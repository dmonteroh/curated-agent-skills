#!/usr/bin/env sh
set -eu

# cdd-context wrapper.
#
# Commands:
#   init     - scaffold docs/context/ core files + index markers (safe defaults)
#   index    - rebuild docs/context/README.md index block deterministically
#   validate - validate required context files and basic headings exist
#   brief    - create/update docs/context/brief.md (context rehydration snapshot)
#
# Env:
#   CONTEXT_DIR=docs/context
#   CONTEXT_INDEX=docs/context/README.md

cmd="${1:-}"
shift || true

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

case "$cmd" in
  init) exec "$script_dir/init.sh" "$@" ;;
  index) exec "$script_dir/update_index.sh" "$@" ;;
  validate) exec "$script_dir/validate.sh" "$@" ;;
  brief) exec "$script_dir/brief.sh" "$@" ;;
  ""|-h|--help|help)
    cat <<'EOF'
cdd-context (context.sh)

Commands:
  init
  index
  validate
  brief

Env:
  CONTEXT_DIR, CONTEXT_INDEX
EOF
    ;;
  *)
    echo "unknown command: $cmd" >&2
    echo "run: $0 --help" >&2
    exit 2
    ;;
esac
