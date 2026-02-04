#!/usr/bin/env sh
set -eu

# Delete local branches that are fully merged into the chosen base branch.
# Safe-by-default: does not delete current branch and only deletes merged branches.

base="${1:-main}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "not a git repo" >&2
  exit 2
fi

current="$(git branch --show-current)"

# Refresh remote tracking.
git fetch --prune >/dev/null 2>&1 || true

echo "Pruning local branches merged into '$base' (keeping current: '$current')"

git branch --merged "$base" \
  | sed 's/^[* ]*//' \
  | while read -r b; do
      [ -z "$b" ] && continue
      [ "$b" = "$current" ] && continue
      [ "$b" = "$base" ] && continue
      echo "  - deleting $b"
      git branch -d "$b" >/dev/null
    done

echo "OK"

