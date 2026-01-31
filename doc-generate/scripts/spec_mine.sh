#!/usr/bin/env sh
set -eu

# Scaffold a "reverse-spec" doc quickly.
#
# Safe-by-default:
# - writes only under docs/specs/
# - creates files only if missing (does not overwrite)
#
# The intent is to give agents a deterministic starting point for deriving a spec
# from existing code/config/tests (aka "spec mining").

docs_dir="${DOCS_DIR:-docs}"
specs_dir="${SPECS_DIR:-$docs_dir/specs}"
spec_file="${REVERSE_SPEC_FILE:-$specs_dir/reverse-spec.md}"

mkdir -p "$specs_dir"

if [ ! -f "$spec_file" ]; then
  cat >"$spec_file" <<'EOF'
# Reverse Spec (Derived from Code)

Generated: YYYY-MM-DD (UTC)
Source: repo scan + code/config/tests

## Scope

- In scope:
- Out of scope:

## Actors & Primary Flows

- Actor:
  - Flow:

## Functional Requirements (EARS)

### Authentication / Authorization
- OBS-AUTH-001: WHEN <trigger> THEN the system SHALL <response>.
  - Evidence: `path/to/file.ext:123` (or symbol name)

### Core Behaviors
- OBS-CORE-001: The system SHALL <capability>.
  - Evidence: `path/to/file.ext:123`

### Error Handling / Unwanted Behavior
- OBS-ERR-001: IF <unwanted condition> THEN the system SHALL <mitigation>.
  - Evidence: `path/to/file.ext:123`

## Non-Functional Requirements (Discovered / Implied)

- Security:
- Reliability:
- Performance:
- Observability:
- Privacy/Compliance:

## Constraints & Invariants

- Invariant:

## Data & State (External Contracts)

- Entities:
- Identifiers:
- Versioning / concurrency:

## Assumptions

- Assumption (needs confirmation):

## Open Questions / Follow-Ups

- Question:
EOF
  echo "OK: created $spec_file"
else
  echo "OK: exists $spec_file"
fi

echo "Next: run ./doc-generate/scripts/doc.sh index to ensure docs/README.md indexes docs/specs/* (optional)."
