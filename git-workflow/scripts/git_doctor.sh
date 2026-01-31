#!/usr/bin/env sh
set -eu

# Read-only diagnostics for "what state is this repo in?"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "not a git repo" >&2
  exit 2
fi

echo "== Repo =="
git rev-parse --show-toplevel

echo
echo "== Branch =="
git branch --show-current || true

echo
echo "== Status =="
git status -sb

echo
echo "== Remotes =="
git remote -v

echo
echo "== Upstream / ahead-behind =="
git branch -vv | sed -n '1,15p'

echo
echo "== Recent history =="
git log --oneline --graph --decorate -n 20

