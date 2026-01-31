#!/usr/bin/env sh
set -eu

# Create a new track directory with spec/plan/context stubs and update registries.
#
# Usage:
#   ./tracks-conductor-protocol/scripts/tcd_new_track.sh "Billing overhaul"
#
# Optional env vars:
#   TCD_TRACK_SLUG=billing-overhaul

title="${1:-}"
if [ -z "$title" ]; then
  echo "usage: $0 \"track title\"" >&2
  exit 2
fi

project_dir="${TCD_PROJECT_DIR:-docs/project}"
tracks_dir="${TCD_TRACKS_DIR:-$project_dir/tracks}"
tracks_registry="${TCD_TRACKS_REGISTRY:-$project_dir/tracks.md}"

slugify() {
  printf "%s" "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | tr ' _' '--' \
    | sed -E 's/[^a-z0-9-]+/-/g; s/-+/-/g; s/^-//; s/-$//'
}

slug="${TCD_TRACK_SLUG:-$(slugify "$title")}"
dir="$tracks_dir/$slug"

mkdir -p "$dir"

if [ ! -f "$dir/spec.md" ]; then
  cat >"$dir/spec.md" <<EOF
# $title

## Status

Draft

## Problem / Context

<why now, what problem>

## Goals

- ...

## Non-goals

- ...

## Requirements

Must:
- ...

Should:
- ...

Must not:
- ...

## Acceptance Criteria

- [ ] ...

## Dependencies

- ADRs:
  - ADR-XXXX: ...
- Futures:
  - FUT-XXX: ...

## Links

- Context (CDD):
  - docs/context/product.md
  - docs/context/tech-stack.md
  - docs/context/workflow.md
EOF
fi

if [ ! -f "$dir/plan.md" ]; then
  cat >"$dir/plan.md" <<EOF
# Plan: $title

## Phases

### Phase 1: <name>

- [ ] Task: <link to task brief>
- [ ] Verification: <what proves phase is complete>

### Phase 2: <name>

- [ ] ...

## Checkpoints

- Architecture checkpoint: do we need an ADR?
- Context checkpoint: does CDD context need updating?
EOF
fi

if [ ! -f "$dir/context.md" ]; then
  cat >"$dir/context.md" <<EOF
# Context: $title

## What this track changes

- ...

## Assumptions

- ...

## Key terms / glossary

- ...

## Open questions

- ...

## Links

- Global context:
  - docs/context/product.md
  - docs/context/tech-stack.md
  - docs/context/workflow.md
- ADRs:
  - ADR-XXXX: ...
EOF
fi

# Ensure registries exist then update managed blocks via tcd_update_index.sh.
mkdir -p "$project_dir"
if [ ! -f "$tracks_registry" ]; then
  cat >"$tracks_registry" <<'EOF'
# Tracks

Registry of active tracks.

<!-- TCD:TRACK-REGISTRY:START -->
| Track | Title | Status | Links |
| --- | --- | --- | --- |
<!-- TCD:TRACK-REGISTRY:END -->
EOF
fi

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$script_dir/tcd_update_index.sh" >/dev/null

echo "OK: created track $dir"
