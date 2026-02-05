#!/usr/bin/env sh
set -eu

# Single entrypoint wrapper for doc-generate scripts.
#
# Usage:
#   ./skills/doc-generate/scripts/doc.sh scan
#   ./skills/doc-generate/scripts/doc.sh index
#   ./skills/doc-generate/scripts/doc.sh spec
#
# Optional env vars:
#   DOCS_DIR=docs
#   DOCS_INDEX_FILE=docs/README.md
#   DOCSCAN_OUT_DIR=docs/_docgen

cmd="${1:-}"
shift || true

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

case "$cmd" in
  scan) exec "$script_dir/docscan.sh" "$@" ;;
  index) exec "$script_dir/update_docs_index.sh" "$@" ;;
  spec) exec "$script_dir/spec_mine.sh" "$@" ;;
  ""|-h|--help|help)
    cat <<'EOF'
doc-generate (doc.sh)

Commands:
  scan   - create docs/_docgen/inventory.md with repo signals
  index  - rebuild docs/README.md managed docs index block
  spec   - scaffold docs/specs/reverse-spec.md (reverse-spec baseline)

Env overrides:
  DOCS_DIR, DOCS_INDEX_FILE, DOCSCAN_OUT_DIR, SPECS_DIR, REVERSE_SPEC_FILE
EOF
    ;;
  *)
    echo "unknown command: $cmd" >&2
    echo "run: $0 --help" >&2
    exit 2
    ;;
esac
