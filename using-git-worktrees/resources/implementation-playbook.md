# Using Git Worktrees - Implementation Playbook

This playbook is command-oriented. Adjust branch names and paths to the repo’s conventions.

## 1) Pick a worktree root

Priority order:

1. Use an existing directory if present (`.worktrees/` or `worktrees/`).
2. If the repo documents a convention (AGENTS.md/README/CLAUDE.md), follow it.
3. Otherwise create `.worktrees/` (project-local).

## 2) Safety gate: verify ignore (project-local)

Before creating a project-local worktree directory:

```sh
git check-ignore -q .worktrees || git check-ignore -q worktrees
```

If the directory is not ignored:

- Stop and ask before editing `.gitignore`.

Why: prevents accidental tracking of worktree directories.

## 3) Create a worktree

Create a new branch worktree:

```sh
branch="feature/my-branch"
path=".worktrees/my-branch"
git worktree add "$path" -b "$branch"
```

Attach an existing branch:

```sh
branch="feature/my-branch"
path=".worktrees/my-branch"
git worktree add "$path" "$branch"
```

## 4) Baseline checks

Inside the worktree:

```sh
cd "$path"
git status --porcelain
```

If you plan to run tests/build:

- Prefer the project’s documented command.
- Do not run dependency installs without approval (may require network).

## 5) Cleanup

When done:

```sh
git worktree remove "$path"
git branch -d "$branch"   # only if appropriate
```

